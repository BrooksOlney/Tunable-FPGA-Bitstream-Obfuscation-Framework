module demo1_s (input [3:0] sk, input reset, input clk, input enable, output [3:0] out);



	wire out[0], out[1], out[2], out[3], g5, g11, g6, g12, g7, g13, g8;
	wire g14, g10, g15, g9;


	reg g1, g2, g3, g4;


	assign out[0] = (((sk[0]) & (g1)));
	assign out[1] = (((sk[3]) & (g2)));
	assign out[2] = (((sk[3]) & (g3)));
	assign out[3] = (((sk[2]) & (g4)));
	assign g11 = (((sk[2]) & (!g5)));
	assign g12 = (((!sk[3]) & (!g6) & (g11) & (!g1)) + ((!sk[3]) & (g6) & (g11) & (!g1)) + ((sk[3]) & (!g6) & (!g11) & (g1)));
	assign g13 = (((!g6) & (!sk[1]) & (!g7) & (g2)) + ((!g6) & (!sk[1]) & (!g7) & (g2)) + ((g6) & (sk[1]) & (g7) & (!g2)));
	assign g14 = (((g6) & (g8) & (!sk[1]) & (!g3)) + ((g6) & (!g8) & (!sk[1]) & (!g3)) + ((!g6) & (!g8) & (sk[1]) & (g3)));
	assign g15 = (((g6) & (!sk[1]) & (g10) & (!g4)) + ((!g6) & (!sk[1]) & (g10) & (!g4)) + ((!g6) & (sk[1]) & (!g10) & (g4)) + ((g6) & (!sk[1]) & (!g10) & (g4)));
	assign g5 = (((g1) & (!sk[3]) & (!reset)) + ((!g1) & (sk[3]) & (reset)));
	assign g6 = (((!sk[1]) & (reset) & (!enable)) + ((sk[1]) & (!reset) & (enable)));
	assign g7 = (((!g1) & (g2) & (!sk[2]) & (!reset)) + ((g1) & (!g2) & (!sk[2]) & (reset)) + ((!g1) & (g2) & (!sk[2]) & (!reset)) + ((g1) & (!g2) & (sk[2]) & (!reset)));
	assign g8 = (((!g3) & (!sk[2]) & (!g1) & (!g2) & (reset)) + ((g3) & (!sk[2]) & (!g1) & (g2) & (!reset)) + ((g3) & (sk[2]) & (!g1) & (!g2) & (!reset)) + ((!g3) & (sk[2]) & (g1) & (g2) & (!reset)) + ((g3) & (!sk[2]) & (!g1) & (g2) & (!reset)));
	assign g9 = (((!sk[0]) & (g1) & (!g3)) + ((sk[0]) & (!g1) & (!g3)) + ((!sk[0]) & (g1) & (!g3)));
	assign g10 = (((!reset) & (!sk[1]) & (!g4) & (!g2) & (g9)) + ((reset) & (!sk[1]) & (!g4) & (g2) & (!g9)) + ((!reset) & (!sk[1]) & (g4) & (!g2) & (g9)) + ((!reset) & (sk[1]) & (g4) & (!g2) & (!g9)) + ((!reset) & (sk[1]) & (!g4) & (g2) & (!g9)));

endmodule