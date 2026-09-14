module hft_pipeline (
    input wire clk,
    input wire rst,
    input wire [63:0] rx_data,
    output reg [63:0] tx_data
);
always @(posedge clk or posedge rst) begin
    if (rst)
        tx_data <= 64'd0;
    else
        tx_data <= rx_data + 64'd1;
end
endmodule
