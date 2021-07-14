using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Diagnostics;

namespace SecBLIF
{
    [DebuggerDisplay("{getInputString()}")]
    class LUT : ICloneable
    {
        public List<string> LUTinputs { get; set; }

        public List<LUT> similarityList { get; set; }

        public string LUToutput { get; set; }
        public Dictionary<string, string> TruthTable { get; set; }
        public int NumInputs { get; set; }
        public int Weight { get; set; }
        public bool secured { get; set; }
        public int ContentSize { get; set; }
        public int keyBits { get; set; }
        public int keyIndex { get; set; }
        public string keyVal { get; set; }
        public string LUTID { get; set; }
        public bool IsMinimized { get; set; }
        public Dictionary<string, string> MinTruthTable { get; set; }
        public double hammingDistance { get; set; }


        public LUT(string output, string id, params string[] input_list)
        {
            similarityList = new List<LUT>();
            Weight = 0;
            LUToutput = output;
            NumInputs = input_list.Length;
            ContentSize = (int)Math.Pow(2.0, (double)NumInputs);
            TruthTable = new Dictionary<string, string>();
            MinTruthTable = new Dictionary<string, string>();
            LUTinputs = new List<string>();
            IsMinimized = false;
            LUTID = id;
            for (int i = 0; i < NumInputs; i++)
                this.AddInput(input_list[i]);
            secured = false;
            hammingDistance = 0;
        }

        public LUT(LUT prev)
        {
            similarityList = new List<LUT>();
            Weight = prev.Weight;
            LUToutput = prev.LUToutput;
            NumInputs = prev.NumInputs;
            ContentSize = prev.ContentSize;
            TruthTable = new Dictionary<string, string>(prev.TruthTable);
            MinTruthTable = new Dictionary<string, string>();
            LUTinputs = new List<string>(prev.LUTinputs);
            IsMinimized = false;
            LUTID = prev.LUTID;
            secured = false;
            hammingDistance = 0;
        }

        public void ConvertToMinterms()
        {
            Dictionary<string, string> newTT = new Dictionary<string, string>();

            foreach (KeyValuePair<string, string> kvp in this.TruthTable)
            {
                if (kvp.Value == "1")
                {
                    newTT.Add(kvp.Key, kvp.Value);
                    continue;
                }
                else
                {
                    for(int i = 0; i < Math.Pow(2, this.NumInputs); i++)
                    {
                        string tt_line = Convert.ToString(i, 2).PadLeft(this.NumInputs, '0');
                        if (tt_line != kvp.Key && !newTT.ContainsKey(tt_line))
                        {
                            newTT.Add(tt_line, "1");
                        }
                    }
                }
            }
            this.TruthTable = newTT;
        }

        public object Clone()
        {
            return (LUT)this.MemberwiseClone();
        }

        public void Minimize()
        {
            MinTruthTable.Clear();
            string minPLA = Util.MinimzeWithEspresso(GetPLADesc());
            string[] minPLAtt = Regex.Split(minPLA, Environment.NewLine);
            string[] tt_row;
            // start at 3: 0 = ".i [#input]", 1 = ".o [#output]", 2 = ".p [#primes]"
            for (int i = 3; i < minPLAtt.Length; i++)
            {
                if (minPLAtt[i].Equals("") || minPLAtt[i].Contains(".e"))
                    continue;
                tt_row = minPLAtt[i].Split(' '); // [0] = input cover, [1] = output cover
                MinTruthTable.Add(tt_row[0], tt_row[1]);
            }          
            IsMinimized = true;
        }

        public void AddMinterm(string input_pattern, string result)
        {
            TruthTable.Add(input_pattern, result);
            IsMinimized = false;
        }

        public double AddWatermarkSubstring(string key_bit, string hmac_sub, int key_idx, int lut_idx)
        {
            Dictionary<string, string> original_tt = new Dictionary<string, string>(TruthTable);
            Dictionary<string, string> tt_sec = new Dictionary<string, string>();

            // is the truth table implemented in minterms or maxterms?
            string min_maxterm = "1";

            // reverse keybit
            string incorrect_keybit = key_bit == "1" ? "0" : "1";

            foreach (KeyValuePair<string, string> tt_line in original_tt)
            {
                if (tt_line.Value == "0") min_maxterm = "0";
            }

            while (TruthTable.Count > 0)
            {
                string tt_entry = TruthTable.Keys.ElementAt<string>(0);
                string tt_value = TruthTable[tt_entry];
                TruthTable.Remove(tt_entry);

                tt_entry = tt_entry.Insert(lut_idx, key_bit);
                tt_sec.Add(tt_entry, tt_value);
            }

            // insert the HMAC, baby!
            for (int i = 0; i < hmac_sub.Length; i++)
            {
                string tt_line = Convert.ToString(i, 2).PadLeft(NumInputs, '0');

                tt_line = tt_line.Insert(lut_idx, incorrect_keybit);

                // maintain a min/maxterm representation
                if(hmac_sub[i].ToString() == min_maxterm)
                {
                    tt_sec.Add(tt_line, min_maxterm);
                }
            }


            TruthTable = tt_sec;
            LUTinputs.Insert(lut_idx, "sk[" + key_idx + "]");
            this.NumInputs++;
            //return HammingDistance(lut_idx);
            return 0;
        }

        public void AddKeyInput(string key_bit, int key_idx, int lut_idx)
        {
            keyIndex = lut_idx;
            keyVal = key_bit;
            Random rand = new Random();
            Dictionary<string, string> tt_sec = new Dictionary<string, string>();
            IsMinimized = false;
            //string tt_value = "";
            //string original_tt_val = expandTruthTable();
            Dictionary<string, string> original_tt = new Dictionary<string, string>(TruthTable);
            string tmp = "1";
            foreach (KeyValuePair<string, string> kvp in TruthTable)
            {
                if (kvp.Value == "0")
                    tmp = "0";
            }
            while (TruthTable.Count > 0)
            {
                string tt_entry = TruthTable.Keys.ElementAt<string>(0);
                string tt_value = TruthTable[tt_entry];
                TruthTable.Remove(tt_entry);

                tt_entry = tt_entry.Insert(key_idx, key_bit);
                tt_sec.Add(tt_entry, tt_value);

            }

            NumInputs++;
            ContentSize *= 2;



            ////fill in don't care logic
            for (int i = 0; i < NumInputs - 2; i++)
            {
                StringBuilder tt_entry = new StringBuilder("0".PadLeft(NumInputs, '0'));

                string tt_value = tmp;

                if (key_bit.Equals("1"))
                    tt_entry[key_idx] = '0';
                else
                    tt_entry[key_idx] = '1';
                while (!tt_sec.ContainsKey(tt_entry.ToString()))
                {
                    for (int j = 0; j < NumInputs; j++)
                    {
                        if (j == key_idx)
                            continue;
                        if (rand.Next(100) < 20) tt_entry[j] = '1'; // we should use a template (of n input function) instead of random gen. this is just for test.
                        else tt_entry[j] = '-';
                    }
                    if (tt_entry.ToString().Contains('1'))
                    {
                        try
                        {
                            tt_sec.Add(tt_entry.ToString(), tt_value);
                        }
                        catch { }
                    }
                }
            }



            LUTinputs.Insert(key_idx, "sk[" + lut_idx + "]");
            TruthTable = tt_sec;
            string new_tt = expandTruthTable();

            secured = true;
            var newer_tt = expandTruthTable();
            keyBits++;
            //hammingDistance = HammingDistance(key_idx);
        }

        private string matchTT(string pattern)
        {
            string ret = "0";

            foreach (KeyValuePair<string, string> tt_entry in TruthTable)
            {
                bool isMatch = true;

                for (int i = 0; i < tt_entry.Key.Length; i++)
                {
                    if (tt_entry.Key[i] == '-') continue;
                    if (tt_entry.Key[i] != pattern[i]) isMatch = false;
                }

                if (isMatch)
                {
                    ret = tt_entry.Value;
                    break;
                }
            }
            return ret;
        }

        public string expandTruthTable()
        {
            StringBuilder sb = new StringBuilder(("0".PadLeft(ContentSize, '0')));
            string[] _truthTable = new string[ContentSize];

            for (int i = 0; i < ContentSize; i++)
                _truthTable[i] = Convert.ToString(i, 2).PadLeft(NumInputs, '0');

            Dictionary<string, string> tt_Final = (IsMinimized ? MinTruthTable : TruthTable);

            foreach (KeyValuePair<string, string> tt_entry in tt_Final)
            {
                for (int i = 0; i < ContentSize; i++)
                {
                    string tt_row = tt_entry.Key;
                    //for (int j = 0; j < NumInputs; j++)
                    //{
                        if (isMatchDontCare(_truthTable[i], tt_row))
                        {
                            sb[i] = '1';
                        }
                    //}
                }
            }
            
            return sb.ToString();
        }

        public string ToPrimitive(Manufacturer manufacturer)
        {
            StringBuilder sv = new StringBuilder();


            string input_string = getInputString();

            if (manufacturer == Manufacturer.ALTERA)
            {
                //string tt = expandTruthTable();
                sv.AppendFormat("\t{0} lut_{1} ({{{2}}}, {3});\n", "lut_sub", LUTID, getInputString(), LUToutput);
                sv.AppendFormat("\tdefparam lut_{0}.LUT_SIZE = {1};\n", LUTID, NumInputs);
                string tt = expandTruthTable();
                var arr = tt.ToCharArray();
                Array.Reverse(arr);
                string tt_reversed = new string(arr);

                sv.AppendFormat("\tdefparam lut_{0}.mask = {1}'{2}{3};\n", LUTID, ContentSize, (tt.Length >= 8 ? "H" : "b"), (tt.Length >= 8 ? BinToHex(tt_reversed) : tt_reversed));
            }
            else if (manufacturer == Manufacturer.XILINX)
            {
               // ReverseTruthTable();
                string tt = expandTruthTable();
                var arr = tt.ToCharArray();
                Array.Reverse(arr);
                string tt_reversed = new string(arr);
                if (NumInputs <= 6)
                {

                    sv.AppendFormat("defparam U{0}.INIT = {1}'{2}{3};\n", LUTID, ContentSize, (tt.Length >= 8 ? "h" : "b"), (tt.Length >= 8 ? BinToHex(tt_reversed) : tt));
                    sv.AppendFormat("\tLUT{0} U{1}(.O({2}), ", NumInputs, LUTID, LUToutput);
                    //for (int i = 0, j = NumInputs - 1; i < NumInputs - 1; i++, j--)
                    //    sv.AppendFormat(".I{0}({1}), ", i, LUTinputs[j]);

                    for (int i = 0; i < NumInputs - 1; i++)
                        sv.AppendFormat(".I{0}({1}), ", i, LUTinputs[i]);
                    sv.AppendFormat(".I{0}({1}));\n", NumInputs - 1, LUTinputs[NumInputs - 1]);
                }
                else
                {
                    sv.AppendFormat(getSOP());
                }
            }

            return sv.ToString();
        }

        public override string ToString()
        {
            StringBuilder sb = new StringBuilder();

            sb.AppendFormat("inputs = {2}", this.getInputString());

            return sb.ToString();
        }

        public void ReverseTruthTable()
        {
            Dictionary<string, string> tt_Final = (IsMinimized ? MinTruthTable : TruthTable);
            Dictionary<string, string> temp = new Dictionary<string, string>();

            foreach (KeyValuePair<string, string> tt_entry in tt_Final)
            {
                //for (int i = 0; i < ContentSize; i++)
                //{

                //}
                var tt_row = tt_entry.Key.ToCharArray();
                Array.Reverse(tt_row);
                var reversed_row = new string(tt_row);
                temp.Add(reversed_row, tt_entry.Value);
            }

            MinTruthTable = temp;
          //  TruthTable = temp;
        }

        public string getSOP()
        {
            StringBuilder sop = new StringBuilder();
            if (IsMinimized)
            {
                sop.AppendFormat("\tassign {0} = (", LUToutput);
                int minTermCount = 0;
                foreach (KeyValuePair<string, string> kvp in MinTruthTable)
                {
                    if (kvp.Value.Equals("0")) continue; // should not happen in espresso output, but just in case
                    sop.Append("(");
                    for (int j = 0; j < NumInputs; j++)
                    {
                        string[] li = LUTinputs[j].Split('~');
                        string sli = "";
                        if (li.Length > 1)
                        {
                            sli = li[0] + "[" + li[1] + "]" + li[2];
                        }
                        else
                        {
                            sli = li[0];
                        }

                        if (kvp.Key[j] == '1')
                        {
                            sop.AppendFormat("({0})", sli);// LUTinputs[j]);
                        }
                        else
                        {
                            sop.AppendFormat("(!{0})", sli);// LUTinputs[j]);
                        }
                        if (j < NumInputs - 1)
                            sop.Append(" & ");
                    }
                    sop.Append(")");
                    minTermCount++;
                    if (minTermCount < MinTruthTable.Count)// && tt.Substring(i + 1).Contains("1"))
                        sop.Append(" + ");
                }
                sop.Append(");");
            }
            else
            {
                string tt = expandTruthTable();
                string tt_row = "";

                sop.AppendFormat("\tassign {0} = (", LUToutput);

                for (int i = 0; i < ContentSize; i++)
                {
                    if (tt[i] == '0') continue;

                    tt_row = Convert.ToString(i, 2).PadLeft(NumInputs, '0');
                    sop.Append("(");
                    for (int j = 0; j < NumInputs; j++)
                    {
                        string[] li = LUTinputs[j].Split('~');
                        string sli = "";
                        if (li.Length > 1)
                        {
                            sli = li[0] + "[" + li[1] + "]" + li[2];
                        }
                        else
                        {
                            sli = li[0];
                        }

                        if (tt_row[j] == '1')
                        {
                            sop.AppendFormat("({0})", sli);// LUTinputs[j]);
                        }
                        else
                        {
                            sop.AppendFormat("(!{0})", sli);// LUTinputs[j]);
                        }
                        if (j < NumInputs - 1)
                            sop.Append(" & ");
                    }
                    sop.Append(")");
                    if (i < ContentSize - 1 && tt.Substring(i + 1).Contains("1"))
                        sop.Append(" + ");
                }
                sop.Append(");");
            }
            
            return sop.ToString();
        }

        // Private helper functions
        private string getInputString()
        {
            StringBuilder input_list = new StringBuilder();
            for (int i = 0; i < LUTinputs.Count; i++)
            {
                string[] li = LUTinputs[i].Split('~');
                string sli = "";
                if (li.Length > 1)
                {
                    sli = li[0] + "[" + li[1] + "]" + li[2];
                }
                else
                {
                    sli = li[0];
                }
                input_list.Append(sli);// LUTinputs[i]);
                if (i != LUTinputs.Count - 1)
                    input_list.Append(", ");
            }
            return input_list.ToString();
        }

        public string BinToHex(string bin)
        {
            if (bin == null)
                throw new ArgumentNullException("bin");
            if (bin.Length % 8 != 0)
                throw new ArgumentException("The length must be a multiple of 8", "bin");

            var hex = Enumerable.Range(0, bin.Length / 8)
                             .Select(i => bin.Substring(8 * i, 8))
                             .Select(s => Convert.ToByte(s, 2))
                             .Select(b => b.ToString("x2"));
            return String.Join(null, hex);
        }
        private bool isMatchDontCare(string tt_gold, string test_row)
        {
            bool isMatch = true;

            for (int i = 0; i < tt_gold.Length; i++)
            {
                if (test_row[i] == '-')
                    continue;
                if (tt_gold[i] != test_row[i])
                    return false;
            }

            return isMatch;
        }
        private void AddInput(string input)
        {
            LUTinputs.Add(input);
            IsMinimized = false;
        }
        private string GetPLADesc()
        {
            StringBuilder sb = new StringBuilder();

            sb.AppendFormat(".i {0}\n", NumInputs);
            sb.AppendFormat(".o {0}\n", "1");
            string tt = expandTruthTable();
            for (int i = 0; i < ContentSize; i++)
            {
                sb.AppendFormat("{0} {1}\n", Convert.ToString(i, 2).PadLeft(NumInputs, '0'), tt[i]);
            }
            sb.Append(".e");

            //Console.WriteLine();
            //Console.Write(sb.ToString());

            return sb.ToString();
        }

        public double Similarity(LUT compare)
        {
            return this.LUTinputs.Intersect(compare.LUTinputs).Count() / (double)((this.NumInputs + compare.NumInputs)/2);
        }

        public static List<List<LUT>> PartitionLUTs(List<LUT> LUTs, double avgSimilarity)
        {
            List<List<LUT>> ret = new List<List<LUT>>();
            ret.Add(new List<LUT>());
            var lute = LUTs.GetEnumerator();
            if (lute.MoveNext())
            {
                ret[0].Add(lute.Current);
                while (lute.MoveNext())
                {
                    var curLUT = lute.Current;
                    var max = ret.Select((lf, i) => (AvgSimilarity: lf.Average(f =>
                        f.Similarity(curLUT)), i)).MaxBy(si => si.AvgSimilarity);
                    // count is changed for experimentation with grouping
                    if (max.AvgSimilarity < avgSimilarity || ret[max.ToTuple().Item2].Count == 30)
                        ret.Add(new List<LUT> { curLUT });
                    else
                        ret[max.ToTuple().Item2].Add(curLUT);
                }
            }
            return ret;
        }
    }

    public static class ExtensionMethods
    {
        public static T MaxBy<T, TKey>(this IEnumerable<T> src, Func<T, TKey> key, Comparer<TKey> keyComparer) => 
            src.Aggregate((a, b) => keyComparer.Compare(key(a), key(b)) > 0 ? a : b);

        public static T MaxBy<T, TKey>(this IEnumerable<T> src, Func<T, TKey> key) => 
            src.Aggregate((a, b) => Comparer<TKey>.Default.Compare(key(a), key(b)) > 0 ? a : b);
    }
}