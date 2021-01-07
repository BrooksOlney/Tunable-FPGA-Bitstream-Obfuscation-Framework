using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace SecBLIF
{
    class BLIFReader
    {
        public static BLIFFILE Read(string filename)
        {
            Util.WriteInfo(String.Format("Processing BLIF file ({0})...", filename), true);
            DateTime start = DateTime.Now;

            BLIFFILE bf = new BLIFFILE(/*8*/ 6);
            TextReader r = new StreamReader(filename);

            string ckt = r.ReadToEnd();
            ckt = ckt.Replace("\\\n ", ""); // BLIF provides multiline extension using \ character - we can just have everything on one line.
            ckt = ckt.Replace("\\\r\n ", "");
            string[] ckt_lines = Regex.Split(ckt, Environment.NewLine);
            if (ckt_lines.Length == 1) // wasn't generated on windows
                ckt_lines = Regex.Split(ckt, "\n");

            int lut_count = 0;

            int line_num = 0;
            for (int i = 0; i < ckt_lines.Length; i++)
            {
                string s = ckt_lines[i];

                if (string.IsNullOrWhiteSpace(s)) continue;

                if (s.ToLower().Contains("model"))
                {
                    string[] slist = s.Split(' ');
                    // bf.CKT_NAME = slist[1];
                    int tmp1 = filename.LastIndexOf("/") + 1;
                    int tmp2 = filename.LastIndexOf(".");
                    bf.CKT_NAME = filename.Substring(tmp1, tmp2 - tmp1);
                }
                else if (s.ToLower().Contains("inputs"))
                {
                    string[] port_list = s.Split(' ');
                    List<string> input_list = new ArraySegment<string>(port_list, 1, port_list.Length - 1).ToList<string>();
                    for (int k = 0; k < input_list.Count; k++)
                        input_list[k] = input_list[k].Replace('[', '~').Replace(']', '~');
                    bf.CKT_INPUTS = input_list;
                }
                else if (s.ToLower().Contains("outputs"))
                {
                    string[] port_list = s.Split(' ');
                    List<string> output_list = new ArraySegment<string>(port_list, 1, port_list.Length - 1).ToList<string>();
                    for (int k = 0; k < output_list.Count; k++)
                        output_list[k] = output_list[k].Replace('[', '~').Replace(']', '~');

                    bf.CKT_OUTPUTS = output_list;
                }
                else if (s.ToLower().Contains("names"))
                {
                    string[] port_list = s.Split(' ');
                    int numInputs = port_list.Length - 2; // -1 (.names), -1 (output)
                    string output = port_list[port_list.Length - 1];//.Replace('[', '~').Replace(']', '~');
                    string[] input_list = new ArraySegment<string>(port_list, 1, numInputs).ToArray<string>();

                    for (int k = 0; k < input_list.Length; k++)
                    {
                        if(input_list[k].IndexOf('[') == 0)
                            input_list[k] = input_list[k].Replace('[', '~').Replace(']', '~');
                    }

                    LUT lut0 = new LUT(output, lut_count++.ToString(), input_list);
                    bool hasMoreTT = true;
                    int j = 1;
                    while (hasMoreTT)
                    {
                        s = ckt_lines[i + j];
                        string[] tt_entry = s.Split();
                        if (tt_entry.Length == 2) // truth table row
                        {
                            lut0.AddMinterm(tt_entry[0], tt_entry[1]);
                            j++;
                        }
                        else
                        {
                            hasMoreTT = false;
                        }
                    }

                    foreach (string wire in lut0.LUTinputs)
                    {
                        if (!bf.CKT_WIRES.Contains(wire) && !wire.Contains('['))
                            bf.CKT_WIRES.Add(wire);
                    }
                    if (!bf.CKT_WIRES.Contains(lut0.LUToutput) && !bf.CKT_OUTPUTS.Contains(output.Replace('[', '~').Replace(']', '~'))) bf.CKT_WIRES.Add(lut0.LUToutput);

                    bf.AddLUT(lut0);
                  //  bf.lutCount++;
                }
                else if (s.ToLower().Contains("latch"))
                {
                    s = s.Replace('[', '~').Replace(']', '~');
                    string[] port_list = s.Split(' ');
                    //bf.CKT_LATCHES.Add(String.Format("\talways @ (posedge {0}) begin {1} <= {2}; end\n", port_list[4], port_list[2], port_list[1]));
                    bf.CKT_LATCHES.Add(new Latch(s));
                    bf.CKT_REGS.Add(port_list[2]);
                    for (int ii = 0; ii < bf.CKT_OUTPUTS.Count; ii++)
                    {
                        if (bf.CKT_OUTPUTS[ii].Equals(port_list[2]))
                        {
                            //bf.CKT_OUTPUTS[ii] = bf.CKT_OUTPUTS[ii].Insert(0, "reg ");
                            break;
                        }
                    }
                }
                else
                {
                    if (string.IsNullOrWhiteSpace(s) || s.StartsWith("#") || s.Contains(".end") || s.Split(' ').Length == 2) continue;
                    Console.WriteLine("Unsupported BLIF type @ Line {0}: {1}", line_num, s);
                }
                line_num++;
            }

            foreach (string s in bf.CKT_REGS)
            {
                if (bf.CKT_WIRES.Contains(s))
                    bf.CKT_WIRES.Remove(s);
            }

            DateTime end = DateTime.Now;
            var diff = end - start;
            Util.WriteInfo(String.Format("Done. ({0:0.000} s)\n", diff.TotalSeconds), false);
            return bf;
        }
    }
}
