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

// Read keyboard input

(LOOP)
@KBD
D=M
@NOTPRESSED
D;JEQ

@PRESSED
@color
M=-1
@CHECKSCREEN
0;JMP

(NOTPRESSED)
@color
M=0

// Check if screen and keyboad color are the same
(CHECKSCREEN)
@color
D=M
@SCREEN
D=D+M
D=D+1

@PAINT
D;JEQ
@LOOP
0;JMP


(PAINT)
// If not equal, fill screen with color
@SCREEN
D=A
@i
M=D
@8192
D=D+A
@n
M=D

(FILL)
// if i==n goto END
@i
D=M
@n
D=D-M
@LOOP
D;JEQ

// Set word i to color
@color
D=M
@i
A=M
M=D

// increment i
@i
M=M+1
@FILL
0;JMP

