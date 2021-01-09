import time as t
import random
import numpy as np
import re
from copy import deepcopy

from LUT import LUT
from Circuit import circuit

class ObfuscationEngine:
    def __init__(self, filename, vot, manufacturer):
        """ ObfuscationEngine class constructor. This class serves as the top level - in terms of data/function operations.
            Use this class to parse BLIF files, perform obfuscation, and compile output files.

        Args:
            filename ([str]): name of the BLIF file describing the circuit
            vot ([string]): verilog output type: combinational logic, minimized combinational logic, LUT primitives
            manufacturer ([list(str)]): manufacturer name, relevant for LUT primitives. Xilinx/Altera (AMD/Intel?)
        """
        self.ckt    = self.readBLIF(filename)
        self.cktObf = None
        self.vot    = vot
        self.man    = manufacturer

    def readBLIF(self, filename):
        """ Parse BLIF into circuit object

        Args:
            filename ([string]): path to BLIF describing input circuit
        """
        start = t.time()
        
        # remove multiline extensions in BLIF to make parsing easier
        # e.g. => .inputs a b c d \\n e f g ... out => .inputs a b c d e f g ... out
        with open(filename, mode="r") as _bliffile:
            bliffile = _bliffile.read().replace("\\\n ", "").replace("\\\r\n ", "")
            bliffile = bliffile.split("\n")

        lutCount = 0
        cktName  = ""
        inputs   = []
        outpus   = []
        wires    = []
        regs     = []
        luts     = []

        # notes: signals can often just be of the format [1234], so we replace as ~1234~ to prevent issues
        # distinguishing [1234] from something like a[1234]...
        for i, line in enumerate(bliffile):

            if "model" in line:
                sl = line.split(' ')
                cktName = sl[1]

            elif "inputs" in line or "outputs" in line:
                ports = [port.replace("[", "~").replace("]", "~") for port in line.split(' ')[1:]]
                
                if "inputs" in line:
                    inputs = ports
                else:
                    outputs = ports

            elif "names" in line:

                portList = line.split(' ')
                output = portList[-1]
                lutInputs = [port.replace("[", "~").replace("]", "~") for port in portList[1:-1]] 

                newLUT = LUT(lutCount, lutInputs, output)
                lutCount += 1
                hasMoreTT = True
                j = 1

                # parse the tt line by line
                while hasMoreTT:
                    ttLine  = bliffile[i + j]
                    ttEntry = ttLine.split(' ') 

                    if len(ttEntry) == 2:
                        newLUT.addMinterm(*ttEntry)
                        j += 1
                    else:  
                        hasMoreTT = False

                # add unseen wires 
                for wire in lutInputs:
                    if wire not in wires:
                        wires.append(wire)

                luts.append(newLUT)
        
            else:
                if str.isspace(line) or line.startswith("#") or "end" in line or len(line.split(' ')) == 2 or line == '': continue
                print("Unsupported BLIF type @ line {}: {}".format(i, line))
                
        ckt = circuit(cktName, inputs, outputs, wires, regs, luts)     
        end = t.time()
        print("BLIF parsing took {0:04f}s to complete.".format(end - start))
        
        return ckt 
    
    def obfuscate(self, p):
        """ Obfuscate a portion of the circuit. Size of the portion is adjusted by p.
            Implements the obfuscation approach published in this paper:

                B. Olney and R. Karam, "Tunable FPGA Bitstream Obfuscation with Boolean Satisfiability Attack Countermeasure"
                ACM Trans. Des. Autom. Electron. Syst. 25, 2, Article 19 (March 2020), 22 pages. DOI:https://doi.org/10.1145/3373638

        Args:
            p (float): percentage of circuit to obfuscate.
        """
        if p <= 0 or p > 1: raise Exception("Invalid value for p. Must be in range: 0 < p <= 1")
        self.cktObf = deepcopy(self.ckt)

        self.cktObf.calculateWeights()
        self.cktObf.LUTs.sort(key=lambda x: x.weight, reverse=True)

        lutSizes = self.cktObf.getLUTsizeCount()
        obfRange = int(p * len(self.cktObf.LUTs))

        # partition the LUTs for obfuscation to prevent key explosion
        subCkt = self.cktObf.LUTs[:obfRange]
        lutParts = partitionLUTs(subCkt)

        # generate random key
        obfKey = [random.randint(0,1) for x in range(len(lutParts))]


        for keybit, part in enumerate(lutParts):
            for lut in part:
                lutIdx = random.randint(0, lut.numInputs - 1)
                

        print("success!")

    def partitionLUTs(self, luts):
        partitions = []

        return partitions

# just testing for now
def main():
    alu4_oe = ObfuscationEngine(filename="F:\\Research\\Tunable_MUTARCH\\Python\\alu4.blif", vot="combinational", manufacturer="Altera")
    alu4_oe.obfuscate(0.1)

if __name__ == "__main__":
    main()