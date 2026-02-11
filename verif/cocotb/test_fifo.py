# verif/cocotb/test_fifo.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random
import ctypes
import os
from cocotb_coverage.coverage import CoverPoint, coverage_db

# ==========================================
# SETUP & COVERAGE DEFINITIONS
# ==========================================
lib_path = os.path.abspath("./fifo_model.so")
golden_model = ctypes.CDLL(lib_path)

@CoverPoint("FIFO.DATA_IN", rel=lambda val, b: b[0] <= val <= b[1], bins=[(0, 63), (64, 127), (128, 191), (192, 255)])
def cover_data_in(data): pass

@CoverPoint("FIFO.FULL_FLAG", xf=lambda full: full, bins=[0, 1])
def cover_full_flag(full): pass

@CoverPoint("FIFO.EMPTY_FLAG", xf=lambda empty: empty, bins=[0, 1])
def cover_empty_flag(empty): pass

# ==========================================
# TEST 1: HALF-DUPLEX (Sequential)
# ==========================================
@cocotb.test()
async def half_duplex_test(dut):
    """TEST 1: Writes until full, then reads until empty (50 transactions)."""
    
    # Start Clocks
    cocotb.start_soon(Clock(dut.w_clk, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.r_clk, 25, unit="ns").start())

    # Reset
    dut.w_rst_n.value = 0
    dut.r_rst_n.value = 0
    dut.w_en.value = 0
    dut.r_en.value = 0
    dut.w_data.value = 0
    golden_model.cpp_clear() 

    await Timer(50, unit="ns")
    dut.w_rst_n.value = 1
    dut.r_rst_n.value = 1
    cover_empty_flag(int(dut.r_empty.value))

    NUM_TRANSACTIONS = 50
    dut._log.info("==================================================")
    dut._log.info(f"🚀 STARTING TEST 1: HALF-DUPLEX ({NUM_TRANSACTIONS} items)")
    dut._log.info("==================================================")
    
    items_written = 0
    for _ in range(NUM_TRANSACTIONS):
        await RisingEdge(dut.w_clk)
        await Timer(1, unit="ns")
        
        full_val = int(dut.w_full.value)
        cover_full_flag(full_val)
        
        if full_val == 1:
            dut._log.warning(f"FIFO is FULL after {items_written} items. Stopping writes.")
            break
            
        random_data = random.randint(0, 255)
        dut.w_en.value = 1
        dut.w_data.value = random_data
        golden_model.cpp_write(random_data)
        cover_data_in(random_data)
        items_written += 1

    await RisingEdge(dut.w_clk)
    dut.w_en.value = 0 
    NUM_TRANSACTIONS = items_written

    for _ in range(5): await RisingEdge(dut.r_clk)

    for i in range(NUM_TRANSACTIONS):
        rtl_data = int(dut.r_data.value)
        expected_data = golden_model.cpp_read()
        cover_empty_flag(int(dut.r_empty.value))
        assert rtl_data == expected_data, f"MISMATCH! RTL: {hex(rtl_data)} | C++: {hex(expected_data)}"
        dut.r_en.value = 1
        await RisingEdge(dut.r_clk)
        await Timer(1, unit="ns") 

    dut.r_en.value = 0
    for _ in range(3): await RisingEdge(dut.r_clk)
    cover_empty_flag(int(dut.r_empty.value))
    assert golden_model.cpp_get_size() == 0, "Error: C++ model not empty!"
    dut._log.info("✅ TEST 1 PASSED!")


# ==========================================
# PARALLEL TASKS FOR TEST 2
# ==========================================
async def driver_task(dut, num_trans):
    written = 0
    while written < num_trans:
        await RisingEdge(dut.w_clk)
        await Timer(1, unit="ns") 
        full_val = int(dut.w_full.value)
        cover_full_flag(full_val)
        
        if full_val == 0:
            random_data = random.randint(0, 255)
            dut.w_en.value = 1
            dut.w_data.value = random_data
            golden_model.cpp_write(random_data)
            cover_data_in(random_data)
            written += 1
        else:
            dut.w_en.value = 0
    await RisingEdge(dut.w_clk)
    dut.w_en.value = 0

async def monitor_task(dut, num_trans):
    read = 0
    while read < num_trans:
        await RisingEdge(dut.r_clk)
        await Timer(1, unit="ns") 
        empty_val = int(dut.r_empty.value)
        cover_empty_flag(empty_val)
        
        if empty_val == 0:
            rtl_data = int(dut.r_data.value)
            expected_data = golden_model.cpp_read()
            assert rtl_data == expected_data, f"MISMATCH! RTL: {hex(rtl_data)} | C++: {hex(expected_data)}"
            dut.r_en.value = 1 
            read += 1
        else:
            dut.r_en.value = 0
    await RisingEdge(dut.r_clk)
    dut.r_en.value = 0

# ==========================================
# TEST 2: FULL-DUPLEX (Concurrent)
# ==========================================
@cocotb.test()
async def full_duplex_test(dut):
    """TEST 2: Concurrent Read/Write testing CDC stress (10,000 transactions)."""
    
    cocotb.start_soon(Clock(dut.w_clk, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.r_clk, 25, unit="ns").start())

    # Reset
    dut.w_rst_n.value = 0
    dut.r_rst_n.value = 0
    dut.w_en.value = 0
    dut.r_en.value = 0
    dut.w_data.value = 0
    golden_model.cpp_clear() 

    await Timer(50, unit="ns")
    dut.w_rst_n.value = 1
    dut.r_rst_n.value = 1
    
    NUM_TRANSACTIONS = 10000
    dut._log.info("==================================================")
    dut._log.info(f"🚀 STARTING TEST 2: FULL-DUPLEX ({NUM_TRANSACTIONS} items)")
    dut._log.info("==================================================")
    
    # Start both threads concurrently
    write_thread = cocotb.start_soon(driver_task(dut, NUM_TRANSACTIONS))
    read_thread = cocotb.start_soon(monitor_task(dut, NUM_TRANSACTIONS))
    
    await write_thread
    await read_thread
    
    assert golden_model.cpp_get_size() == 0, "Error: C++ model not empty!"
    dut._log.info("✅ TEST 2 PASSED!")
    
    # ==========================================
    # FINAL COVERAGE REPORT
    # ==========================================
    coverage_file = os.path.join(os.getcwd(), "coverage.xml")
    coverage_db.export_to_xml(filename=coverage_file)
    
    dut._log.info("===========================================")
    dut._log.info(" 🎯 CUMULATIVE FUNCTIONAL COVERAGE REPORT:")
    dut._log.info("===========================================")
    coverage_db.report_coverage(dut._log.info, bins=True)
    dut._log.info("===========================================")
    dut._log.info("🏆 ALL TESTS PASSED SUCCESSFULLY! 🏆")