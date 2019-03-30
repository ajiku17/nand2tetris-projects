// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

@KBD
D=A
@SCREEN
D=D-A
@n
M=D

(START)
@i
M=0
@KBD
D=M
@LOOPWHITE
D;JEQ

(LOOPBLACK)
@n
D=M
@i
D=D-M
@START
D;JLE

@SCREEN
D=A
@i
A=D+M
M=-1
@i
M=M+1
@LOOPBLACK
0;JMP


(LOOPWHITE)
@n
D=M
@i
D=D-M
@START
D;JLE

@SCREEN
D=A
@i
A=D+M
M=0
@i
M=M+1
@LOOPWHITE
0;JMP



