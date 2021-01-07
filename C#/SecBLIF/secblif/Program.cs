using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace SecBLIF
{
    class Program
    {
        static int Main(string[] args)
        {
            DateTime start = DateTime.Now;
            Console.SetWindowSize(Console.WindowWidth, Console.WindowHeight);
            string strUsage = "\n\tUsage:\tSecBLIF.exe -i {ckt_name}.blif -k {key_bits} [optional_args]" +
                "\n\n\tOptional Arguments:\n" +
                "\n\t\tVerilog Output Type: -v {0, 1, 2}" +
                "\n\t\tDebug Output: -d {0, 1}" +
                "\n\t\tBitstream Output: -b {0, 1}" +
                "\n\t\tLevenshtein Distance Computation: -l {0, 1}" +
                "\n\t\tDesired Percentage of Ofuscation: -op 100(a-b,increment)" +
                "\n\t\tTestbench Output: -tb: {0, 1}\n" + 
                "\n\t\tManufacturer: {0 = Altera, 1 = Xilinx}";

            //string directory_orig = "quartus_blif/";
            //string directory_sec = "s_blif/";
            string circuit = "";
            string directory = "";

            int key_bits = 128;
            VerilogOutputType vot = VerilogOutputType.COMBLOG_MIN;

            bool argErr = false, hasCkt = false, keySpec = false, debugEnabled = false, bitstreamOutput = false, levDist = false, embed_watermark = false;
            bool multipleObfus = false;
            int genTestBench = 0;
            int manufacturer = -1;
            decimal obfusPercentage = 0m, obfusStart = 0m, obfusEnd = 0m, obfusInc = 0m;

            if (args.Length == 0 || args.Length % 2 == 1)   // must have more than 0 args, and every flag must have a value
            {
                Console.WriteLine(strUsage);
            }
            else
            {
                for (int i = 0; i < args.Length; i++)
                {
                    if (args[i].Equals("-i"))
                    {
                        if (!args[i + 1].ToLower().EndsWith(".blif"))
                        {
                            argErr = true;
                            Console.WriteLine("Error: Input file \"{0}\" must be a BLIF file (*.blif).", args[i + 1]);
                        }
                        else
                        {
                            string dir_sep = "";
                            if (args[i + 1].Contains(@"\"))
                                dir_sep = @"\";
                            else
                                dir_sep = @"/";

                            string ckt_only = args[i + 1].Substring(args[i + 1].LastIndexOf(dir_sep) + 1);
                            circuit = ckt_only.Substring(0, ckt_only.ToLower().IndexOf(".blif"));
                            directory = args[i + 1].Substring(0, args[i + 1].LastIndexOf(dir_sep) + 1);
                            hasCkt = true;
                        }
                    }
                    else if (args[i].Equals("-k"))
                    {
                        if (!Regex.IsMatch(args[i + 1], @"^[0-9]+$"))
                        {
                            argErr = true;
                            Console.WriteLine("Error: Key Bits must be an integer greater than 0 (you entered {0}).", args[i + 1]);
                        }
                        else
                        {
                            key_bits = Convert.ToInt32(args[i + 1]);
                            keySpec = true;
                        }
                    }
                    else if (args[i].Equals("-v"))
                    {
                        if (!args[i + 1].Equals("0") && !args[i + 1].Equals("1") && !args[i + 1].Equals("2"))
                        {
                            argErr = true;
                            Console.WriteLine("Error: VerilogOutputType - 0 (complete combinational logic), 1 " +
                                "(minimized combinational logic), or 2 (Altera LUT primitives) must be specified (you entered {0}).", args[i + 1]);
                        }
                        else
                        {
                            int iVOT = Convert.ToInt32(args[i + 1]);
                            vot = (VerilogOutputType)iVOT;
                        }
                    }
                    else if (args[i].Equals("-d"))
                    {
                        if (!args[i + 1].Equals("0") && !args[i + 1].Equals("1"))
                        {
                            argErr = true;
                            Console.WriteLine("Error: Debug Output - 0 (disable) or 1 (enable) must be specified (you entered {0}).", args[i + 1]);
                        }
                        else
                        {
                            int iDebugEn = Convert.ToInt32(args[i + 1]);
                            debugEnabled = Convert.ToBoolean(iDebugEn);
                        }
                    }
                    else if (args[i].Equals("-b"))
                    {
                        if (!args[i + 1].Equals("0") && !args[i + 1].Equals("1"))
                        {
                            argErr = true;
                            Console.WriteLine("Error: Bitstream Output - 0 (disable) or 1 (enable) must be specified (you entered {0}).", args[i + 1]);
                        }
                        else
                        {
                            int iBitstreamOutput = Convert.ToInt32(args[i + 1]);
                            bitstreamOutput = Convert.ToBoolean(iBitstreamOutput);
                        }
                    }
                    else if (args[i].Equals("-l"))
                    {
                        if (!args[i + 1].Equals("0") && !args[i + 1].Equals("1"))
                        {
                            argErr = true;
                            Console.WriteLine("Error: Levenshtein Distance Computation - 0 (disable) or 1 (enable) must be specified (you entered {0}).", args[i + 1]);
                        }
                        else
                        {
                            int iLevDist = Convert.ToInt32(args[i + 1]);
                            levDist = Convert.ToBoolean(iLevDist);
                        }
                    }
                    else if (args[i].Equals("-op"))
                    {
                        if (args[i + 1].Contains('-') && args[i + 1].Contains(','))
                        {
                            string[] tmp = args[i + 1].Split(new Char[] { '-', ',' });
                            if (!Decimal.TryParse(tmp[0], out obfusStart) || !Decimal.TryParse(tmp[1], out obfusEnd) ||
                                !Decimal.TryParse(tmp[2], out obfusInc))
                            {
                                argErr = true;
                                Console.WriteLine("Error: Obfuscation Percentage: Must be a number 0-100");
                            }
                            multipleObfus = true;
                        }
                        else if (!Decimal.TryParse(args[i + 1], out obfusPercentage))
                        {

                            argErr = true;
                            Console.WriteLine("Error: Obfuscation Percentage: Must be a number 0-100");
                        }
                        else
                        {
                            obfusPercentage = obfusPercentage / 100;
                        }
                    }
                    else if (args[i].Equals("-tb"))
                    {
                        if (!args[i + 1].Equals("0") && !args[i + 1].Equals("1") && !args[i + 1].Equals("2"))
                        {
                            argErr = true;
                        }
                        else if (!int.TryParse(args[i + 1], out genTestBench))
                        {
                            argErr = true;
                            Console.WriteLine("Error: Test Bench Generation - Must be a number 0-2");
                        }
                    }
                    else if (args[i].Equals("-m"))
                    {
                        if (!args[i + 1].Equals("0") && !args[i + 1].Equals("1"))
                        {
                            argErr = true;
                            Console.WriteLine("Error: Manufacturer - Must be a number 0-2");
                        }
                        else
                        {
                            manufacturer = Convert.ToInt32(args[i + 1]);
                        }
                    }
                    else if (args[i].Equals("-w"))
                    {
                        if (args[i + 1].Equals("1")) embed_watermark = true;
                    }
                }
                if (argErr)
                {
                    Console.WriteLine("Argument error.");
                }
                if (!hasCkt)
                {
                    Console.WriteLine("Missing input file.");
                }
                if (!keySpec)
                {
                    Console.WriteLine("Missing key bits specification.");
                }
                if (argErr || !hasCkt || !keySpec)
                {
                    Console.WriteLine(strUsage);
                    var xx = Console.ReadKey(true);
                    return -1;
                }
            }

            string blif_file = circuit + ".blif";
            string bs_orig = "", bs_secure = "";
            int lev_dist = 0;

            BLIFFILE bf = BLIFReader.Read(directory + blif_file);
            bf.manufacturer = (Manufacturer)manufacturer;
            bf.embed_watermark = embed_watermark;
            bf.obfuscationPercentage = obfusPercentage > 0 ? obfusPercentage : 1;
            bf.keyBits = key_bits;

            string circuit_file_orig = circuit + "_000pObf_s" + ".v";
            string circuit_file_secure = circuit + "_" + ((int)(obfusPercentage * 100)).ToString("000") + "pObf_s" + ".v";
            string bitstream_orig = circuit + "_o.dat";
            string bitstream_sec = circuit + "_" + ((int)(obfusPercentage * 100)).ToString("000") + "pObf_s" + ".dat";
            string testbench = circuit + "_FunctionalMismatch.v";
            
            if (debugEnabled)
            {
                bf.PrintStats();
            }

            if (bitstreamOutput)
            { 
                bs_orig = bf.WriteBitstream(directory + bitstream_orig);
            }


            if (multipleObfus)
            {
                obfusStart /= 100;
                obfusEnd /= 100;
                obfusInc /= 100;

                bf.MakeSecure(directory, obfusStart, obfusInc, obfusEnd, genTestBench, vot, debugEnabled);
                //bs_secure = bf.WriteBitstream(directory + bitstream_sec);
            }
            else
            {
                obfusStart /= 100;
                obfusEnd /= 100;
                obfusInc /= 100;
                bf.WriteVerilog(directory + circuit_file_orig, vot);
                bf.MakeSecure(directory, obfusPercentage, obfusPercentage, obfusPercentage, genTestBench, vot, debugEnabled);// key bits
                bf.WriteVerilog(directory + circuit_file_secure, vot);
                if (debugEnabled)
                {
                    bf.PrintStats();
                }
                if (bitstreamOutput)
                {
                    bs_secure = bf.WriteBitstream(directory + bitstream_sec);
                }
            }

            if (levDist)
            {
                lev_dist = Util.getLevensteinDistance(bs_orig, bs_secure);
            }

            DateTime end = DateTime.Now;

            var diff = end - start;
            StreamWriter sw = new StreamWriter("runtime.txt", true);
            sw.WriteLine(diff.TotalSeconds.ToString());
            sw.Close();
            
            Console.WriteLine("Done. Total time: {0:0.000} s.", diff.TotalSeconds);
            Console.Write("\nPress any key to continue...");
            
            //var x = Console.ReadKey(true);

            return 0;
        }

    }
}
