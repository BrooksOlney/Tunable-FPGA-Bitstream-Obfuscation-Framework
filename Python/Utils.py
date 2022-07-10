import time as t
from LUT import LUT
from Circuit import circuit
from Latch import latch
import functools
import subprocess
import os
import matplotlib.pyplot as plt
import numpy as np

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
            ports = [port.replace("[", "~").replace("]", "~") for port in line.split(' ')[1:] if port != '']
            
            if ".inputs" in line:
                inputs = ports
            else:
                outputs = ports
        
        # encode LUT info into object
        elif ".names" in line:

            portList = line.split(' ')
            output = portList[-1]
            lutInputs = [port.replace("[", "~").replace("]", "~") for port in portList[1:-1] if port != ''] 
            
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
                if wire not in wires and wire not in regs:
                    wires.append(wire)

            if output not in wires and output.replace("[","~").replace("]", "~") not in outputs:
                wires.append(output)

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
            regs.append(latchOutput)
            latches.append(newLatch)
            
            if latchOutput in wires:
                wires.remove(latchOutput)

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
    
    # blif.append(".inputs ")
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
            blif.append(' '.join([''.join(["keyinput", str(bit)]) for bit in range(len(ckt.obfKey))]))

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
            if nsplit[0] == 'sk':
                ret = f'keyinput{nsplit[1]}'
            else:
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
        vCode.append('// sk = {}\n'.format(ckt.obfKey))

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
    
    vCode.append(', '.join([*iStrs, *oStrs]))
    # vCode.append(', '.join(oStrs))
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
        lutPrim.append("\tinput[LUT_SIZE - 1:0] din;")
        lutPrim.append("\tparameter[NUM_BITS - 1:0] mask = {NUM_BITS{1'b0}};")
        lutPrim.append("\n\toutput out;")
        lutPrim.append("\twire out;")
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

def write_bench(fileHeader):
    abcPath = "/bin/abc"
    cwd = os.getcwd()
    msg = f'read_blif {cwd}/Python/blifs/{fileHeader}.blif\nfraig\nwrite_bench -l {cwd}/Python/benchs/{fileHeader}.bench\n'.encode()
    subprocess.Popen(abcPath,stdin=subprocess.PIPE,stdout=subprocess.PIPE).communicate(msg)
    # subprocess.Popen(abcPath,stdin=subprocess.PIPE,stdout=subprocess.PIPE).communicate(f'read_blif {cwd}/Python/blifs/{ckt.cktName}.blif\nfraig\nwrite_bench -l {cwd}/Python/benchs/{ckt.cktName}.bench\n'.encode())
    # subprocess.Popen(abcPath,stdin=subprocess.PIPE,stdout=subprocess.PIPE).communicate(f'read_blif {cwd}/Python/blifs/{ckt.cktName}_s.blif\nfraig\nwrite_bench -l {cwd}/Python/benchs/{ckt.cktName}_s.bench\n'.encode())

def plot_hist(ckt : circuit, cktObf : circuit):

    orig = ckt.getLUTsizeCount()
    obf = cktObf.getLUTsizeCount()

    # fig,ax = plt.subplots()
    plt.bar(np.arange(1,ckt.sizeLUT+1) - 0.12, orig,width=0.25, label='Original')
    plt.bar(np.arange(1,ckt.sizeLUT+1) + 0.12, obf,width=0.25, label='Obfuscated')
    plt.legend()
    plt.ylabel("# LUTs")
    plt.xlabel("LUT Size (# inputs)")
    plt.title("Design LUTs Before and After Obfuscation")

    plt.show()

def generate_testbench(goldenCkt : circuit, obfCkts):

    def write_instantiation_template(ckt : circuit, idx : int):
        output = f'{ckt.cktName} {ckt.cktName}_inst ('

        # inputVectors = parseVectors(ckt.inputs)
        # outputVectors = parseVectors(ckt.outputs)

        if ckt.secured:
            output += f'.sk(sk{idx}), '

        for i,input in enumerate(ckt.inputs):
            output += f'.{input}(inputs[{i}]), '

        instOutputs = []
        for i,out in enumerate(ckt.outputs):
            if ckt.secured:
                instOutputs.append(f'.{out}(obfusoutputs{idx}[{i}])')
            else:
                instOutputs.append(f'.{out}(outputs{idx}[{i}])')

        output += ', '.join(instOutputs)
        output += ');'

        return output


    txtOutput = []

    inputs = parseVectors(goldenCkt.inputs)
    outputs = parseVectors(goldenCkt.outputs)

    txtOutput.append('/* Testbench auto-generated by EDA tool */')
    txtOutput.append('`timescale 10ns/1ns')
    txtOutput.append(f'module GoldenChip_{goldenCkt.cktName} ();')
    txtOutput.append('')
    txtOutput.append('/* INPUTS */')

    numInputs = len(inputs.keys())
    numOutputs = len(outputs.keys())

    txtOutput.append(f'reg [{numInputs-1}:0] inputs;')
    txtOutput.append(f'localparam MAX_COUNT = {2**numInputs};')
    for i,obfCkt in enumerate(obfCkts):
        keylen = len(obfCkt.obfKey)
        txtOutput.append(f'reg [{len(obfCkt.inputs)-1}:0] mismatch{i};')
        txtOutput.append(f'reg [{keylen-1}:0]sk{i};')
        txtOutput.append(f'localparm [{keylen-1}:0] correct_sk{i} = {keylen}\'b{obfCkt.obfKey};')
    
    txtOutput.append('')
    txtOutput.append('/* OUTPUTS */')
    txtOutput.append(f'reg outputs[{numOutputs-1}:0];')
    txtOutput.append('')

    txtOutput.append('/* END NETS */')
    txtOutput.append('')

    
    txtOutput.append(write_instantiation_template(goldenCkt,0))
    for i,obfCkt in enumerate(obfCkts):
        txtOutput.append(write_instantiation_template(obfCkt,i))

    txtOutput.append('')
    txtOutput.append('')

    for i in range(len(obfCkts)):
        txtOutput.append(f'assign mismatch{i} = outputs ^ obfusoutputs{i};')
    txtOutput.append('')

    fileHandles = [f'f{i}' for i in range(len(obfCkts))]
    randomKeys  = [f'rk{i}' for i in range(len(obfCkts))]
    mismatches  = [f'real mismatchPercentage{i} = 0;' for i in range(len(obfCkts))]
    txtOutput.append(f'integer {",".join(fileHandles)};')
    txtOutput.append(f'integer {",".join(randomKeys)};')
    txtOutput.extend(mismatches)

    txtOutput.append('integer i, j, k, l;')
    txtOutput.append('initial begin')

    # for i in range(len(obfCkts)):
    #     txtOutput.append(f'\trk{i} = $fopen("RNG.txt", "r");')
    txtOutput += [f'\trk{i} = $fopen("RNG.txt", "r");' for i in range(len(obfCkts))]
    txtOutput += [f'\tf{i} = $fopen("functionalMismatch_{obfCkts[i].cktName}", "w");' for i in range(len(obfCkts))]

    txtOutput.append('end')
    txtOutput.append('')
    txtOutput.append('initial begin')
    txtOutput.append('\tfor(i = 0; i < MAX_COUNT; i = i + 1) begin')
    txtOutput.append(f'\t\tfor(l = 0; l < {len(obfCkts)}; l = l + 1) begin')
    txtOutput.extend([f'\t\t\t$fscanf(rk{i}, "%{len(obfCkts[i].obfKey)}, sk{i});' for i in range(len(obfCkts))])


    txtOutput.append("\t\t\t#1;")

    txtOutput.append(f'\t\t\tfor(j  = 0; j < {len(goldenCkt.outputs)}; j = j + 1) begin')
    txtOutput.extend([f'\t\t\t\tmismatchPercentage{i} = mismatchPercentage{i} + mismatch{i}[j];' for i in range(len(obfCkts))])
    txtOutput.append('\t\t\tend')

    txtOutput.append("\t\t\t#1;")
    txtOutput.extend([f'\t\t\tmismatchPercentage{i} = mismatchPercentage{i} / {len(obfCkts)};' for i in range(len(obfCkts))])
    txtOutput.append('')

    txtOutput.extend([f'\t\t\$fwrite(f{i}, "%f\n", mismatchPercentage{i});' for i in range(len(obfCkts))])
    txtOutput.append('')
    txtOutput.extend([f''])

    txtOutput.append('\t\tinputs = inputs + 1;')
    txtOutput.append('\tend')

    txtOutput += [f'\t$fclose(f{i});' for i in range(len(obfCkts))]
    txtOutput.append('end')
    txtOutput.append('')
    txtOutput.append('endmodule')

    with open(f'Python/verilog/{goldenCkt.cktName}_tb.v', 'w') as ofile:
        ofile.write('\n'.join(txtOutput))



    # print('hi')