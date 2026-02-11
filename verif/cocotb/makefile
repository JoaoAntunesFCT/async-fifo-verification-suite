# verif/cocotb/Makefile

# Choose the simulator
SIM ?= verilator
TOPLEVEL_LANG ?= verilog

# Path to the RTL directory
PWD=$(shell pwd)
RTL_DIR=$(PWD)/../../rtl

# Add our 3 RTL source files
VERILOG_SOURCES += $(RTL_DIR)/bit_sync.sv
VERILOG_SOURCES += $(RTL_DIR)/fifo_mem.sv
VERILOG_SOURCES += $(RTL_DIR)/fifo_top.sv

# Ignore Verilator warnings during simulation and enable Waveform tracing
EXTRA_ARGS += -Wno-fatal --trace

# The name of the top-level Hardware module
TOPLEVEL = fifo_top

# The name of our Python test file (without the .py extension)
MODULE = test_fifo

# Include standard Cocotb rules
include $(shell cocotb-config --makefiles)/Makefile.sim
