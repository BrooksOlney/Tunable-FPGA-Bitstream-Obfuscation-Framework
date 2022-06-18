import time as t
import random
import numpy as np
import re
from copy import deepcopy
import argparse
import traceback

from LUT import LUT
from Circuit import circuit
import Utils

class ObfuscationEngine:
    def __init__(self, filename, vot, manufacturer, ks=-1,k=None):
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
        self.ks     = ks
        self.k      = k

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            # return False # uncomment to pass exception through

        return True
    
    def writeVerilog(self, filename, ofilename):

        Utils.writeVerilog(filename, self.ckt, self.vot, self.man)
        Utils.writeVerilog(ofilename, self.cktObf, self.vot, self.man)

    def writeBLIF(self, filename, ofilename):

        Utils.writeBLIF(filename, self.ckt)
        Utils.writeBLIF(filename, self.cktObf)

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
        lutParts = self.partitionLUTs(subCkt, 6)

        # generate random obfuscation key
        keySize = self.ks if self.ks != -1 else len(lutParts)
        obfKey = self.k[::-1] if self.k != None else bin(random.randint(0,2**keySize - 1))[2:].zfill(keySize)[::-1]

        # distribute the key throughout the partitions, 1 bit per partition
        for keyIdx, part in enumerate(lutParts):
            for lut in part:
                keyIdx %= keySize
                lutIdx = random.randint(0, lut.numInputs - 1)
                lut.addKeybit(obfKey[keyIdx], keyIdx, lutIdx)

        self.cktObf.secured = True
        self.cktObf.obfKey  = ''.join(obfKey[::-1])

        end = t.time()        
        print("Finished obfuscating design in {0:4f}s.".format(end - start))

    def satResilience(self, numInputs=None, maxlutsize=None):
        if numInputs  == None: numInputs  = len(self.ckt.inputs)
        if maxlutsize == None: maxlutsize = self.ckt.sizeLUT

        sID = max(i.ID for i in self.ckt.luts) + 1
        satKey  = [str(random.randint(0,1)) for x in range(numInputs)]
        sBit = len(self.ckt.obfKey) + 1 if self.ckt.secured else 0

        keyStrs = [''.join(["sk~", str(keyIdx), "~"]) for keyIdx in range(sBit, sBit + numInputs)]
        keyDict = {keyStr : satKeybit for keyStr, satKeybit in zip(keyStrs, satKey)}    

        satModuleInputs = self.ckt.inputs[:numInputs]
        
        compKeyGroups = (list(self.chunkList(satKey, maxlutsize // 2)), list(self.chunkList(keyStrs, maxlutsize // 2)))
        maskKeyGroups = (list(self.chunkList(satKey, maxlutsize)), list(self.chunkList(keyStrs, maxlutsize)))
        compInputGroups = list(self.chunkList(satModuleInputs, maxlutsize // 2))

        compLUTs = []
        
        compNum = 0
        for keyComp, inComp in zip(compKeyGroups, compInputGroups):
            lutInputs = [keyComp[0][:], inComp[:]]
            lutOutput = ''.join(["satCompare", str(compNum)])

            compLUT = LUT(sID, lutInputs, lutOutput)

            for i in range(len(inComp)):
                q = ''.join(["{:", str(numInputs // 2), "b}"])
                ttLine = str(q).format(i) * 2
                compLUT.addMinterm(ttLine, "1")
            
            compLUTs.append(compLUT)
            compNum += 1
            sID += 1


        print("STILL TO BE IMPLEMENTED FROM C# VERSION")

    def chunkList(self, lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

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
def main(args):

    print(args)
    with ObfuscationEngine(args.i, args.v, args.m, args.ks, args.k) as oe:
        
        oe.obfuscate(args.op)
        oe.writeVerilog(*args.vFiles)
        if args.blif:
            oe.writeBLIF(args.blif)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap._action_groups.pop()
    required = ap.add_argument_group('required arguments')
    required.add_argument('-i', help="Input BLIF file: -i {ckt_name.blif}")
    required.add_argument('-vFiles', help="Verilog output filenames: -vFiles ckt.v ckt_secured.v", type=str, nargs=2, required=True)
    required.add_argument('-m', help="FPGA manufacturer (for verilog primitives): -m {xilinx/altera}", required=True)
    required.add_argument('-v', help="Verilog Output Type: -v {comb, lutprim}", required=True)
    
    optional = ap.add_argument_group('optional arguments')
    optional.add_argument('-op', help="Percentage of design to obfuscate: -op {float(0.0, 1.0]}", type=float, default=1.0)
    # optional.add_argument('-sat', help="Implement SAT Attack resilience for the circuit: -sat")
    optional.add_argument('-blif', help="BLIF ouput filename: -blif {ckt_name.blif}")
    optional.add_argument('-ks', help="Desired size of the obfuscation key.", type=int, default=-1)
    optional.add_argument('-k', help="Hardcoded key to provide (won't randomly generate a key)", default=None)

    args = ap.parse_args()
    main(args)

