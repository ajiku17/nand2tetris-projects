import sys
import glob
import os

returnCounter = 0
currFnName = ""
segmentTable = {}

def buildTable():
	segmentTable["local"] = "LCL"
	segmentTable["argument"] = "ARG"
	segmentTable['this'] = "THIS"
	segmentTable['that'] = "THAT"
	segmentTable["temp"] = "5"
	

def pushConstant(const):
	return "@" + str(const) + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

def expression(operator):
	return "@SP\nM=M-1\n@SP\nA=M\nD=M\n@SP\nM=M-1\n@SP\nA=M\nM=M" + str(operator) + "D\n@SP\nM=M+1\n"

def neg():
	return "@SP\nM=M-1\n@SP\nA=M\nM=-M\n@SP\nM=M+1\n"

def notCode():
	return "@SP\nM=M-1\n@SP\nA=M\nM=!M\n@SP\nM=M+1\n"

def getBoolean(counter, cond):
	return "@SP\nM=M-1\n@SP\nA=M\nD=M\n@SP\nM=M-1\n@SP\nA=M\nD=D-M\n@WRITETRUE" + str(counter) + "\nD;" + cond + "\n@SP\nA=M\nM=0\n@END" + str(counter) + "\n0;JMP\n(WRITETRUE" + str(counter) +  ")\n@SP\nA=M\nM=-1\n(END"+ str(counter) + ")\n@SP\nM=M+1\n"


#################################
def pushStatement(base, index):
	return "@" + str(index) + "\nD=A\n@" + segmentTable[base] + "\nA=M\nA=A+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

def popStatement(base, index):
	return "@" + str(index) + "\nD=A\n@" + segmentTable[base] + "\nA=M\nD=A+D\n@R13\nM=D\n@SP\nM=M-1\n@SP\nA=M\nD=M\n@R13\nA=M\nM=D\n"

def popStatic(name, index):
	return "@SP\nM=M-1\n@SP\nA=M\nD=M\n@" + name + "." + index + "\nM=D\n"

def pushStatic(name, index):
	return "@" + name + "." + index + "\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

def pushPointer(index):
	if index == 0:
		return "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
	else:
		return "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

def popPointer(index):
	if index == 0:
		return "@SP\nM=M-1\n@SP\nA=M\nD=M\n@THIS\nM=D\n"
	else:
		return "@SP\nM=M-1\n@SP\nA=M\nD=M\n@THAT\nM=D\n"

def popTemp(index):
	return "@SP\nM=M-1\n@SP\nA=M\nD=M\n@" + str(5+index) + "\nM=D\n"

def pushTemp(index):
	return "@" + str(5+index) + "\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

def goTo(label):
	return "@" + label + "\n0;JMP\n";

def ifGoTo(label):
	return "@SP\nM=M-1\n@SP\nA=M\nD=M\n@" + label + "\nD;JNE\n"

def pushD(label):
	return "@" + label + "\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

def repositionARG(nArgs):
	return "@SP\nD=M\n@5\nD=D-A\n@" + str(nArgs) + "\nD=D-A\n@ARG\nM=D\n"

def repositionLCL():
	return "@SP\nD=M\n@LCL\nM=D\n"

def retLabel(fnName):
	print(fnName + "$ret." + str(returnCounter))
	return fnName + "$ret." + str(returnCounter)

def pushRet(fnName):
	return "(" + retLabel(fnName) + ")"

def callFunction(fnName, nArgs):
	global returnCounter
	returnCounter = returnCounter + 1
	return "@" + retLabel(currFnName) + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" + pushD('LCL') + pushD('ARG') + pushD('THIS') + pushD('THAT') + repositionARG(nArgs) + repositionLCL() + "@" + fnName + "\n0;JMP\n" + "(" + retLabel(currFnName) + ")\n"


def fnDeclaration(fnName, nVars):
	global returnCounter
	returnCounter = 0
	global currFnName
	currFnName = fnName
	res = "(" + fnName + ")\n"
	for i in range(nVars):
		res += "@SP\nA=M\nM=0\n@SP\nM=M+1\n"
	return res

def returnStatement():
	return "@LCL\nD=M\n@endFrame\nM=D\n@5\nD=A\n@endFrame\nD=M-D\nA=D\nD=M\n@retAddr\nM=D\n@SP\nM=M-1\n@SP\nA=M\nD=M\n@ARG\nA=M\nM=D\n@ARG\nD=M+1\n@SP\nM=D\n@endFrame\nMD=M-1\nA=D\nD=M\n@THAT\nM=D\n@endFrame\nMD=M-1\nA=D\nD=M\n@THIS\nM=D\n@endFrame\nMD=M-1\nA=D\nD=M\n@ARG\nM=D\n@endFrame\nMD=M-1\nA=D\nD=M\n@LCL\nM=D\n@retAddr\nA=M\n0;JMP\n"

def VMinit():
	return "@256\n" + "D=A\n" + "@SP\n" + "M=D\n"# + callFunction('Sys.init', 0) 

def main():
	buildTable()
	if os.path.isfile(sys.argv[1]):
		f = [sys.argv[1]]
		asmFile = open(sys.argv[1].split('.')[0] + ".asm", "w+")
	else:
		f = glob.glob(sys.argv[1] + "*.vm")
		print(sys.argv[1].split('/'))
		asmFile = open(sys.argv[1] + sys.argv[1].split('/')[-2] + ".asm", "w+")
		print(asmFile)

	jmpCounter = 1
	asmFile.write(VMinit());

	for filename in f:
		file = open(filename)
		print(filename)
		for line in file:
			if line:
				line = line.split()
				if line:	
					# print(line)
					if not line[0].startswith('//'):
						if(line[0].startswith('push')):
							if(line[1].startswith('constant')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(pushConstant(line[2]))
								# print('WHAT')
							elif(line[1].startswith('argument')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(pushStatement('argument', line[2]))
							elif(line[1].startswith('this')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(pushStatement('this', line[2]))
							elif(line[1].startswith('that')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(pushStatement('that', line[2]))
							elif(line[1].startswith('local')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(pushStatement('local', line[2]))
							elif(line[1].startswith('temp')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(pushTemp(int(line[2])))
							elif(line[1].startswith('pointer')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(pushPointer(int(line[2])))
							elif(line[1].startswith('static')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(pushStatic(sys.argv[1].split(".")[0].split('/')[-1], line[2]))
						elif(line[0].startswith('pop')):
							if(line[1].startswith('local')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(popStatement('local', line[2]))
							elif(line[1].startswith('argument')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(popStatement('argument', line[2]))
							elif(line[1].startswith('this')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(popStatement('this', line[2]))
							elif(line[1].startswith('that')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(popStatement('that', line[2]))
							elif(line[1].startswith('static')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(popStatic(sys.argv[1].split(".")[0].split('/')[-1], line[2]))
							elif(line[1].startswith('pointer')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(popPointer(int(line[2])))
							elif(line[1].startswith('temp')):
								asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
								asmFile.write(popTemp(int(line[2])))
						elif line[0].startswith('add'):
							asmFile.write("//ADD\n")
							asmFile.write(expression("+"))
						elif line[0].startswith('sub'):
							asmFile.write("//SUB\n")
							asmFile.write(expression("-"))
						elif line[0].startswith('neg'):
							asmFile.write("//NEG\n")
							asmFile.write(neg())
						elif line[0].startswith('and'):
							asmFile.write("//AND\n")
							asmFile.write(expression("&"))
						elif line[0].startswith('or'):
							asmFile.write("//OR\n")
							asmFile.write(expression("|"))
						elif line[0].startswith('not'):
							asmFile.write("//NOT\n")
							asmFile.write(notCode())
						elif line[0].startswith("eq"):
							asmFile.write("//EQ\n")
							asmFile.write(getBoolean(jmpCounter, "JEQ"))
							jmpCounter = jmpCounter + 1
						elif line[0].startswith("lt"):
							asmFile.write("//LT\n")
							asmFile.write(getBoolean(jmpCounter, "JGT"))
							jmpCounter = jmpCounter + 1
						elif line[0].startswith("gt"):
							asmFile.write("//GT\n")
							asmFile.write(getBoolean(jmpCounter, "JLT"))
							jmpCounter = jmpCounter + 1
						elif line[0].startswith("label"):
							asmFile.write("(" + line[1] + ")\n")
						elif line[0].startswith("goto"):
							asmFile.write(goTo(line[1]))
						elif line[0].startswith("if-goto"):
							asmFile.write(ifGoTo(line[1]))
						elif line[0].startswith('call'):
							asmFile.write(callFunction(line[1], int(line[2])))
						elif line[0].startswith('function'):
							asmFile.write(fnDeclaration(line[1], int(line[2])))
						elif line[0].startswith('return'):
							asmFile.write(returnStatement())

main()