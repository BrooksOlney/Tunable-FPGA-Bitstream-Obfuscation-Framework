module demo1_o (input reset, input clk, input enable, output [3:0] out);



	wire out[0], out[1], out[2], out[3], g5, g11, g6, g12, g7, g13, g8;
	wire g14, g10, g15, g9;


	reg g1, g2, g3, g4;


	assign out[0] = (((g1)));
	assign out[1] = (((g2)));
	assign out[2] = (((g3)));
	assign out[3] = (((g4)));
	assign g11 = (((!g5)));
	assign g12 = (((g6) & (g11) & (!g1)) + ((!g6) & (!g11) & (g1)));
	assign g13 = (((g6) & (g7) & (!g2)) + ((!g6) & (!g7) & (g2)));
	assign g14 = (((g6) & (g8) & (!g3)) + ((!g6) & (!g8) & (g3)));
	assign g15 = (((g6) & (g10) & (!g4)) + ((!g6) & (!g10) & (g4)));
	assign g5 = (((g1) & (!reset)) + ((!g1) & (reset)));
	assign g6 = (((reset) & (!enable)) + ((!reset) & (enable)));
	assign g7 = (((!g1) & (g2) & (!reset)) + ((g1) & (!g2) & (!reset)));
	assign g8 = (((g3) & (!g1) & (!g2) & (!reset)) + ((g3) & (!g1) & (!g2) & (!reset)) + ((!g3) & (g1) & (g2) & (!reset)));
	assign g9 = (((!g1) & (!g3)) + ((!g1) & (!g3)));
	assign g10 = (((!reset) & (g4) & (!g2) & (!g9)) + ((!reset) & (g4) & (!g2) & (g9)) + ((!reset) & (!g4) & (g2) & (!g9)));

endmodule