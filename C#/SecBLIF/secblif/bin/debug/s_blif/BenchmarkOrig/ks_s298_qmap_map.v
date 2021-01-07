module ks_s298_qmap_map (sk, blif_clk_net, blif_reset_net, g0, g2, g1, g117, g132, g66, g118, g133, g67);

	input blif_clk_net;
	input blif_reset_net;
	input g0;
	input g2;
	input g1;
	output g117;
	output g132;
	output g66;
	output g118;
	output g133;
	output g67;

	input [127 : 0] sk /* synthesis noprune */;

reg g10;
reg g11;
reg g12;
reg g13;
reg g14;
reg g15;
reg g16;
reg g17;
reg g18;
reg g19;
reg g20;
reg g21;
reg g22;
reg g23;

	wire g1, g2, g3, g4, g5, g6, g42, g43, g44, g45, g46, g47, g26, g48, g27;
	wire g49, g7, g8, g9, g28, g50, g30, g29, g51, g25, g24, g32, g33;
	wire g31, g34, g37, g35, g36, g40, g38, g39, g41;

	
	always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g10 <= 0;
  else
    g10 <= g29;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g11 <= 0;
  else
    g11 <= g30;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g12 <= 0;
  else
    g12 <= g34;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g13 <= 0;
  else
    g13 <= g39;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g14 <= 0;
  else
    g14 <= g44;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g15 <= 0;
  else
    g15 <= g56;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g16 <= 0;
  else
    g16 <= g86;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g17 <= 0;
  else
    g17 <= g92;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g18 <= 0;
  else
    g18 <= g98;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g19 <= 0;
  else
    g19 <= g102;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g20 <= 0;
  else
    g20 <= g107;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g21 <= 0;
  else
    g21 <= g113;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g22 <= 0;
  else
    g22 <= g119;
always @(posedge blif_clk_net or posedge blif_reset_net)
  if(blif_reset_net == 1)
    g23 <= 0;
  else
    g23 <= g125;
	 
	
	assign g117 = (((sk[0]) & (g1)));
	assign g132 = (((sk[1]) & (g2)));
	assign g66 = (((sk[2]) & (g3)));
	assign g118 = (((sk[3]) & (g4)));
	assign g133 = (((sk[4]) & (g5)));
	assign g67 = (((sk[5]) & (g6)));
	assign g42 = (((sk[6]) & (!g13)));
	assign g43 = (((sk[7]) & (!g17)));
	assign g44 = (((sk[8]) & (!g18)));
	assign g45 = (((sk[9]) & (!g19)));
	assign g46 = (((sk[10]) & (!g22)));
	assign g47 = (((sk[11]) & (!g23)));
	assign g48 = (((sk[12]) & (!g26)));
	assign g49 = (((sk[13]) & (!g27)));
	assign g13 = (((!g7) & (!g8) & (g9) & (!g10) & (!g11) & (!g1)) + ((!g7) & (!g8) & (!g9) & (g10) & (!g11) & (!g1)) + ((!g7) & (!g8) & (!g9) & (g10) & (!g11) & (!g1)) + ((!g7) & (g8) & (!g9) & (!g10) & (g11) & (!g1)) + ((!g7) & (!g8) & (!g9) & (!g10) & (g11) & (!g1)));
	assign g50 = (((sk[15]) & (!g28)));
	assign g15 = (((!g10) & (!g11) & (!g7) & (!g8) & (g9) & (!g12)) + ((!g10) & (g11) & (!g7) & (!g8) & (g9) & (!g12)) + ((!g10) & (!g11) & (!g7) & (!g8) & (g9) & (!g12)) + ((!g10) & (!g11) & (!g7) & (g8) & (g9) & (!g12)) + ((!g10) & (!g11) & (!g7) & (!g8) & (g9) & (g12)) + ((g10) & (!g11) & (!g7) & (!g8) & (!g9) & (g12)));
	assign g16 = (((g11) & (g9) & (!g14) & (!g8) & (!g2) & (!g30)) + ((!g11) & (g9) & (!g14) & (g8) & (!g2) & (!g30)) + ((!g11) & (!g9) & (!g14) & (!g8) & (!g2) & (!g30)) + ((g11) & (!g9) & (!g14) & (g8) & (g2) & (!g30)) + ((g11) & (!g9) & (!g14) & (!g8) & (!g2) & (!g30)));
	assign g17 = (((g3) & (!g10) & (!g11) & (!g8) & (!sk[18]) & (!g15)) + ((!g3) & (!g10) & (!g11) & (!g8) & (sk[18]) & (g15)) + ((!g3) & (!g10) & (g11) & (!g8) & (sk[18]) & (!g15)) + ((!g3) & (!g10) & (!g11) & (!g8) & (sk[18]) & (!g15)) + ((!g3) & (!g10) & (!g11) & (!g8) & (sk[18]) & (!g15)) + ((!g3) & (!g10) & (g11) & (g8) & (!sk[18]) & (!g15)));
	assign g18 = (((!g5) & (!g10) & (!g11) & (!g7) & (!g8) & (g9)) + ((!g5) & (!g10) & (g11) & (!g7) & (!g8) & (!g9)) + ((!g5) & (g10) & (!g11) & (!g7) & (!g8) & (!g9)) + ((!g5) & (!g10) & (!g11) & (!g7) & (!g8) & (!g9)) + ((!g5) & (!g10) & (!g11) & (!g7) & (!g8) & (!g9)));
	assign g19 = (((!g6) & (!g10) & (!g11) & (!g7) & (!g8) & (g9)) + ((!g6) & (g10) & (!g11) & (!g7) & (!g8) & (!g9)) + ((!g6) & (g10) & (!g11) & (!g7) & (!g8) & (!g9)) + ((!g6) & (!g10) & (!g11) & (g7) & (g8) & (!g9)) + ((!g6) & (!g10) & (g11) & (!g7) & (!g8) & (!g9)) + ((!g6) & (!g10) & (g11) & (!g7) & (g8) & (!g9)));
	assign g20 = (((g10) & (!g7) & (!g8) & (!sk[21]) & (!g14) & (!g0)) + ((!g10) & (!g7) & (g8) & (!sk[21]) & (g14) & (!g0)) + ((!g10) & (!g7) & (g8) & (!sk[21]) & (g14) & (!g0)) + ((!g10) & (g7) & (!g8) & (sk[21]) & (!g14) & (!g0)) + ((!g10) & (!g7) & (!g8) & (sk[21]) & (g14) & (!g0)));
	assign g21 = (((g7) & (!g8) & (!g14) & (!sk[22]) & (!g0)) + ((!g7) & (g8) & (g14) & (!sk[22]) & (!g0)) + ((g7) & (!g8) & (g14) & (!sk[22]) & (!g0)) + ((!g7) & (g8) & (!g14) & (sk[22]) & (!g0)) + ((!g7) & (g8) & (!g14) & (sk[22]) & (!g0)));
	assign g22 = (((sk[23]) & (!g15) & (!g0)) + ((!sk[23]) & (g15) & (g0)));
	assign g23 = (((g10) & (!g7) & (!sk[24]) & (!g8) & (!g14) & (!g0)) + ((!g10) & (!g7) & (sk[24]) & (!g8) & (!g14) & (!g0)) + ((!g10) & (!g7) & (!sk[24]) & (g8) & (g14) & (!g0)) + ((!g10) & (!g7) & (sk[24]) & (!g8) & (!g14) & (!g0)) + ((g10) & (g7) & (!sk[24]) & (g8) & (g14) & (!g0)) + ((!g10) & (!g7) & (sk[24]) & (!g8) & (!g14) & (g0)) + ((!g10) & (!g7) & (!sk[24]) & (g8) & (g14) & (!g0)) + ((!g10) & (!g7) & (sk[24]) & (!g8) & (g14) & (!g0)));
	assign g51 = (((sk[25]) & (!g29)));
	assign g25 = (((g10) & (!g7) & (!sk[26]) & (!g8) & (!g14)) + ((!g10) & (g7) & (!sk[26]) & (g8) & (!g14)) + ((g10) & (!g7) & (!sk[26]) & (!g8) & (g14)));
	assign g26 = (((!sk[27]) & (g11) & (!g0) & (!g24) & (!g25)) + ((sk[27]) & (!g11) & (g0) & (!g24) & (!g25)) + ((!sk[27]) & (g11) & (!g0) & (g24) & (!g25)) + ((!sk[27]) & (!g11) & (g0) & (g24) & (!g25)) + ((!sk[27]) & (g11) & (!g0) & (!g24) & (g25)) + ((sk[27]) & (!g11) & (!g0) & (!g24) & (!g25)));
	assign g27 = (((g12) & (g0) & (!sk[28]) & (!g2)) + ((!g12) & (g0) & (sk[28]) & (!g2)) + ((g12) & (!g0) & (!sk[28]) & (g2)) + ((!g12) & (!g0) & (sk[28]) & (!g2)));
	assign g28 = (((g14) & (sk[29]) & (!g0)) + ((g14) & (!sk[29]) & (g0)) + ((!g14) & (sk[29]) & (g0)));
	assign g29 = (((!sk[30]) & (g0) & (g24) & (!g1)) + ((!sk[30]) & (g0) & (!g24) & (g1)) + ((sk[30]) & (!g0) & (g24) & (g1)) + ((sk[30]) & (!g0) & (!g24) & (!g1)));
	assign g30 = (((!g11) & (!g9) & (!g10) & (!g7) & (!g12) & (!g2)) + ((!g11) & (!g9) & (!g10) & (g7) & (!g12) & (!g2)) + ((!g11) & (!g9) & (!g10) & (g7) & (!g12) & (!g2)) + ((!g11) & (!g9) & (!g10) & (!g7) & (!g12) & (!g2)) + ((!g11) & (!g9) & (g10) & (g7) & (!g12) & (!g2)) + ((g11) & (!g9) & (g10) & (!g7) & (!g12) & (!g2)));
	assign g31 = (((g32) & (!sk[32]) & (g33)) + ((!g32) & (sk[32]) & (!g33)));
	assign g32 = (((!sk[33]) & (g10) & (g34)) + ((sk[33]) & (!g10) & (g34)));
	assign g33 = (((!sk[34]) & (g10) & (g37)));
	assign g34 = (((!sk[35]) & (g35) & (g36)) + ((sk[35]) & (!g35) & (!g36)));
	assign g35 = (((!g15) & (sk[36]) & (g40)) + ((g15) & (!sk[36]) & (g40)));
	assign g36 = (((!g14) & (sk[37]) & (g15)) + ((g14) & (!sk[37]) & (g15)));
	assign g37 = (((!sk[38]) & (g38) & (g39)) + ((sk[38]) & (!g38) & (!g39)));
	assign g38 = (((!g15) & (sk[39]) & (g41)) + ((g15) & (!sk[39]) & (g41)));
	assign g39 = (((!sk[40]) & (g14) & (g15)) + ((sk[40]) & (!g14) & (g15)));
	assign g40 = (((g8) & (!sk[41]) & (!g7) & (!g4) & (!g11)) + ((!g8) & (!sk[41]) & (g7) & (g4) & (!g11)) + ((g8) & (!sk[41]) & (!g7) & (g4) & (g11)) + ((!g8) & (sk[41]) & (!g7) & (!g4) & (g11)));
	assign g41 = (((g4) & (!sk[42]) & (g11)) + ((!g4) & (sk[42]) & (!g11)));

endmodule