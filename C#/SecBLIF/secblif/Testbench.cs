using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

namespace SecBLIF
{
    class Testbench
    {
        List<string> TB_REGS { get; set; }
        List<string> TB_WIRES { get; set; }
        List<string> TB_MAXES { get; set; }
        List<string> TB_INSTANTIATION_TEMPLATES { get; set; }
        List<int>    SecretKeys { get; set; }

        bool Buses { get; set; }
        bool Sequential { get; set; }

        public Testbench()
        {
            TB_REGS = new List<string>();
            TB_WIRES = new List<string>();
            TB_MAXES = new List<string>();
            TB_INSTANTIATION_TEMPLATES = new List<string>();
            SecretKeys = new List<int>();
            Buses = Sequential = false;
        }

        public string GenerateInstantiationTemplate(int moduleIndex, BLIFFILE bf)
        {
            StringBuilder sb = new StringBuilder();

            string goldenModule = bf.CKT_NAME + "_000pObf_s";
            string obfuscatedModule = bf.CKT_NAME + "_" + ((int)(bf.obfuscationPercentage * 100)).ToString("000") + "pObf_s";
            Dictionary<string, int> input_vectors = bf.parseVectors(bf.CKT_INPUTS);
            Dictionary<string, int> output_vectors = bf.parseVectors(bf.CKT_OUTPUTS);
            Dictionary<string, int> testInputVectors = new Dictionary<string, int>();
            Dictionary<string, int> testOutputVectors = new Dictionary<string, int>();

            int inputCount = 0;
            int outputCount = 0;
            bool buses = false;

            foreach (KeyValuePair<string, int> vector in input_vectors)
            {
                if (vector.Value > 1)
                {
                    buses = true;
                    testInputVectors.Add(vector.Key, vector.Value);
                }
                else
                {
                    inputCount++;
                }
            }


            if (inputCount > 0 && !buses) testInputVectors.Add("inputs", inputCount - 1);

            foreach (KeyValuePair<string, int> vector in output_vectors)
            {
                if (vector.Value > 1)
                {
                    testOutputVectors.Add(vector.Key, vector.Value);
                }
                else
                {
                    outputCount++;
                }
            }

            if (outputCount > 0) testOutputVectors.Add("outputs", outputCount - 1);

            sb.AppendFormat("{0} ObfuscatedModule{1} (.sk(sk{2}), ", obfuscatedModule, (bf.obfuscationPercentage * 100).ToString("000"), moduleIndex);

            int inputIndex = 0;
            foreach (KeyValuePair<string, int> vector in input_vectors)
            {
                if (buses)
                {
                    sb.AppendFormat(".{0}({0}), ", vector.Key);
                }
                /*
                if (testInputVectors.Contains(vector))
                {
                    sb.AppendFormat(".{0}({0}), ", vector);
                }
                */
                else
                {
                    sb.AppendFormat(".{0}(inputs[{1}]), ", vector.Key, inputIndex++);
                }
            }

            int outputIndex = 0;
            foreach (KeyValuePair<string, int> vector in output_vectors)
            {
                if (buses)
                {
                    if (vector.Value > 0)
                    {
                        if (vector.Key == output_vectors.Last().Key)
                            sb.AppendFormat(".{0}({0}{1}));", vector.Key, moduleIndex);
                        else
                            sb.AppendFormat(".{0}({0}{1}), ", vector.Key, moduleIndex);
                    }
                }
                else
                {
                    if (vector.Key == output_vectors.Last().Key)
                    {
                        sb.AppendFormat(".{0} (outputs{2}[{1}]));", vector.Key, outputIndex++, moduleIndex);
                    }

                    else
                        sb.AppendFormat(".{0}(outputs{2}[{1}]), ", vector.Key, outputIndex++, moduleIndex);
                }

                /*
                if (testOutputVectors.Contains(vector))
                {
                    if (vector.Key == output_vectors.Last().Key)
                    {
                        sb.AppendFormat(".{0} (outputs{2}[{1}]));", vector.Key, outputIndex++, moduleIndex);
                    }

                    else
                        sb.AppendFormat(".{0}(outputs{2}[{1}]), ", vector.Key, outputIndex++, moduleIndex);
                }
                else
                {
                    if (vector.Key == output_vectors.Last().Key)
                        sb.AppendFormat(".{0} (obfusoutputs{2}[{1}]));", vector.Key, outputIndex++, moduleIndex);
                    else
                        sb.AppendFormat(".{0}(obfusoutputs{2}[{1}]), ", vector.Key, outputIndex++, moduleIndex);
                }
                */
            }

            return sb.ToString();
        }

        internal void GenerateTestBench(string directory, BLIFFILE bf)
        {
            string goldenModule = bf.CKT_NAME + "_000pObf_s";
            //string obfuscatedModule = bf.CKT_NAME + "_" + ((int)(bf.obfuscationPercentage * 100)).ToString("000") + "pObf_s";

            StringBuilder sb = new StringBuilder();
            Dictionary<string, int> input_vectors = bf.parseVectors(bf.CKT_INPUTS);
            Dictionary<string, int> output_vectors = bf.parseVectors(bf.CKT_OUTPUTS);
            Dictionary<string, int> testInputVectors = new Dictionary<string, int>();
            Dictionary<string, int> testOutputVectors = new Dictionary<string, int>();

            int inputCount = 0;
            int outputCount = 0;

            foreach (KeyValuePair<string, int> vector in input_vectors)
            {
                if (vector.Value > 1)
                {
                    testInputVectors.Add(vector.Key, vector.Value);
                }
                else
                {
                    inputCount++;
                }
            }

            if (inputCount > 0) testInputVectors.Add("inputs", inputCount - 1);

            foreach (KeyValuePair<string, int> vector in output_vectors)
            {
                if (vector.Value > 1)
                {
                    testOutputVectors.Add(vector.Key, vector.Value);
                }
                else
                {
                    outputCount++;
                }
            }

            if (outputCount > 0) testOutputVectors.Add("outputs", outputCount - 1);


            StreamWriter tb = new StreamWriter(string.Format("{0}FunctionalMismatch{1}.v", directory, bf.CKT_NAME));

            tb.WriteLine("/* Testbench auto-generated by EDA Tool */");
            tb.WriteLine("module GoldenChip_{0} ();\n", bf.CKT_NAME);

            tb.Write("\n");

            tb.WriteLine("/* INPUTS */");
            foreach (KeyValuePair<string, int> vector in testInputVectors)
            {
                if (vector.Value > 1)
                {
                    tb.WriteLine("reg [{0}:0] {1} = 0;", vector.Value, vector.Key);
                    tb.WriteLine("localparam MAX_COUNT = {0};", (Math.Pow(2, vector.Value + 1).ToString()));
                }
                else
                {
                    tb.WriteLine("reg {0} = 0;", vector.Value);
                    tb.WriteLine("localparam MAX_COUNT = {0};", (Math.Pow(2, vector.Value + 1).ToString()));
                }
            }

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
            {
                tb.WriteLine("reg [{0}:0] sk{1};", SecretKeys[i] - 1, i + 1);
            }


            tb.WriteLine("/* OUTPUTS */");
            foreach (KeyValuePair<string, int> vector in testOutputVectors)
            {
                if (vector.Value > 1)
                {
                    tb.WriteLine("wire [{0}:0] {1};", vector.Value, vector.Key);
                    for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                    {
                        tb.WriteLine("wire [{0}:0] {1}{2};", vector.Value, "obfus" + vector.Key, i + 1);
                    }

                    for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                    {
                        tb.WriteLine("wire [{0}:0] mismatch{1};", vector.Value, i + 1);
                    }

                }
                // else
                //     tb.WriteLine("write {0};", vector.Value);
            }



            tb.WriteLine("/* END NETS */");
            tb.Write("\n");

            // WRITE INSTANTIATION FOR GOLDEN MODULE ------------------------------------------------------------
            tb.Write("{0} GoldenModule (", goldenModule);

            int inputIndex = 0;
            foreach (KeyValuePair<string, int> vector in input_vectors)
            {
                if (testInputVectors.Contains(vector))
                {
                    tb.Write(".{0}({0}), ", vector.Value);
                }
                else
                {
                    tb.Write(".{0}(inputs[{1}]), ", vector.Key, inputIndex++);
                }
            }

            tb.Write("\n");

            int outputIndex = 0;
            foreach (KeyValuePair<string, int> vector in output_vectors)
            {
                if (testOutputVectors.Contains(vector))
                {
                    if (vector.Key == output_vectors.Last().Key)
                        tb.Write(".{0} (outputs[{1}]));", vector.Key, outputIndex++);
                    else
                        tb.Write(".{0}(outputs[{1}]), ", vector.Key, outputIndex++);
                }
                else
                {
                    if (vector.Key == output_vectors.Last().Key)
                        tb.Write(".{0} (outputs[{1}]));", vector.Key, outputIndex++);
                    else
                        tb.Write(".{0}(outputs[{1}]), ", vector.Key, outputIndex++);
                }
            }

            tb.Write("\n");
            tb.Write("\n");
            // END WRITE INSTANTIATION FOR GOLDEN MODULE ------------------------------------------------------------


            // WRITE INSTANTIATION FOR OBFUSCATED MODULE ------------------------------------------------------------
            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
            {
                tb.WriteLine(TB_INSTANTIATION_TEMPLATES[i]);
            }
            tb.Write("\n");
            tb.Write("\n");
            // END WRITE INSTANTIATION FOR OBFUSCATED MODULE ------------------------------------------------------------

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
            {
                tb.WriteLine("assign mismatch{0} = outputs ^ obfusoutputs{0};", i + 1);
            }

            tb.Write("\n");

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("real mismatchPercentage{0} = 0;", i + 1);

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("real keyPercentageCorrect{0} = 0;", i + 1);

            tb.Write("integer ");
            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count - 1; i++)
            {
                tb.Write("f{0}, ", i + 1);
            }
            tb.Write("f{0};\n", TB_INSTANTIATION_TEMPLATES.Count);

            tb.Write("integer ");
            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count - 1; i++)
            {
                tb.Write("rk{0}, ", i + 1);
            }
            tb.Write("rk{0};\n", TB_INSTANTIATION_TEMPLATES.Count);

            tb.WriteLine("integer i, j, k, l;");
            tb.WriteLine("initial begin");

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("\trk{0} = $fopen(\"RNG1.txt\", \"r\");", i + 1);

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("\tf{0} = $fopen(\"functionalMismatch_{1}_{2}.txt\", \"w\");", i + 1, bf.CKT_NAME, ((i + 1) * 5).ToString("000"));
            // tb.WriteLine("\tf = $fopen(\"functionalMismatch{0}.txt\", \"w\");", obfuscatedModule);
            //     for(int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count)
            //tb.WriteLine("$fwrite(f, \"input, sk, mismatch\\n\");");

            tb.WriteLine("end");

            tb.WriteLine("initial begin");
            tb.WriteLine("\tfor(i = 0; i < MAX_COUNT; i = i +1) begin");

            tb.WriteLine("\t\tfor(l = 0; l < 10; l = l + 1) begin");

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("\t\t\t$fscanf(rk{0}, \"%{1}b\", sk{0});", i + 1, SecretKeys[i]);

            tb.WriteLine("\t\t\t#1;");

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
            {
                tb.WriteLine("\t\t\tfor(j = 0; j < {0}; j = j + 1) begin", testOutputVectors.ElementAt(0).Value + 1);
                tb.WriteLine("\t\t\t\tmismatchPercentage{0} = mismatchPercentage{0} + mismatch{0}[j];", i + 1);
                tb.WriteLine("\t\t\tend");
            }
            //tb.WriteLine("\t\t\tfor(j = 0; j < {0}; j = j + 1) begin", testOutputVectors.ElementAt(0).Value + 1);
            //tb.WriteLine("\t\t\t\tmismatchPercentage = mismatchPercentage + mismatch[j];");
            //tb.WriteLine("\t\t\tend");

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
            {
                tb.WriteLine("\t\t\tfor(k = 0; k < {0}; k = k + 1) begin", SecretKeys[i]);
                tb.WriteLine("\t\t\t\tkeyPercentageCorrect{0} = keyPercentageCorrect{0} + sk{0}[k];", i + 1);
                tb.WriteLine("\t\t\tend");
            }
            //tb.WriteLine("\t\t\tfor(k = 0; k < {0}; k = k + 1) begin", keyBits);
            //tb.WriteLine("\t\t\t\tkeyPercentageCorrect = keyPercentageCorrect + sk[k];");
            //tb.WriteLine("\t\t\tend");

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("\t\t\tkeyPercentageCorrect{0} = keyPercentageCorrect{0} / {1};", i + 1, SecretKeys[i]);

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("\t\t\tmismatchPercentage{0} = mismatchPercentage{0} / {1};", i + 1, testOutputVectors.ElementAt(0).Value + 1);

            tb.WriteLine("\t\t\t#1;");
            //tb.WriteLine("\t\t$fwrite(f, \"%b, %f, %f\\n\", inputs, keyPercentageCorrect, mismatchPercentage);");

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("\t\t\t$fwrite(f{0}, \"%f, %f\\n\", keyPercentageCorrect{0}, mismatchPercentage{0});", i + 1);

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("\t\t\tmismatchPercentage{0} = 0;", i + 1);

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("\t\t\tkeyPercentageCorrect{0} = 0;", i + 1);


            tb.WriteLine("\t\tend");
            tb.WriteLine("\t\tinputs = inputs + 1;");
            //tb.WriteLine("\t\t#1;");
            tb.WriteLine("\tend");

            for (int i = 0; i < TB_INSTANTIATION_TEMPLATES.Count; i++)
                tb.WriteLine("\t$fclose(f{0});", i + 1);

            tb.WriteLine("\t$finish;");
            tb.WriteLine("end");

            tb.Write("\n");
            tb.WriteLine("endmodule");
            tb.Close();
        }
    }
}
