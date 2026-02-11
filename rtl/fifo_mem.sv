module fifo_mem #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 4
)(
    input  logic                  w_clk,
    input  logic                  w_en,
    input  logic [ADDR_WIDTH-1:0] w_addr,
    input  logic [DATA_WIDTH-1:0] w_data,
    
    input  logic [ADDR_WIDTH-1:0] r_addr,
    output logic [DATA_WIDTH-1:0] r_data
);

    // Depth is 2^ADDR_WIDTH
    localparam DEPTH = 1 << ADDR_WIDTH;

    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    // Write Logic
    always_ff @(posedge w_clk) begin
        if (w_en) begin
            mem[w_addr] <= w_data;
        end
    end

    // Read Logic (Asynchronous read is simpler for verification demos, 
    // but synchronous read is common in FPGAs. Let's stick to async read for simplicity)
    assign r_data = mem[r_addr];

endmodule
