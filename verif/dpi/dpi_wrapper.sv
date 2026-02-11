package dpi_wrapper_pkg; // <--- TEM DE SER ESTE NOME EXATO
    import "DPI-C" context function void cpp_write(int data);
    import "DPI-C" context function int  cpp_read();
    import "DPI-C" context function int  cpp_get_size();
    import "DPI-C" context function void cpp_clear();
endpackage : dpi_wrapper_pkg