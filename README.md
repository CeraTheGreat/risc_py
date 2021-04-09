# risc_py
A simple RISC interpereter in python

Largely based on the pseudo-assembly used in the [Zachtronics](http://www.zachtronics.com/) game **TIS-100**


## Placeholders

- **\<SRC\>** – A read location, register, constant value or otherwise
- **\<DST\>** – A write location, register or stack
- **\<TAG\>** – A tag marking a line in the code.


## Old Functionality
This interpereter includes the base functionality from **TIS-100**:

### Registers
- **ACC** – Accumulator for math and comparisons
- **BAK** – Backup register

### Instructions
- **MOV** *\<SRC\> \<DST\>* – Move value from *\<SRC\>* to *\<DST\>*
- **ADD** *\<SRC\>* – Add *\<SRC\>* to *ACC*
- **SUB** *\<SRC\>* – Subtract *\<SRC\>* from *ACC*
- **JMP** *\<SRC\>* – Jump unconditionally to *\<SRC\>*
- **JEZ** *\<SRC\>* – Jump if ACC is zero to *\<SRC\>*
- **JNZ** *\<SRC\>* – Jump if ACC is not zero to *\<SRC\>*
- **JGZ** *\<SRC\>* – Jump if ACC is greater than zero to *\<SRC\>*
- **JLZ** *\<SRC\>* – Jump if ACC is less than zero to *\<SRC\>*


## New Functionality
This old functionality is difficult by design, it is a puzzle game after all. This project, however, adds several new commands and some new functionality was included for fun:

### Registers
- **STP** – Stack pointer, Read only register which points to the head of the stack
- **SFP** – Stack frame pointer, Read only register which points to the end of the current frame
- **BSP** – Stack frame base pointer, Read only register which points to the start of the current frame

### Instructions
- **PSH** *\<SRC\>* – Push the value from *\<SRC\>* onto the stack
- **CHP** *\<SRC\>* – Print the value from *\<SRC\>* formatted as a char
- **INP** *\<SRC\>* – Print the value from *\<SRC\>* formatted as an int
- **POP** – Remove and discard the head of the stack
- **CLL** *\<SRC\>* – Call a function at location *\<SRC\>* without stack arguments
- **RET** – Return from a function call
- **HLT** – Stop execution


## The Stack

Growing and shrinking the stack is done with **PSH** and **POP** respectively. There is no limit to the size of the stack except for memory constraints.

Any element within the stack can be accessed with the [Memory Access](#memory-access) functionality.

The stack contains all the constructs neccesary for function calls.


## Functions and Stack Frames
Stack frames are constructed in the following way:

```
  .  Prev General Use Stack  .
  :                          :
  |                          |
  ----------------------------
  |      Stack Arguments     |  n - k
  :                          :
  .                          .  
  :                          :
  |                          |  n - 1
--------------------------------
  | Prev Instruction Pointer |  n       <-- Current Base Stack Pointer
  ----------------------------
  |  Prev Base Stack Pointer |  n + 1   
  ----------------------------
  | Prev Stack Frame Pointer |  n + 2   <-- Current Stack Frame Pointer
--------------------------------
  |    General Use Stack     |  
  :                          :
  .                          .
```

The **CLL** and **RET** instructions automatically construct and deconstruct the stack frame.

You may change the values of the stack arguments. **DO NOT** change the values of the three pointers at _n_, _n+1_ and _n+2_. This will break your program.

To access stack arguments, you must offset onto the stack behind the current Base Stack Pointer or use a register to pass arguments. You should know how many arguments your function takes and therefore know exactly how far to offset. If you need to pass an arbitrary number of arguments, consider adding a count argument at _n-1_ and use that to further offset your program.
## Memory Access
Memory access is done by placing brackets around a *\<DST\>* or *\<SRC\>* value:

```
MOV [ACC] [BAK]
```
This code takes the value pointed at by **ACC** and moves it to the location pointed at by **BAK**. This is akin to dereferencing a pointer in C/C++. 

Memory access is always in reference to the stack. A register may hold a value, but using square brackets will reference a location on the stack. Accessing memory outside of the current stack will cause an error.


## I/O
### Input
Input is only done through command line arguments. Command line arguments are provided to the program on the stack in the following way:

```
       Beggining of Stack
_________________________________
  |          argc            |  0       <-- Initial Base Stack Pointer
  ----------------------------
  |        arg_1 ptr         |  1       --> Points to memory cell 'a'
  ----------------------------
  |        arg_2 ptr         |  2       --> Points to memory cell 'b'
  ----------------------------
  |        arg_n ptr         |  3
  :                          :
  .                          .  
  :                          :
  |                          |  n       
  ----------------------------
  |       arg_1 char_0       |  a
  :       arg_1 char_1       :  a + 1
  .       arg_1 char_2       .  a + 2
  :                          :
  |    arg_1 char_k ('\0')   |  a + k     
  ----------------------------
  |       arg_2 char_0       |  b
  :       arg_2 char_1       :  b + 1
  .       arg_2 char_2       .  b + 2
  :                          :
  |    arg_2 char_k ('\0')   |  b + k     
  ----------------------------
  |       arg_m char_0       |  m
  :       arg_m char_1       :  m + 1
  .       arg_m char_2       .  m + 2
  :                          :
  |    arg_m char_k ('\0')   |  m + k      <-- Current Stack Frame Pointer
--------------------------------
  |    General Use Stack     |  
  :                          :
  .                          .
```

The first memory position in the stack is the number of arguments passed to the program.

The next _n_ memory positions in the stack point to strings somewhere in the stack.

The strings in the stack are cstrings: an array of ascii character values followed by a null byte.

### Output
Output is achieved with the **INP** and **CHP** instructions.

Both of these instructions will output the value of a single value in memory without a newline:
- **INP** will format the output as an integer
- **CHP** will format the output as a character

To print whole strings you will need to iterate over each character in the string.

## Logic
All logic operations are preformed on **ACC**.

To compare two values try subtracting them from one another and comparing that to zero.

You can jump to any line in your program, the jump can be specified by a tag or from some value in memory.

## Math
All mathematical operations are preformed on **ACC**

## Debugging
To debug a program, run risc.py with the `-d` or `--debug` flags, this will print out information about the state of the interperetation at each instruction.

To slowly step through the program, run risc.py with `-d` or `--debug` **AND** `-s` or `--step`.
