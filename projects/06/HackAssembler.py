import sys

symbolTable = {}
compTable = {}
jmpTable = {}
destTable = {}

def addPreDefinedSymbols():
	for i in range(0,16):
		symbolTable["R" + str(i)] = i
	symbolTable["SCREEN"] = 16384
	symbolTable["KBD"] = 24576
	symbolTable["SP"] = 0
	symbolTable["LCL"] = 1
	symbolTable["ARG"] = 2
	symbolTable["THIS"] = 3
	symbolTable["THAT"] = 4


def addComp():
	compTable["0"] = "0101010"
	compTable["1"] = "0111111"
	compTable["-1"] = "0111010"
	compTable["D"] = "0001100"
	compTable["A"] = "0110000"
	compTable["M"] = "1110000"
	compTable["!D"] = "0001101"
	compTable["!A"] = "0110001"
	compTable["!M"] = "1110001"
	compTable["-D"] = "0001111"
	compTable["-A"] = "0110011"
	compTable["-M"] = "1110011"
	compTable["D+1"] = "0011111"
	compTable["1+D"] = "0011111"
	compTable["A+1"] = "0110111"
	compTable["M+1"] = "1110111"
	compTable["1+A"] = "0110111"
	compTable["1+M"] = "1110111"
	compTable["D-1"] = "0001110"
	compTable["A-1"] = "0110010"
	compTable["M-1"] = "1110010"
	compTable["D+A"] = "0000010"
	compTable["D+M"] = "1000010"
	compTable["A+D"] = "0000010"
	compTable["M+D"] = "1000010"
	compTable["D-A"] = "0010011"
	compTable["D-M"] = "1010011"
	compTable["A-D"] = "0000111"
	compTable["M-D"] = "1000111"
	compTable["D&A"] = "0000000"
	compTable["D&M"] = "1000000"
	compTable["A&D"] = "0000000"
	compTable["M&D"] = "1000000"
	compTable["D|A"] = "0010101"
	compTable["D|M"] = "1010101"
	compTable["A|D"] = "0010101"
	compTable["M|D"] = "1010101"

def addDest():
	destTable["null"] = "000"
	destTable["M"] = "001"
	destTable["D"] = "010"
	destTable["MD"] = "011"
	destTable["A"] = "100"
	destTable["AM"] = "101"
	destTable["AD"] = "110"
	destTable["AMD"] = "111"

def addJmp():
	jmpTable["null"] = "000"
	jmpTable["JGT"] = "001"
	jmpTable["JEQ"] = "010"
	jmpTable["JGE"] = "011"
	jmpTable["JLT"] = "100"
	jmpTable["JNE"] = "101"
	jmpTable["JLE"] = "110"
	jmpTable["JMP"] = "111"


def error(linenumber):
	print("error on line " + str(linenumber))
	sys.exit(0)


def main():
	addPreDefinedSymbols()
	addComp()
	addDest()
	addJmp()
	if len(sys.argv) == 1:
		print("Please enter the file name you want assembled");
		sys.exit(0)
	try:
		f = open(sys.argv[1])
		linenumber = 0
		for line in f:
			if line:
				line = line.split()
				if line:
					line = line[0]
					if(not line.startswith("//")):
						if line.startswith("(") and line.endswith(")"):
							if(symbolTable.has_key(line[1:len(line) - 1])):
								error(linenumber)
							else:
								symbolTable[line[1:len(line) - 1]] = linenumber
						else:
							linenumber = linenumber + 1
	except IOError:
		print("<file \"" + sys.argv[1] + "\"  does not exist>")
		sys.exit(0)

	asmFile = open(sys.argv[1].split('.')[0] + ".hack", "w+")
	f = open(sys.argv[1])
	nextFreeRamAddress = 16
	for line in f:
		if line:
			line = line.split()
			if line:
				line = line[0]
				if (line.startswith("@")):
					aCommand = ''
					if(line[1:].isdigit()):
						aCommand = bin(int(line.split()[0][1:]))[2:].zfill(16)
					elif symbolTable.has_key(line[1:]):
						aCommand = bin(symbolTable[line[1:]])[2:].zfill(16)
					else:
						symbolTable[line.split()[0][1:]] = nextFreeRamAddress
						nextFreeRamAddress = nextFreeRamAddress + 1
						aCommand = bin(symbolTable[line[1:]])[2:].zfill(16)
					asmFile.write(aCommand + '\n')
					continue 
				jmp = ''
				comp = ''
				dest = ''
				if '=' in line and ';' in line:
					jmp = line[line.index(';') + 1:]
					dest = line[:line.index('=')]
					comp = line[line.index('=') + 1:line.index(';')]
				elif '=' in line:
					jmp = 'null'
					dest = line[:line.index('=')]
					comp = line[line.index('=') + 1:]
				elif ';' in line:
					comp = line[:line.index(';')]
					dest = 'null'
					jmp = line[line.index(';') + 1:]
				if jmp != '':
					cCommand = "111" + compTable[comp] + destTable[dest] + jmpTable[jmp]
					asmFile.write(cCommand + '\n')

main()