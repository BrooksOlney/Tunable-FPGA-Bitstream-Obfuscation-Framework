using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SecBLIF
{
    class Util
    {
        public static int getLevensteinDistance(string s, string t)
        {
            Util.WriteInfo("Computing Levenshtein Distance...", true);
            DateTime start = DateTime.Now;

            // degenerate cases
            if (s.Equals(t)) return 0;
            if (s.Length == 0) return t.Length;
            if (t.Length == 0) return s.Length;

            // create two work vectors of integer distances
            int[] v0 = new int[t.Length + 1];
            int[] v1 = new int[t.Length + 1];

            // initialize v0 (the previous row of distances)
            // this row is A[0][i]: edit distance for an empty s
            // the distance is just the number of characters to delete from t
            for (int i = 0; i < v0.Length; i++)
                v0[i] = i;

            for (int i = 0; i < s.Length; i++)
            {
                // calculate v1 (current row distances) from the previous row v0

                // first element of v1 is A[i+1][0]
                //   edit distance is delete (i+1) chars from s to match empty t
                v1[0] = i + 1;

                // use formula to fill in the rest of the row
                for (int j = 0; j < t.Length; j++)
                {
                    var cost = (s[i] == t[j]) ? 0 : 1;
                    v1[j + 1] = Math.Min(Math.Min(v1[j] + 1, v0[j + 1] + 1), v0[j] + cost);
                }

                // copy v1 (current row) to v0 (previous row) for next iteration
                for (int j = 0; j < v0.Length; j++)
                    v0[j] = v1[j];
            }

            DateTime end = DateTime.Now;

            var diff = end - start;
            Console.WriteLine("Done. ({0:0.000} s)", diff.TotalSeconds);
            Console.WriteLine("\tDistance = {0} = {1:#0.00%}.", (double)v1[t.Length], v1[t.Length] / (double)Math.Max(s.Length, t.Length));
            return v1[t.Length];
        }

        public static string MinimzeWithEspresso(string pladesc)
        {
            string espresso_output = "";
            string espresso_error = "";

            Process espresso = new Process();
            espresso.StartInfo.UseShellExecute = false;
            espresso.StartInfo.RedirectStandardInput = true;
            espresso.StartInfo.RedirectStandardOutput = true;
            espresso.StartInfo.RedirectStandardError = true;
            espresso.StartInfo.FileName = "espresso.exe";

            espresso.StartInfo.Arguments = String.Format("-Dexact");

            espresso.Start();

            espresso.StandardInput.WriteLine(pladesc);

            espresso_output = espresso.StandardOutput.ReadToEnd();
            espresso_error = espresso.StandardError.ReadToEnd();

            espresso.WaitForExit();

            return espresso_output;
        }

        public static void WriteInfo(string s, bool pad)
        {
            if (pad)
                Console.Write(s.PadRight(50, '.'));
            else
                Console.Write(s);
        }


    }
}
