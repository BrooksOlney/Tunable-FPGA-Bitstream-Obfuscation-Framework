module s298 (
	G0, G1, G2, G117, G132, G66, G118, G133, 
	G67);

input G0, G1, G2;

output G117, G132, G66, G118, G133, G67;

wire G29, G30, G34, G39, G44, G56, G86, G92, G98, G102, G107, G113, G119, G125, G130, G28, G38, G40, G45, G46, G50, G51, G54, G55, G59, G60, G64, II155, II158, G76, G82, G87, G91, G93, G96, G99, G103, G112, G108, G114, II210, II213, G124, G120, G121, II221, G131, G126, G127, II229, II232, II235, II238, G26, G27, G31, G32, G33, G35, G36, G37, G41, G42, G47, G48, G52, G49, G61, G57, G65, G58, G62, G63, G74, G75, G88, G89, G90, G94, G95, G100, G104, G105, G109, G110, G111, G115, G122, G123, G128, G129, G24, G25, G68, G69, G70, G71, G72, G73, G77, G78, G79, G80, G81, G83, G84, G85, G43, G97, G101, G106, G116, G53;

reg G10, G11, G12, G13, G14, G15, G16, G17, G18, G19, G20, G21, G22, G23;

initial
begin
	G10 = 0;
	G11 = 0;
	G12 = 0;
	G13 = 0;
	G14 = 0;
	G15 = 0;
	G16 = 0;
	G17 = 0;
	G18 = 0;
	G19 = 0;
	G20 = 0;
	G21 = 0;
	G22 = 0;
	G23 = 0;
end

always @(G29)
	G10<=G29;

 always @(G30)
	G11<=G30;

 always @(G34)
	G12<=G34;

 always @(G39)
	G13<=G39;

 always @(G44)
	G14<=G44;

 always @(G56)
	G15<=G56;

 always @(G86)
	G16<=G86;

 always @(G92)
	G17<=G92;

 always @(G98)
	G18<=G98;

 always @(G102)
	G19<=G102;

 always @(G107)
	G20<=G107;

 always @(G113)
	G21<=G113;

 always @(G119)
	G22<=G119;

 always @(G125)
	G23<=G125;

 assign G117 = ( (~ II210) ) ;
 assign G132 = ( (~ II235) ) ;
 assign G66 = ( (~ II155) ) ;
 assign G118 = ( (~ II213) ) ;
 assign G133 = ( (~ II238) ) ;
 assign G67 = ( (~ II158) ) ;
 assign G29 = ( (~ G10)  &  (~ G130) ) ;
 assign G30 = ( (~ G31)  &  (~ G32)  &  (~ G33)  &  (~ G130) ) ;
 assign G34 = ( (~ G35)  &  (~ G36)  &  (~ G37)  &  (~ G130) ) ;
 assign G39 = ( (~ G42)  &  (~ G43) ) ;
 assign G44 = ( (~ G48)  &  (~ G49)  &  (~ G53) ) ;
 assign G56 = ( (~ G57)  &  (~ G58)  &  (~ G130) ) ;
 assign G86 = ( (~ G88)  &  (~ G89)  &  (~ G90)  &  (~ G112) ) ;
 assign G92 = ( (~ G94)  &  (~ G95)  &  (~ G97) ) ;
 assign G98 = ( (~ G100)  &  (~ G101) ) ;
 assign G102 = ( (~ G105)  &  (~ G106) ) ;
 assign G107 = ( (~ G110)  &  (~ G111) ) ;
 assign G113 = ( (~ G115)  &  (~ G116) ) ;
 assign G119 = ( (~ G122)  &  (~ G123)  &  (~ G130) ) ;
 assign G125 = ( (~ G128)  &  (~ G129)  &  (~ G130) ) ;
 assign G130 = ( (~ II229) ) ;
 assign G28 = ( (~ G130) ) ;
 assign G38 = ( (~ G10) ) ;
 assign G40 = ( (~ G13) ) ;
 assign G45 = ( (~ G12) ) ;
 assign G46 = ( (~ G11) ) ;
 assign G50 = ( (~ G14) ) ;
 assign G51 = ( (~ G23) ) ;
 assign G54 = ( (~ G11) ) ;
 assign G55 = ( (~ G13) ) ;
 assign G59 = ( (~ G12) ) ;
 assign G60 = ( (~ G22) ) ;
 assign G64 = ( (~ G15) ) ;
 assign II155 = ( (~ G16) ) ;
 assign II158 = ( (~ G17) ) ;
 assign G76 = ( (~ G10) ) ;
 assign G82 = ( (~ G11) ) ;
 assign G87 = ( (~ G16) ) ;
 assign G91 = ( (~ G12) ) ;
 assign G93 = ( (~ G17) ) ;
 assign G96 = ( (~ G14) ) ;
 assign G99 = ( (~ G18) ) ;
 assign G103 = ( (~ G13) ) ;
 assign G112 = ( (~ G62)  &  (~ G63) ) ;
 assign G108 = ( (~ G112) ) ;
 assign G114 = ( (~ G21) ) ;
 assign II210 = ( (~ G18) ) ;
 assign II213 = ( (~ G19) ) ;
 assign G124 = ( (~ II221) ) ;
 assign G120 = ( (~ G124) ) ;
 assign G121 = ( (~ G22) ) ;
 assign II221 = ( (~ G2) ) ;
 assign G131 = ( (~ II232) ) ;
 assign G126 = ( (~ G131) ) ;
 assign G127 = ( (~ G23) ) ;
 assign II229 = ( (~ G0) ) ;
 assign II232 = ( (~ G1) ) ;
 assign II235 = ( (~ G20) ) ;
 assign II238 = ( (~ G21) ) ;
 assign G26 = ( G28  &  G50 ) ;
 assign G27 = ( G51  &  G28 ) ;
 assign G31 = ( G10  &  G45  &  G13 ) ;
 assign G32 = ( G10  &  G11 ) ;
 assign G33 = ( G38  &  G46 ) ;
 assign G35 = ( G10  &  G11  &  G12 ) ;
 assign G36 = ( G38  &  G45 ) ;
 assign G37 = ( G46  &  G45 ) ;
 assign G41 = ( (~ G12) ) | ( (~ G11) ) | ( (~ G10) ) ;
 assign G42 = ( G40  &  G41 ) ;
 assign G47 = ( (~ G50)  &  (~ G40) ) ;
 assign G48 = ( G45  &  G46  &  G10  &  G47 ) ;
 assign G52 = ( (~ G13) ) | ( (~ G45) ) | ( (~ G46) ) | ( (~ G10) ) ;
 assign G49 = ( G50  &  G51  &  G52 ) ;
 assign G61 = ( (~ G14)  &  (~ G55) ) ;
 assign G57 = ( G59  &  G11  &  G60  &  G61 ) ;
 assign G65 = ( (~ G59) ) | ( (~ G54) ) | ( (~ G22) ) | ( (~ G61) ) ;
 assign G58 = ( G64  &  G65 ) ;
 assign G62 = ( G59  &  G11  &  G60  &  G61 ) ;
 assign G63 = ( G64  &  G65 ) ;
 assign G74 = ( G12  &  G14  &  G19 ) ;
 assign G75 = ( G82  &  G91  &  G14 ) ;
 assign G88 = ( G14  &  G87 ) ;
 assign G89 = ( G103  &  G96 ) ;
 assign G90 = ( G91  &  G103 ) ;
 assign G94 = ( G93  &  G13 ) ;
 assign G95 = ( G96  &  G13 ) ;
 assign G100 = ( G99  &  G14  &  G12 ) ;
 assign G104 = ( (~ G74)  &  (~ G75) ) ;
 assign G105 = ( G103  &  G108  &  G104 ) ;
 assign G109 = ( (~ G71) ) | ( (~ G72) ) | ( (~ G73) ) | ( (~ G14) ) ;
 assign G110 = ( G108  &  G109 ) ;
 assign G111 = ( G10  &  G112 ) ;
 assign G115 = ( G114  &  G14 ) ;
 assign G122 = ( G120  &  G121 ) ;
 assign G123 = ( G124  &  G22 ) ;
 assign G128 = ( G126  &  G127 ) ;
 assign G129 = ( G131  &  G23 ) ;
 assign G24 = ( G38 ) | ( G46 ) | ( G45 ) | ( G40 ) ;
 assign G25 = ( G38 ) | ( G11 ) | ( G12 ) ;
 assign G68 = ( G11 ) | ( G12 ) | ( G13 ) | ( G96 ) ;
 assign G69 = ( G103 ) | ( G18 ) ;
 assign G70 = ( G103 ) | ( G14 ) ;
 assign G71 = ( G82 ) | ( G12 ) | ( G13 ) ;
 assign G72 = ( G91 ) | ( G20 ) ;
 assign G73 = ( G103 ) | ( G20 ) ;
 assign G77 = ( G112 ) | ( G103 ) | ( G96 ) | ( G19 ) ;
 assign G78 = ( G108 ) | ( G76 ) ;
 assign G79 = ( G103 ) | ( G14 ) ;
 assign G80 = ( G11 ) | ( G14 ) ;
 assign G81 = ( G12 ) | ( G13 ) ;
 assign G83 = ( G11 ) | ( G12 ) | ( G13 ) | ( G96 ) ;
 assign G84 = ( G82 ) | ( G91 ) | ( G14 ) ;
 assign G85 = ( G91 ) | ( G96 ) | ( G17 ) ;
 assign G43 = ( (~ G24) ) | ( (~ G25) ) | ( (~ G28) ) ;
 assign G97 = ( (~ G83) ) | ( (~ G84) ) | ( (~ G85) ) | ( (~ G108) ) ;
 assign G101 = ( (~ G68) ) | ( (~ G69) ) | ( (~ G70) ) | ( (~ G108) ) ;
 assign G106 = ( (~ G77) ) | ( (~ G78) ) ;
 assign G116 = ( (~ G79) ) | ( (~ G80) ) | ( (~ G81) ) | ( (~ G108) ) ;
 assign G53 = ( (~ G26)  &  (~ G27) ) ;


endmodule

