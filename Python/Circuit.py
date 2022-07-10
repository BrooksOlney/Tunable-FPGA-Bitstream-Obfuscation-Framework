from LUT import LUT

class circuit:
    def __init__(self, cktName, inputs, outputs, cktWires, cktRegs, LUTs, latches):
        """ Circuit class constructor.

        Args:
            cktName ([str]): name of the circuit
            inputs ([list(str)]): list of the primary circuit inputs
            outputs ([list(str)]): list of the primary circuit outputs
            LUTs ([list(LUT)]): list of all LUTs comprising the combinational logic of the circuit
        """
        self.cktName  = cktName
        self.inputs   = inputs
        self.outputs  = outputs
        self.wires    = cktWires
        self.regs     = cktRegs
        self.luts     = LUTs
        self.latches  = latches
        self.secured  = False
        self.obfP     = 0.0
        self.obfKey   = None
        # self.sizeLUT  = max(lut.numInputs for lut in LUTs)
        self.sizeLUT  = 6
    
    def calculateWeights(self):
        """ Compute the "weight" of each LUT which is used as a heuristic for certain obfuscation functions. 
            The weight of a LUT is simply its fanout, i.e. how many LUTs its output feeds into.
        """

        for lut in self.luts:
            lut.weight = sum(1 for _lut in self.luts if lut.output in _lut.inputs)
            
    def getLUTsizeCount(self):
        """ Returns an array of integers corresponding to the number of LUTs of that size.
            i.e. if arr[5] == 10, then there are 10 5-LUTs in the circuit
        """
        return [sum(1 for lut in self.luts if lut.numInputs == i) for i in range(1, self.sizeLUT + 1)]