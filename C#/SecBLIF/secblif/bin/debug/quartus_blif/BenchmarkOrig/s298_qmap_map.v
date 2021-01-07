module s298_qmap_map (sk, blif_clk_net, blif_reset_net, G0, G2, G1, G117, G132, G66, G118, G133, G67);

	input blif_clk_net;
	input blif_reset_net;
	input G0;
	input G2;
	input G1;
	output G117;
	output G132;
	output G66;
	output G118;
	output G133;
	output G67;



	wire g1, g2, g3, g4, g5, g6, g13, g42, g17, g43, g18, g44, g19, g45, g22, g46, g23, g47, g26, g48, g27;
	wire g49, g7, g8, g9, g10, g11, g28, g50, g12, g15, g14, g30, g16, g20, g21, g29, g51, g25, g24, g32, g33;
	wire g31, g34, g37, g35, g36, g40, g38, g39, g41;

	lut_sub lut_7 ({g1}, G117);
	defparam lut_7.LUT_SIZE = 1;
	defparam lut_7.mask = 2'b01;

	lut_sub lut_11 ({g2}, G132);
	defparam lut_11.LUT_SIZE = 1;
	defparam lut_11.mask = 2'b01;

	lut_sub lut_15 ({g3}, G66);
	defparam lut_15.LUT_SIZE = 1;
	defparam lut_15.mask = 2'b01;

	lut_sub lut_19 ({g4}, G118);
	defparam lut_19.LUT_SIZE = 1;
	defparam lut_19.mask = 2'b01;

	lut_sub lut_23 ({g5}, G133);
	defparam lut_23.LUT_SIZE = 1;
	defparam lut_23.mask = 2'b01;

	lut_sub lut_27 ({g6}, G67);
	defparam lut_27.LUT_SIZE = 1;
	defparam lut_27.mask = 2'b01;

	lut_sub lut_30 ({g13}, g42);
	defparam lut_30.LUT_SIZE = 1;
	defparam lut_30.mask = 2'b10;

	lut_sub lut_39 ({g17}, g43);
	defparam lut_39.LUT_SIZE = 1;
	defparam lut_39.mask = 2'b10;

	lut_sub lut_48 ({g18}, g44);
	defparam lut_48.LUT_SIZE = 1;
	defparam lut_48.mask = 2'b10;

	lut_sub lut_54 ({g19}, g45);
	defparam lut_54.LUT_SIZE = 1;
	defparam lut_54.mask = 2'b10;

	lut_sub lut_66 ({g22}, g46);
	defparam lut_66.LUT_SIZE = 1;
	defparam lut_66.mask = 2'b10;

	lut_sub lut_72 ({g23}, g47);
	defparam lut_72.LUT_SIZE = 1;
	defparam lut_72.mask = 2'b10;

	lut_sub lut_78 ({g26}, g48);
	defparam lut_78.LUT_SIZE = 1;
	defparam lut_78.mask = 2'b10;

	lut_sub lut_84 ({g27}, g49);
	defparam lut_84.LUT_SIZE = 1;
	defparam lut_84.mask = 2'b10;

	lut_sub lut_97 ({g7, g8, g9, g10, g11, g1}, g13);
	defparam lut_97.LUT_SIZE = 6;
	defparam lut_97.mask = 64'h3eff2eff0eff2eff;

	lut_sub lut_147 ({g28}, g50);
	defparam lut_147.LUT_SIZE = 1;
	defparam lut_147.mask = 2'b10;

	lut_sub lut_160 ({g10, g11, g7, g8, g9, g12}, g15);
	defparam lut_160.LUT_SIZE = 6;
	defparam lut_160.mask = 64'h3333333373133333;

	lut_sub lut_201 ({g11, g9, g14, g8, g2, g30}, g16);
	defparam lut_201.LUT_SIZE = 6;
	defparam lut_201.mask = 64'ha000af00a3a3ff00;

	lut_sub lut_233 ({g3, g10, g11, g8, g15}, g17);
	defparam lut_233.LUT_SIZE = 5;
	defparam lut_233.mask = 32'hff5ffd55;

	lut_sub lut_267 ({g5, g10, g11, g7, g8, g9}, g18);
	defparam lut_267.LUT_SIZE = 6;
	defparam lut_267.mask = 64'hfdfffffffdddff55;

	lut_sub lut_332 ({g6, g10, g11, g7, g8, g9}, g19);
	defparam lut_332.LUT_SIZE = 6;
	defparam lut_332.mask = 64'h57f7ffff57d5ff55;

	lut_sub lut_389 ({g10, g7, g8, g14, G0}, g20);
	defparam lut_389.LUT_SIZE = 5;
	defparam lut_389.mask = 32'h22880288;

	lut_sub lut_402 ({g7, g8, g14, G0}, g21);
	defparam lut_402.LUT_SIZE = 4;
	defparam lut_402.mask = 16'h0a28;

	lut_sub lut_410 ({g15, G0}, g22);
	defparam lut_410.LUT_SIZE = 2;
	defparam lut_410.mask = 4'b1101;

	lut_sub lut_420 ({g10, g7, g8, g14, G0}, g23);
	defparam lut_420.LUT_SIZE = 5;
	defparam lut_420.mask = 32'hfffd7557;

	lut_sub lut_447 ({g29}, g51);
	defparam lut_447.LUT_SIZE = 1;
	defparam lut_447.mask = 2'b10;

	lut_sub lut_458 ({g10, g7, g8, g14}, g25);
	defparam lut_458.LUT_SIZE = 4;
	defparam lut_458.mask = 16'h0040;

	lut_sub lut_465 ({g11, G0, g24, g25}, g26);
	defparam lut_465.LUT_SIZE = 4;
	defparam lut_465.mask = 16'h8f7f;

	lut_sub lut_481 ({g12, G0, G2}, g27);
	defparam lut_481.LUT_SIZE = 3;
	defparam lut_481.mask = 8'hb7;

	lut_sub lut_491 ({g14, G0}, g28);
	defparam lut_491.LUT_SIZE = 2;
	defparam lut_491.mask = 4'b0111;

	lut_sub lut_498 ({G0, g24, G1}, g29);
	defparam lut_498.LUT_SIZE = 3;
	defparam lut_498.mask = 8'h9f;

	lut_sub lut_513 ({g11, g9, g10, g7, g12, g2}, g30);
	defparam lut_513.LUT_SIZE = 6;
	defparam lut_513.mask = 64'hffcf000c0faa0000;

	lut_sub lut_542 ({g32, g33}, g31);
	defparam lut_542.LUT_SIZE = 2;
	defparam lut_542.mask = 4'b1000;

	lut_sub lut_548 ({g10, g34}, g32);
	defparam lut_548.LUT_SIZE = 2;
	defparam lut_548.mask = 4'b0100;

	lut_sub lut_554 ({g10, g37}, g33);
	defparam lut_554.LUT_SIZE = 2;
	defparam lut_554.mask = 4'b0001;

	lut_sub lut_560 ({g35, g36}, g34);
	defparam lut_560.LUT_SIZE = 2;
	defparam lut_560.mask = 4'b1000;

	lut_sub lut_566 ({g15, g40}, g35);
	defparam lut_566.LUT_SIZE = 2;
	defparam lut_566.mask = 4'b0100;

	lut_sub lut_572 ({g14, g15}, g36);
	defparam lut_572.LUT_SIZE = 2;
	defparam lut_572.mask = 4'b0100;

	lut_sub lut_578 ({g38, g39}, g37);
	defparam lut_578.LUT_SIZE = 2;
	defparam lut_578.mask = 4'b1000;

	lut_sub lut_584 ({g15, g41}, g38);
	defparam lut_584.LUT_SIZE = 2;
	defparam lut_584.mask = 4'b0100;

	lut_sub lut_590 ({g14, g15}, g39);
	defparam lut_590.LUT_SIZE = 2;
	defparam lut_590.mask = 4'b0100;

	lut_sub lut_598 ({g8, g7, g4, g11}, g40);
	defparam lut_598.LUT_SIZE = 4;
	defparam lut_598.mask = 16'h5011;

	lut_sub lut_607 ({g4, g11}, g41);
	defparam lut_607.LUT_SIZE = 2;
	defparam lut_607.mask = 4'b1011;


endmodule