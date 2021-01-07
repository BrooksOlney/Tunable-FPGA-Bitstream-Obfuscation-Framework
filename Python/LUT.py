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
            output {str} -- Binary 1/0 corresponding to min/max-term expression
        """
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

        for i in range(len(hmacsub)):
            q = "{:" + str(self.numInputs) + "b}"
            ttLine = str(q).format(i)

            ttLine = ttLine[:lutIdx] + incorrectKeybit + ttLine[lutIdx:]

            if hmacSub[i] == minMaxterm:
                tt_sec[ttLine] = minMaxterm

        self.tt = tt_sec
        self.inputs.insert(lutIdx, ''.join("sk[", keyIdx, "]"))
        self.numInputs += 1


    def addKeybit(self, keybit, keyIdx, lutIdx):
        """ Add keybit to input list, insert obfuscation function

        Arguments:
            keybit {str} -- Binary value of keybit (1/0)
            keyIdx {str} -- Index of the keybit in the entire secret key (sk[1]) -> 1
            lutIdx {str} -- Index of the LUT inputs to insert the keybit
        """
        # determine what the reverse (incorrect) keybit is
        if keybit is "0":
            revKeybit = "1"
        elif keybit is "1":
            revKeybit = "0"

        # BLIF files sometimes mix min-/max-term function implementations
        # We must make sure to stick to one in our implementation for proper integration
        # into tools like ABC and the SAT Attack 
        minMax = "0"
        for ttLine, output in self.tt.items():
            if output is "1":
                minMax = "1"

        # build secured truth table with the correct keybit to preserve functionality
        ttSec = {}
        while (len(self.tt) > 0):
            ttEntry = self.tt.popitem()
            ttLine = ttEntry[0]
            ttOutput = ttEntry[1]

            ttLine = ttLine[:lutIdx] + keybit + ttLine[lutIdx:]
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
                    if rnd.randint(100) < 20:
                        ttEntry[j] = "1"
                    else:
                        ttEntry[j] = "-"

                if "1" in ttEntry:
                    ttEntry[lutIdx] = revKeybit
                    ttSec[''.join(ttEntry)] = minMax
        
        self.inputs.insert(lutIdx, "sk[" + keyIdx + "]")
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
        inputList = list()

        for i in range(self.numInputs):
            li = self.inputs[i].split('~')
            if len(li) > 1:
                sli = ''.join((li[0], "[", li[1], "]", li[2]))
            else:
                sli = ''.join(li[0])
            
            inputList.append(sli)

            if i != self.numInputs - 1:
                inputList.append(", ")
            
        return ''.join(inputList)

    # def getPLADesc(self):
    
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
                if output is "0":
                    continue
                sop.append("(")

                for i in range(self.numInputs):
                    li = self.inputs[i].split('~')
                    
                    if len(li) > 1:
                        sli = ''.join((li[0], "[", li[1], "]", li[2]))
                    else:
                        sli = li[0]
                    
                    if output is "1":
                        sop.append("({0})".format(li))
                    else:
                        sop.append("(!{0})".format(sli))
                    
                    sop.append(")")
                    mintermCount += 1
                    if mintermCount < len(self.mintt):
                        sop.append(" + ")

                sop.append(");")

        else:
            tt = self.expandTruthTable()
            ttRow = list()

def isMatchDontCare(ttGold, testRow):
    """ Helper function for comparing truth table entries - accounting for don't cares

    Arguments:
        ttGold {[str]} -- Row from the LUT tt that may contain don't care inputs
        testRow {[str]} -- Row from other function to check as a match against ttGold

    Returns:
        [boolean] -- indicates whether or not the given inputs are a functional match
    """
    for i in range(len(ttGold)):
        if testRow[i] is "-":
            continue
        elif ttGold[i] != testRow[i]:
            return False
    
    return True