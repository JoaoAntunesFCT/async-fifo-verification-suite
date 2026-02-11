// verif/dpi/dpi_wrapper.sv
package dpi_wrapper_pkg;

    // Import C++ functions into SystemVerilog
    // "context" allows C++ to access SV scopes if needed (advanced usage)
    import "DPI-C" context function void cpp_write(int data);
    import "DPI-C" context function int  cpp_read();
    import "DPI-C" context function int  cpp_get_size();
    import "DPI-C" context function void cpp_clear();

endpackage : dpi_wrapper_pkg