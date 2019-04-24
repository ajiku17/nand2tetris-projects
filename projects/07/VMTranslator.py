import sys

segmentTable = {};

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


def main():
	buildTable()
	f = open(sys.argv[1])
	asmFile = open(sys.argv[1].split('.')[0] + ".asm", "w+")
	jmpCounter = 1
	for line in f:
		if line:
			line = line.split()
			if line:
				if not line[0].startswith('//'):
					if(line[0].startswith('push')):
						if(line[1].startswith('constant')):
							asmFile.write("//" + line[0] + " " + line[1] + " " + line[2] + "\n")
							asmFile.write(pushConstant(line[2]))
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
						asmFile.write(expression("+"))
					elif line[0].startswith('sub'):
						asmFile.write(expression("-"))
					elif line[0].startswith('neg'):
						asmFile.write(neg())
					elif line[0].startswith('and'):
						asmFile.write(expression("&"))
					elif line[0].startswith('or'):
						asmFile.write(expression("|"))
					elif line[0].startswith('not'):
						asmFile.write(notCode())
					elif line[0].startswith("eq"):
						asmFile.write(getBoolean(jmpCounter, "JEQ"))
						jmpCounter = jmpCounter + 1
					elif line[0].startswith("lt"):
						asmFile.write(getBoolean(jmpCounter, "JGT"))
						jmpCounter = jmpCounter + 1
					elif line[0].startswith("gt"):
						asmFile.write(getBoolean(jmpCounter, "JLT"))
						jmpCounter = jmpCounter + 1

main()