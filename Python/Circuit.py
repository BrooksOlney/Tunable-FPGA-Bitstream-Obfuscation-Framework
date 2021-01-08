import time
import random as rnd
import numpy as np
from LUT import LUT

class circuit:
    def __init__(self, cktName, inputs, outputs, cktWires, cktRegs, cktLUTs):
        """ Circuit class constructor.

        Args:
            cktName ([str]): name of the circuit
            inputs ([list(str)]): list of the primary circuit inputs
            outputs ([list(str)]): list of the primary circuit outputs
            cktLUTs ([list(LUT)]): list of all LUTs comprising the combinational logic of the circuit
        """
        self.cktName  = cktName
        self.inputs   = inputs
        self.outputs  = outputs
        self.cktWires = cktWires
        self.cktRegs  = cktRegs
        self.cktLUTs  = cktLUTs
        self.sizeConstraint = max(lut.numInputs for lut in cktLUTs)
        self.sizeLUTs = [sum(1 for lut in self.cktLUTs if lut.numInputs == i) for i in range(1, self.sizeConstraint)]
        
    
    