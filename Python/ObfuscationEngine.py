import time as t
import random
import numpy as np
import re
from copy import deepcopy

from LUT import LUT
from Circuit import circuit
import Utils

class ObfuscationEngine:
    def __init__(self, filename, vot, manufacturer):
        """ ObfuscationEngine class constructor. This class serves as the top level - in terms of data/function operations.
            Use this class to parse BLIF files, perform obfuscation, and compile output files.

        Args:
            filename ([str]): name of the BLIF file describing the circuit
            vot ([string]): verilog output type: combinational logic, minimized combinational logic, LUT primitives
            manufacturer ([list(str)]): manufacturer name, relevant for LUT primitives. Xilinx/Altera (AMD/Intel?)
        """
        self.ckt    = Utils.readBLIF(filename)
        self.cktObf = None
        self.vot    = vot
        self.man    = manufacturer
    
    def obfuscate(self, p):
        """ Obfuscate a portion of the circuit. Size of the portion is adjusted by p.
            Implements the obfuscation approach published in this paper:

                B. Olney and R. Karam, "Tunable FPGA Bitstream Obfuscation with Boolean Satisfiability Attack Countermeasure"
                ACM Trans. Des. Autom. Electron. Syst. 25, 2, Article 19 (March 2020), 22 pages. DOI:https://doi.org/10.1145/3373638

        Args:
            p (float): percentage of circuit to obfuscate.
        """
        if p <= 0 or p > 1: raise Exception("Invalid value for p. Must be in range: 0 < p <= 1")
        start = t.time()

        self.cktObf = deepcopy(self.ckt)
        self.cktObf.calculateWeights()
        self.cktObf.luts.sort(key=lambda x: x.weight, reverse=True)

        lutSizes = self.cktObf.getLUTsizeCount()
        obfRange = int(p * len(self.cktObf.luts))

        # partition the LUTs for obfuscation to prevent key explosion
        subCkt = [l for l in self.cktObf.luts if l.numInputs < self.ckt.sizeLUT][:obfRange]
        lutParts = self.partitionLUTs(subCkt, 5)

        # generate random obfuscation key
        obfKey = [str(random.randint(0,1)) for x in range(len(lutParts))]

        # distribute the key throughout the partitions, 1 bit per partition
        for keyIdx, part in enumerate(lutParts):
            for lut in part:
                lutIdx = random.randint(0, lut.numInputs - 1)
                lut.addKeybit(obfKey[keyIdx], keyIdx, lutIdx)

        self.cktObf.secured = True
        self.cktObf.obfKey  = ''.join(obfKey)

        end = t.time()        
        print("Finished obfuscating design in {0:4f}s.".format(end - start))

    def partitionLUTs(self, luts, n):
        """ Partition the LUTs based on how many inputs are shared between them. Partitioning the LUTs
            is good because it helps prevent the key from becoming too large, and can improve overheads.

        Args:
            luts (list(LUT)): LUTs to partition
            n (int): max size of partitions

        Returns:
            list(list(LUT)): resulting partitions
        """
        partitions = []

        while luts:
            lut = luts.pop(0)
            p = [lut]

            # rank candidate LUTs by number of inputs shared with the current LUT
            cands = [(l, lut.compareLUT(l)) for l in luts if lut.compareLUT(lut) > 0]
            cands.sort(key=lambda x: x[1], reverse=True)
            cands = [l[0] for l in cands]
            
            # create partition and remove those LUTs from original list
            p = [lut, *cands[:n-1]]
            partitions.append(p)
            luts = [l for l in luts if l not in cands[:n-1]]

        return partitions

# just testing for now
def main():
    alu4_oe = ObfuscationEngine(filename="F:\\Research\\Tunable_MUTARCH\\Python\\blifs\\spla.blif", vot="combinational", manufacturer="Altera")
    alu4_oe.obfuscate(0.1)

    # Utils.writeVerilog("alu4.v", alu4_oe.ckt, "comb", "altera")
    Utils.writeBLIF("spla_s.blif", alu4_oe.cktObf)
    # Utils.writeBLIF("alu4.blif", alu4_oe.cktObf)

if __name__ == "__main__":
    main()