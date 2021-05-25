import re

class latch:
    def __init__(self, linput, output, lType, control, initVal):

        self.linput    = linput
        self.output    = output
        self.latchType = lType
        self.control   = control
        self.initVal   = initVal

    
    def toString(self):
        latchSB = []

        if self.latchType == "re":
            latchSB.append("always @(posedge {0}) begin {1} <= {2}; end".format(self.control, self.output, self.linput))
        elif self.latchType == "fe":
            latchSB.append("always @(negedge {0}) begin {1} <= {2}; end".format(self.control, self.output, self.linput))
        elif self.latchType == "ah":
            latchSB.append("always @({0}) begin if({0}) {1} <= {2}; end".format(self.control, self.output, self.linput))
        elif self.latchType == "al":
            latchSB.append("always @({0}) begin if(!{0}) {1} <= {2}; end".format(self.control, self.output, self.linput))
        elif self.latchType == "as":
            latchSB.append("always @({0}) begin {1} <= {0}; end".format(self.linput, self.output))
        elif self.latchType == "":
            latchSB.append("always @({0}) begin {1} <= {0}; end".format(self.linput, self.output))
        else:
            raise Exception("Invalid latch type found .BLIF file.")
            
        return ''.join(latchSB)