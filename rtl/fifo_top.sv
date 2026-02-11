module fifo_top #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 4
)(
    //Write Domain
    input logic w_clk,
    input logic w_rst_n,
    input logic w_en,
    input logic [DATA_WIDTH-1:0] w_data,
    output logic w_full,

    //Read Domain
    input logic r_clk,
    input logic r_rst_n,
    input logic r_en,
    output logic [DATA_WIDTH-1:0] r_data,
    output logic r_empty
);
    //---------------------------------------------------------
    // 0. Internal Signals and Registers
    //---------------------------------------------------------

    //Pointers are ADDR_WIDTH + 1 to handle wrap-around condition
    logic [ADDR_WIDTH:0] w_ptr_bin, w_ptr_gray, w_ptr_gray_next;
    logic [ADDR_WIDTH:0] r_ptr_bin, r_ptr_gray, r_ptr_gray_next;

    //Synced Pointers
    logic [ADDR_WIDTH:0] w_ptr_gray_synced; //write pointer in read domain
    logic [ADDR_WIDTH:0] r_ptr_gray_synced; //read pointer in write domain

    //Memory Array
    logic [ADDR_WIDTH-1:0] w_addr, r_addr;

    //---------------------------------------------------------
    // 1. Memory Instantiation
    //---------------------------------------------------------
    assign w_addr = w_ptr_bin[ADDR_WIDTH-1:0];
    assign r_addr = r_ptr_bin[ADDR_WIDTH-1:0];

    fifo_mem #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) u_mem (
        .w_clk (w_clk),
        .w_en  (w_en && !w_full), //protect memory from overflow
        .w_addr(w_addr),
        .w_data(w_data),
        .r_addr(r_addr),
        .r_data(r_data)
    );

    //---------------------------------------------------------
    // 2. Synchronizers (Crossing Domains)
    //---------------------------------------------------------
    
    //Sync Read Pointer into Write Domain (to check Full)
    bit_sync #(.WIDTH(ADDR_WIDTH+1)) u_sync_r2w (
        .clk  (w_clk),
        .rst_n(w_rst_n),
        .d_in (r_ptr_gray),
        .d_out(r_ptr_gray_synced)
    );

    //Sync Write Pointer into Read Domain (to check Empty)
    bit_sync #(.WIDTH(ADDR_WIDTH+1)) u_sync_w2r (
        .clk  (r_clk),
        .rst_n(r_rst_n),
        .d_in (w_ptr_gray),
        .d_out(w_ptr_gray_synced)
    );

    //---------------------------------------------------------
    // 3. Write Domain Logic
    //---------------------------------------------------------
    always_ff @(posedge w_clk or negedge w_rst_n) begin
        if (!w_rst_n) begin
            w_ptr_bin  <= '0;
            w_ptr_gray <= '0;
        end else begin
            if (w_en && !w_full) begin
                w_ptr_bin  <= w_ptr_bin + 1;
                w_ptr_gray <= w_ptr_gray_next;
            end
        end
    end

    // Binary to Gray Conversion: (bin >> 1) ^ bin
    assign w_ptr_gray_next = (w_ptr_bin + 1) ^ ((w_ptr_bin + 1) >> 1);

    // FULL Generation:
    // Full happens when pointers match BUT the top two bits are different pattern
    // Pattern: MSB != MSB, 2ndMSB != 2ndMSB, Rest == Rest
    assign w_full = (w_ptr_gray == {~r_ptr_gray_synced[ADDR_WIDTH:ADDR_WIDTH-1], r_ptr_gray_synced[ADDR_WIDTH-2:0]});

    //---------------------------------------------------------
    // 4. Read Domain Logic
    //---------------------------------------------------------
    always_ff @(posedge r_clk or negedge r_rst_n) begin
        if (!r_rst_n) begin
            r_ptr_bin  <= '0;
            r_ptr_gray <= '0;
        end else begin
            if (r_en && !r_empty) begin
                r_ptr_bin  <= r_ptr_bin + 1;
                r_ptr_gray <= r_ptr_gray_next;
            end
        end
    end

    // Binary to Gray Conversion
    assign r_ptr_gray_next = (r_ptr_bin + 1) ^ ((r_ptr_bin + 1) >> 1);

    // EMPTY Generation:
    // Empty happens when Gray code pointers are exactly identical
    assign r_empty = (r_ptr_gray == w_ptr_gray_synced);

endmodule
