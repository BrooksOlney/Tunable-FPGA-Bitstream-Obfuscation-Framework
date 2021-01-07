using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace SecBLIF
{ 
    class Latch
    { 
        public string input { get; set; }
        public string output { get; set; }
        public string latchType { get; set; }
        public string control { get; set; }
        public string init_val { get; set; }

        public Latch(string latchDefinition)
        {
            Match regexMatches = Regex.Match(latchDefinition, @"(?<keyword>\.latch)\s+(?<input>\S+)\s+(?<output>\S+)\s+" + 
                                                              @"((?<type>fe|re|ah|al|as)*\s+)*(?<control>\S+)\s(?<initvalue>0|1)?");

            input = regexMatches.Groups["input"].Value;
            output = regexMatches.Groups["output"].Value;
            latchType = regexMatches.Groups["type"].Value;
            control = regexMatches.Groups["control"].Value;
            init_val = regexMatches.Groups["initvalue"].Value != "" ? "\t" +
                output + " = " + regexMatches.Groups["initvalue"].Value + ";\n"
                : string.Empty;

            if (input.Contains("~"))
            {
                string[] buf = input.Split('~');
                input = buf[0];
                input += '[';
                input += buf[1];
                input += ']';
            }

            if (output.Contains("~"))
            {
                string[] buf = output.Split('~');
                output = buf[0];
                output += '[';
                output += buf[1];
                output += ']';
            }
        }

        public override string ToString()
        {
            StringBuilder latchSB = new StringBuilder();

            switch (latchType)
            {
                case "re":
                    latchSB.AppendFormat("always @(posedge {0}) begin {1} <= {2}; end", control, output, input);
                    break;
                case "fe":
                    latchSB.AppendFormat("always @(negedge {0}) begin {1} <= {2}; end", control, output, input);
                    break;
                case "ah":
                    latchSB.AppendFormat("always @({0}) begin if({0}) {1} <= {2}; end", control, output, input);
                    break;
                case "al":
                    latchSB.AppendFormat("always @({0}) begin if(!{0}) {1} <= {2}; end", control, output, input);
                    break;
                case "as":
                    latchSB.AppendFormat("always @({0}) begin {1} <= {0}; end", input, output);
                    break;
                case "":
                    latchSB.AppendFormat("always @({0}) begin {1} <= {0}; end", input, output);
                    break;
                default:
                    throw new Exception("Invalid latch type found .BLIF file.");
            }

            return latchSB.ToString();
        }
    }
}
