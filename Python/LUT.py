import time
import random as rnd

class LUT:
    def __init__(self, ID, inputs, output):
        """ Lookup-table (LUT) class constructor

        Arguments:
            ID {int32} -- Unique Identifier for each LUT in circuit
            inputs {list(str)} -- List of input signals into LUT
            output {str} -- Name of output signal from the LUT
        """
        self.ID = ID
        self.inputs = list(inputs)
        self.output = output
        self.tt = {}
        self.mintt = {}
        self.weight = 0
        self.isMinimized = False
        self.numInputs = len(inputs)
        self.contentSize = 2**self.numInputs
        self.secured = False

    def __str__(self):
        return "inputs = {0}".format(self.getInputString())
    
    def addMinterm(self, tt_line, output):
        """ Add minterm expression to existing truth table (tt)

        Arguments:
            tt_line {str} -- Binary string representing input minterm
            output  {str} -- Binary 1/0 corresponding to min/max-term expression
        """
        if output == "0":
            for i in range(self.contentSize):
                ttLine = bin(i)[2:].zfill(self.numInputs)
                if ttLine != tt_line and ttLine not in self.tt.keys():
                    self.tt[ttLine] = "1"
        else:
            self.tt[tt_line] = output
        
        self.isMinimised = False

    def addWatermarkSubstring(self, keybit, keyIdx, lutIdx, hmacSub):
        """ 
            Obfuscates LUT with provided HMAC substring. Implements methods proposed in the paper: 

                B. Olney and R. Karam, "WATERMARCH: IP Protection Through Authenticated Obfuscation in FPGA Bitstreams,"
                in IEEE Embedded Systems Letters, doi: 10.1109/LES.2020.3015092. (IEEE ESL 2020)

        Arguments:
            keybit  {str} -- Binary value of keybit (1/0)
            keyIdx  {str} -- Index of the keybit in the entire secret key (sk[1]) -> 1
            lutIdx  {str} -- Index of the LUT inputs to insert the keybit
            hmacSub {str} -- HMAC substring to insert into LUT truth table
        """
        orig_tt = dict(self.tt) 
        tt_sec = {}

        minMaxterm = "1"
        incorrectKeybit = "0" if keybit == "1" else "1"

        for ttEntry, ttVal in orig_tt:
            if ttVal == "0":
                minMaxterm = "0" 

        while orig_tt:
            ttEntry, ttVal = list(orig_tt.items())[0]
            orig_tt.pop(ttEntry)

            ttEntry = ttEntry[:lutIdx] + keybit + ttEntry[lutIdx:]
            tt_sec[ttEntry] = ttVal

        for i in range(len(hmacSub)):
            q = ''.join(["{:", str(self.numInputs), "b}"])
            ttLine = str(q).format(i)

            ttLine = ''.join([ttLine[:lutIdx], incorrectKeybit, ttLine[lutIdx:]])

            if hmacSub[i] == minMaxterm:
                tt_sec[ttLine] = minMaxterm

        self.tt = tt_sec
        self.inputs.insert(lutIdx, ''.join(["sk~", keyIdx, "~"]))
        self.numInputs += 1
        self.contentSize *= 2

    def addKeybit(self, keybit, keyIdx, lutIdx):
        """ Add keybit to input list, insert obfuscation function

        Arguments:
            keybit {str} -- Binary value of keybit (1/0)
            keyIdx {str} -- Index of the keybit in the entire secret key (sk[1]) -> 1
            lutIdx {str} -- Index of the LUT inputs to insert the keybit
        """
        # determine what the reverse (incorrect) keybit is
        revKeybit = "1" if keybit == "0" else "0"

        # BLIF files sometimes mix min-/max-term function implementations
        # We must make sure to stick to one in our implementation for proper integration
        # into tools like ABC and the SAT Attack 
        minMax = "0"
        for ttLine, output in self.tt.items():
            if output == "1":
                minMax = "1"

        # build secured truth table with the correct keybit to preserve functionality
        ttSec = {}
        while self.tt:
            ttLine, ttOutput = self.tt.popitem()
            ttLine = ''.join([ttLine[:lutIdx], keybit, ttLine[lutIdx:]])
            ttSec[ttLine] = ttOutput

        # add additional input (sk[keyidx])
        self.numInputs += 1
        self.contentSize *= 2

        # obfuscate the functionality by inserting random functions when keybit is incorrect
        for i in range(self.numInputs - 2):
            ttEntry = list("0" * self.numInputs)

            while ''.join(ttEntry) not in ttSec:

                for j in range(self.numInputs):
                    if j == lutIdx:
                        continue
                    
                    # random don't care generation
                    if rnd.randint(0, 100) < 20:
                        ttEntry[j] = "1"
                    else:
                        ttEntry[j] = "-"

                if "1" in ttEntry:
                    ttEntry[lutIdx] = revKeybit
                    ttSec[''.join(ttEntry)] = minMax
        
        self.inputs.insert(lutIdx, ''.join(["sk~", str(keyIdx), "~"]))
        self.tt = ttSec
        self.secured = True

    def expandTruthTable(self):
        """ Expands truth table of minterms into full binary string of size 2**contentSize

        Returns:
            [str] -- binary string of output for every possible input combination
        """

        expandedTT = list("0" * self.contentSize)
        tt = list()

        for i in range(self.contentSize):
            tt.append(bin(i)[2:].zfill(self.numInputs))

        ttFinal = self.mintt if self.isMinimised else self.tt

        for ttLine, output in ttFinal.items():
            for i in range(self.contentSize):
                ttRow = ttLine

                if isMatchDontCare(tt[i], ttRow):
                    expandedTT[i] = "1"
        
        return ''.join(expandedTT)

    def getInputString(self):
        """ Generate input string for other functions

        Returns:
            [str] -- comma separated string of all inputs to the LUT in proper order
        """
        return ', '.join([*map(decodeNet, self.inputs)])

    def getSOP(self):
        """ Generate sum-of-products (SOP) expression of LUT functionality

        Returns:
            [str] -- SOP expression describing functionality in Verilog format
        """
        sop = list()
        sop.append("\tassign {0} = (".format(self.output))

        if self.isMinimised:
            mintermCount = 0

            for ttEntry, output in self.mintt.items():
                
                if output == "0": continue
                
                sop.append(self.genSOPline(self.inputs, ttEntry))
                mintermCount += 1

                if mintermCount < len(self.mintt):
                    sop.append(" + ")

                sop.append(");")

        else:
            tt = self.expandTruthTable()

            for i in range(self.contentSize):

                if tt[i] == "0": 
                    continue

                q = ''.join(["{:", str(self.numInputs), "b}"])
                ttRow = str(q).format(i)
                sop.append(self.genSOPline(ttRow))
                
                if i < self.contentSize - 1 and "1" in tt[i + 1:]:
                    sop.append(" + ")
            
            sop.append(");")

        return ''.join(sop)

    def genSOPline(self, ttLine):
        """ Take the list of primary LUT inputs and the tt line, and generate a LUT function statement.

            i.e. => inputs = ('a', 'b', 'c'), ttline = "010" => returns "((!a) & (b) & (!c))" 

        Args:
            inputs {[list(string)]}: list of LUT inputs
            ttLine {[str]}: binary string corresponding to input signal values

        Returns:
            string: SOP line for given tt value
        """
        sop = []
        sop.append("(")

        for i, lutInput in enumerate(self.inputs):
            sli = decodeNet(lutInput)
            
            if ttLine[i] == "1":
                sop.append("({})".format(sli))
            else:
                sop.append("(!{})".format(sli))

            if i < self.numInputs - 1:
                sop.append(" & ")

        sop.append(")")

        return ''.join(sop)

    def toPrimitive(self, manufacturer):
        """ Generate LUT primitive output string for verilog - corresponding to manufacturer and the way
            they instantiate primitives. Altera (Intel) for example requires us to reverse the truth table
            of the LUT prior to outputting. 

            Currently, I am unsure whether or not the Xilinx primitives work. When we published the paper, we
            only included results gathered from targeting Altera boards. May need to revisit this in the future.

        Args:
            manufacturer ([string]): string telling which manufacturer specs to use

        Returns:
            [str] -- LUT primitive instantiation string for outputting to verilog file
        """
        sv = []
        inputString = self.getInputString()
        tt = self.expandTruthTable()
        reversedTT = tt[::-1]

        if manufacturer.upper() == "ALTERA" or manufacturer.upper() == "INTEL":
            sv.append("\t{} lut_{} ({{{}}}, {});\n".format("lut_sub", self.ID, inputString, self.output))
            sv.append("\tdefparam lut_{}.LUT_SIZE = {};\n".format(self.ID, self.numInputs))
        
            precision = "H" if len(reversedTT) >= 8 else "b"
            content = BinToHex(reversedTT) if len(reversedTT) >= 8 else reversedTT
            
            sv.append("\tdefparam lut_{}.mask = {}'{}{};\n".format(self.ID, self.contentSize, precision, content))

        elif manufacturer.upper() == "XILINX" or manufacturer.upper() == "AMD":
            
            if self.numInputs <= 6:
                precision = "H" if len(tt) >= 8 else "b"
                content = BinToHex(reversedTT) if len(reversedTT) >= 8 else tt

                sv.append("defparam U{}.INIT = {}'{}{};\n".format(self.ID, self.contentSize, precision, content))

                precision = "H" if len(tt) >= 8 else "b"
                content = BinToHex(tt) if len(tt) >= 8 else tt

                sv.append("\tLUT{} U{}(.O({}), ".format(self.numInputs, self.ID, self.output))

                for i, lutInput in enumerate(self.inputs[:-1]):
                    sv.append(".I{}({}), ".format(i, decodeNet(lutInput)))
                
                sv.append(".I{}({}));\n".format(self.numInputs - 1, self.inputs[-1]))
            else:
                sv.append(self.getSOP())                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        
        return ''.join(sv) 

    def compareLUT(self, lut):
        """ Compare 2 luts, output the number of inputs they share.

        Args:
            lut (LUT): lut to compare to

        Returns:
            int: number of inputs shared between this lut and the one to compare
        """
        return len(set(self.inputs) & set(lut.inputs))

def decodeNet(net):
    """ Decode a net's string. i.e. "abc~20~" => "abc[20]"

    Args:
        net (string): encoded net string

    Returns:
        string: decoded net string
    """
    nsplit = net.split("~")

    if len(nsplit) > 1:
        ret = ''.join([nsplit[0], "[", nsplit[1], "]"])
    else:
        ret = net

    return ret

def isMatchDontCare(ttGold, testRow):
    """ Helper function for comparing truth table entries - accounting for don't cares

    Arguments:
        ttGold {[str]} -- Row from the LUT tt that may contain don't care inputs
        testRow {[str]} -- Row from other function to check as a match against ttGold

    Returns:
        boolean -- indicates whether or not the given inputs are a functional match
    """
    for i in range(len(ttGold)):
        if testRow[i] == "-":
            continue
        elif ttGold[i] != testRow[i]:
            return False
    
    return True

def BinToHex(binStr):
    """ Helper function for converting binary string to hex string

    Args:
        binStr (str): binary string

    Raises:
        Exception: binStr cannot be packed into hex format

    Returns:
        str: hex string
    """
    if len(binStr) % 8 != 0:
        raise Exception("Length of binary in BinToHex() must be multiple of 8.")

    h = '%0*X' % ((len(binStr) + 3) // 4, int(binStr, 2)) 

    return h