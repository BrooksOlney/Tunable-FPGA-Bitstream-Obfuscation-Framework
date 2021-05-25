import time as t
import re
from LUT import LUT
from Circuit import circuit
from Latch import latch
import functools

def readBLIF(filename):
    """ Parse BLIF into circuit object

    Args:
        filename ([string]): path to BLIF describing input circuit

    Returns:
        ckt (circuit): resulting circuit from parsing BLIF file
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
    outputs  = []
    wires    = []
    regs     = []
    luts     = []
    latches  = []

    # notes: signals can often just be of the format [1234], so we replace as ~1234~ to prevent issues
    # distinguishing [1234] from something like a[1234]...
    for i, line in enumerate(bliffile):

        if ".model" in line:
            sl = line.split(' ')
            cktName = sl[1]

        # encode primary input/output circuit ports
        elif ".inputs" in line or ".outputs" in line:
            ports = [port.replace("[", "~").replace("]", "~") for port in line.split(' ')[1:]]
            
            if ".inputs" in line:
                inputs = ports
            else:
                outputs = ports
        
        # encode LUT info into object
        elif ".names" in line:

            portList = line.split(' ')
            output = portList[-1]
            lutInputs = [port.replace("[", "~").replace("]", "~") for port in portList[1:-1]] 
            
            # ignore degenerate port - artifact from rtl tool
            if len(portList) == 2: continue

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

            if newLUT.numInputs == 0:
                print("uh oh")

            luts.append(newLUT)

        elif ".latch" in line:

            latchTypes = ["fe", "re", "ah", "al", "as"]
            portList = line.split(' ')[1:]
            latchInput, latchOutput = portList[:2]
            del portList[:2]
            latchInit = None
            latchControl = None
            latchType = None

            for port in portList:
                if port in latchTypes:
                    latchType = port
                elif port == "2" or port == "1" or port == "0":
                    latchInit = port
                else:
                    latchControl = port

            newLatch = latch(latchInput, latchOutput, latchType, latchControl, latchInit)
            latches.append(newLatch)


        else:
            if str.isspace(line) or line.startswith("#") or "end" in line or len(line.split(' ')) == 2 or line == '': continue
            raise Exception("Unsupported BLIF type @ line {}: {}".format(i, line))
            
    ckt = circuit(cktName, inputs, outputs, wires, regs, luts, latches)
    end = t.time()
    print("BLIF parsing took {0:04f}s to complete.".format(end - start))
    
    return ckt 

def writeBLIF(filename, ckt):

    blif = []

    if ckt.secured:
        blif.append("# Locked with Key = {}\n".format(ckt.obfKey))
    
    blif.append(".model {}\n".format(ckt.cktName))
    
    blif.append(".inputs ")
    for nettype, nets in zip([".inputs ", ".outputs "], [ckt.inputs, ckt.outputs]):
        blif.append(nettype)

        for net in nets:
            vecs = net.split('~')

            # NOTE: use the bottom 2 encodings for the nets interchangeably for whatever you're doing
            # I believe that ABC doesn't read brackets, which is why I had to use the first encoding.
            # Otherwise, use the second encoding if you are using the BLIF for other purposes.
            if len(vecs) > 1:
                blif.append("{} ".format(''.join(vecs[0], vecs[1])))
                # blif.append("{} ".format(''.join(vecs[0], "[", vecs[1], "]")))
            else:
                blif.append("{} ".format(net))

        if ckt.secured and nettype == ".inputs ":
            blif.append(' '.join([''.join(["sk", str(bit)]) for bit in range(len(ckt.obfKey))]))

        blif.append("\n")
    blif.append("\n")

    ckt.luts.sort(key=lambda x: x.ID)

    for lut in ckt.luts:
        lutStr = []
        lutStr.append(' '.join([".names", *map(functools.partial(decodeNet, blif=True), lut.inputs), decodeNet(lut.output)]))
        
        for minterm in lut.tt.items():
            lutStr.append(' '.join([*minterm]))
        
        blif.append('\n'.join(lutStr))
        blif.append("\n\n")

    blif.append("\n")
    blif.append(".end\n")

    with open(filename, "w") as bliffile:
        bliffile.write(''.join(blif))

def decodeNet(net, blif=False):

    nsplit = net.split("~")

    if len(nsplit) > 1:
        if blif:
            ret = ''.join([nsplit[0], nsplit[1]])
        else:
            ret = ''.join([nsplit[0], "[", nsplit[1], "]"])
    else:
        ret = net

    return ret

def writeVerilog(filename, ckt, vot, manufacturer):
    """ Writes a circuit to a verilog file based on the type of verilog desired and manufacturer.

    Args:
        filename (string): name of verilog file to write to
        ckt (circuit): circuit to output to verilog
        vot (string): type of verilog output, valid options are "comb" for combinational logic and "lutprim" for lut primitives
        manufacturer (string): manufacturer name, either "xilinx" or "altera"
    """
    start = t.time()
    vCode = []

    if ckt.secured:
        vCode.append('// sk = {}\n'.format(ckt.obfKey[::-1]))

    vCode.append("`timescale 10ns/1ns\n")
    
    if ckt.secured:
        vCode.append("module {} (/* input clk, */ input [{}:0] sk, ".format(ckt.cktName, len(ckt.obfKey) - 1))
    else:
        vCode.append("module {} (/* input clk, */ ".format(ckt.cktName))
    
    iVecs = parseVectors(ckt.inputs)
    oVecs = parseVectors(ckt.outputs)
    rVecs = parseVectors(ckt.regs)
    wVecs = parseVectors(ckt.wires)
    
    iStrs = []
    oStrs = []

    # writes the inputs/outputs within the module declaration
    for ivecKey, ivecVal in iVecs.items():
        if ivecVal > 0:
            iStrs.append("input [{}:0] {}".format(ivecVal, ivecKey))
        else:
            iStrs.append("input {}".format(ivecKey))
    
    for ovecKey, ovecVal in oVecs.items():
        regWire = "reg" if ovecKey in rVecs.keys() else "wire"
        
        if ovecVal > 0:
            oStrs.append("output {} [{}:0] {}".format(regWire, ovecVal, ovecKey))
        else:
            oStrs.append("output {} {}".format(regWire, ovecKey))
    
    vCode.append(', '.join(iStrs))
    vCode.append(', '.join(oStrs))
    vCode.append(");\n\n")

    # adds commented out registers for inputs/outputs/obfKey
    # these were required in order to get accurate timing overhead estimations for combinational benchmarks
    vCode.append("//reg [{}:0] inputs;\n".format(len(ckt.inputs) - 1))
    vCode.append("//reg [{}:0] outputs;\n".format(len(ckt.outputs) - 1))
    if ckt.secured: vCode.append("//reg [{}:0] sk_reg;\n".format(len(ckt.obfKey) - 1))
    vCode.append("//always @(posedge clk) inputs = {{{}}};\n".format(', '.join(ckt.inputs)))
    vCode.append("//always @(posedge clk) outputs = {{{}}};\n".format(', '.join(ckt.outputs)))
    if ckt.secured: vCode.append("//always @(posedge clk) sk_reg = {{{}}};\n".format(', '.join(ckt.outputs)))

    cnt = 0
    elemsPerLine = 10
    for rw, vecs in zip(["wire", "reg"], [wVecs.items(), rVecs.items()]):
        for key, val in vecs:
            if key in ckt.inputs or key in ckt.outputs or key in iVecs or key in oVecs:
                continue
            if val > 0:    
                vCode.write("\n\t{} [{}:0] {};\n".format(rw, val, key))
            else:
                if cnt == 0:
                    vCode.append("\n\t{} {}".format(rw, key))
                    cnt += 1
                elif cnt < elemsPerLine:
                    vCode.append(", {}".format(key))
                    cnt += 1
                else:
                    vCode.append(", {};".format(key))
                    cnt = 0
    
        if cnt != 0:
            cnt = 0
            vCode.append(";\n\n")
        
        elemsPerLine = 8

    for latch in ckt.latches:
        vCode.append(''.join(["\t", latch.toString(), "\n"]))

    vCode.append("\n")

    if vot == "lutprim":
        for lut in ckt.luts:
            vCode.append(lut.toPrimitive(manufacturer))
            vCode.append("\n")
    else:
        for lut in ckt.luts:
            vCode.append(lut.getSOP())
            vCode.append("\n")

    vCode.append("endmodule\n")

    # Altera LUT primitives use this submodule which is defined in some of their documentation
    if vot.upper() == "LUTPRIM" and manufacturer.upper() == "ALTERA":
        vCode.append("\n\n")
        lutPrim = []
        lutPrim.append("module lut_sub (din, out);")
        lutPrim.append("\tparameter LUT_SIZE = 4;")
        lutPrim.append("\tparameter NUM_BITS = 2**LUT_SIZE;")
        lutPrim.append("\n\tinput[LUT_SIZE - 1:0] din;")
        lutPrim.append("\n\toupput out;")
        lutPrim.append("\n\twire out;")
        lutPrim.append("")
        lutPrim.append("\t// buffer the LUT inputs...")
        lutPrim.append("\twire[LUT_SIZE - 1:0] din_w;")
        lutPrim.append("")
        lutPrim.append("\tgenvar i;")
        lutPrim.append("\tgenerate")
        lutPrim.append("\t\tfor (i = 0; i < LUT_SIZE; i = i + 1)")
        lutPrim.append("\t\t\tbegin: liloop")
        lutPrim.append("\t\t\tlut_input li_buf(din[i], din_w[i]);")
        lutPrim.append("\t\tend")
        lutPrim.append("\tendgenerate")
        lutPrim.append("")
        lutPrim.append("\t// build up the pterms for the LUT")
        lutPrim.append("\twire[NUM_BITS - 1:0] pterms;")
        lutPrim.append("\tgenerate")
        lutPrim.append("\t\tfor (i = 0; i < NUM_BITS; i = i + 1)")
        lutPrim.append("\t\t\tbegin: ploop")
        lutPrim.append("\t\t\tassign pterms[i] = ((din_w == i) & mask[i]);")
        lutPrim.append("\t\tend")
        lutPrim.append("\tendgenerate")
        lutPrim.append("")
        lutPrim.append("\t// assign the pterms to the LUT function")
        lutPrim.append("\twire result;")
        lutPrim.append("\tassign result = | pterms;")
        lutPrim.append("\tlut_output lo_buf (result, out);")
        lutPrim.append("endmodule")

        vCode.append('\n'.join(lutPrim))

    with open(filename, "w") as vFile:
        vFile.write(''.join(vCode))


    end = t.time()
    print("Wrote circuit {0} to verilog in {1:04f}s.".format(ckt.cktName, end - start))

def parseVectors(nodes):
    """ Parses a list of nodes (inputs, outputs, regs, wires, etc.) and encodes them based on whether they
        are a bus like [127:0]sk, or a single bit value like [1234] or 'a'.

    Args:
        nodes (list(string)): list of nodes to parse

    Returns:
        dict(string : int): dictionary encoding the inputted nodes
    """
    visited = []
    vectors = dict()

    for node in nodes:
        vec = node.split('~')
        if len(vec) == 1:
            visited.append(vec[0])
            vectors[vec[0]] = 0

        else:
            vName, vIdx, _ = vec

            if vName not in visited:
                visited.append(vName)
                vectors[vName] = int(vIdx)
            elif int(vIdx) > vectors[vName]:
                vectors[vName] = int(vIdx)

    return vectors