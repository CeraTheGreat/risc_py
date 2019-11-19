import sys


# Registers:
#   ACC                 - Accumulator, this is where math and comparisons are
#                         preformed. Initialized to 0.
#
#   BAK                 - Backup register, just a place sto store extra values.
#                         Initialized to 0.
#
#   STP                 - Stack pointer, this is the current head of the stack
#
#   SFP                 - Stack frame pointer, this is the end of the stack frame
#
#   BSP                 - Stack frame base pointer, this is the begining of the
#                         stack frame.
#
# Placeholders:
#   <SRC>               - This is the value being acted upon. It may represent a
#                         hard-coded value, a register, or a location on the stack.
#
#   <DST>               - This is the location being acted upon. It may represent
#                         a register or a location on the stack.
#
# Instructions:
#   MOV <SRC> <DST>     - Move a value from <SRC> to <DST>. Will copy over the
#                         top element on the stack.
#
#   PSH <SRC>           - Push the value from <SRC> onto the stack. Will increase
#                         the size of the stack. Will increment stack pointer.
#
#   ADD <SRC>           - Add the value of <SRC> to ACC. Save the result in ACC
#
#   SUB <SRC>           - Subtract the value of <SRC> from ACC. Save the result 
#                         to ACC
#
#   CHP <SRC>           - Print the value of <SRC> as an ascii character.
#
#   INP <SRC>           - Print the value of <SRC> as an integer number.
#
#   POP                 - Remove the top value of the stack and discard it.
#                         Will decrement the stack pointer.
#
#   CLL <SRC>           - <SRC> should contain a pointer to a line in code to act
#                         as a function.
#
#   RET                 - Return to the previously calling function
#
#   JMP <SRC>           - Unconditionally jump to the line specified by <SRC>
#
#   JEZ <SRC>           - If ACC is equal to zero, jump to the line specified by
#                         <SRC>
#
#   JNZ <SRC>           - If ACC is not zero, jump to the line specified by <SRC>
#
#   JGZ <SRC>           - If ACC is greater than zero, jump to the line specified 
#                         by <SRC>
#
#   JLZ <SRC>           - If ACC is less than zero, jump to the line specified by
#                         <SRC>
#
#   HLT                 - Halt interperetation


# FLAGS
# Debug flag will show the state of memory at each cycle
DEBUG = False


# A simple stack class to make code more readable, self explanatory
class Stack:
    def __init__(self, elements=None): self.elements = elements if elements else []
    def push(self, element): self.elements.append(element)
    def pop(self): return self.elements.pop()
    def peek(self): return self.elements[-1]


class Interpereter:
    def __init__(self, instructions):
        # Controlls the continuation of the main interpereter loop, HLT will
        # set this false and stop the loop
        self.do_continue = True

        # The instruction list is simply a list of lists:
        #   - Each line
        #   - Each token on each line
        #
        # Parsing the instructions is a simple line break and split on spaces
        self.instruction_list = self.parse_instructions(instructions)

        # The instruction pointer keeps track of where we are in the code
        # Changing this pointer is how we preform a jump
        self.instruction_ptr = 0

        # The stack is an infinite* memory storage location where we can only
        # access memory on top of the stack, it makes big programs and concepts
        # like functions possible.
        #
        # * infinite really means as much physical memory as we have
        self.stack = Stack()

        # ACC, BAK, STP, SFP and BSP are the registers. They store integer values
        # ACC is where mathematic and comparison operations are preformed
        # BAK is a backup register for extra use
        # STP is where the current pointer to the head of the stack, -1 if empty
        # SFP is the head of the stack frame. This is where general use starts
        # BSP is the begining of the stack frame. This is how stack arguments are passed
        self.acc = 0
        self.bak = 0
        self.stp = -1
        self.fp  = 0
        self.bp = 0

        # A dictionary of instructions allows us to look up functions by keyword.
        # This is useful when we are parsing code because we don't need if else 
        # cases, just an index into a dictionary. Adding more functions is as
        # simple as writing it and adding it to the list.
        self.instructions = {
            "MOV":self._move,
            "PSH":self._push,
            "POP":self._pop,
            "ADD":self._add,
            "SUB":self._sub,
            "CLL":self._call,
            "RET":self._return,
            "CHP":self._char_print,
            "INP":self._int_print,
            "JMP":self._jmp,
            "JEZ":self._jez,
            "JNZ":self._jnz,
            "JGZ":self._jgz,
            "JLZ":self._jlz,
            "HLT":self._halt
        }

    # Take a textfile and turn it into an indexable list of instructions
    def parse_instructions(self, string):
        tags = {}
        instructions = []

        # Remove comments, tokenize lines
        instructions = [line[:line.find("'")].strip().split() if line.find("'") != -1 else line.strip().split() for line in string.splitlines()]

        # Locate tags
        for i,tokens in enumerate(instructions):
            #If we actually have tokens and the first token is a tag
            if tokens and tokens[0][-1] == ':':
                # Save name of tag with line it was found on
                tags[tokens[0][:-1]] = str(i)
                # Save remaining instructions without the tag
                tokens = tokens[1:]
            # Update instruction
            instructions[i] = tokens

        # Replace tags with line numbers
        for i,tokens in enumerate(instructions):
                # Replace jumps
                tokens = [tags[token] if token in tags else token for token in tokens]
                instructions[i] = tokens
        return instructions

    def params(self, parameters):
        self.stack.push(len(parameters))
        self.stp += 1

        if parameters:
            # Initialize argv array
            for parameter in parameters:
                self.stack.push(0)
                self.stp += 1

            # Fill argv pointer values
            for i,parameter in enumerate(parameters):
                # Set pointer to our variable
                self.stack.elements[i+1] = self.stp + 1
                for char in parameter:
                    self.stack.push(ord(char))
                    self.stp += 1
                # Push null terminator
                self.stack.push(0)
                self.stp += 1

        # Set registers accordingly
        self.bp = 0
        self.fp = self.stp

    # Preform interperetation
    def run(self):
        #The main interpereter loop
        while self.do_continue and self.instruction_ptr < len(self.instruction_list):


            #DEBUG -- Debug info on each cycle.
            if DEBUG:
                #STEP -- Wait for user to step each cycle
                #if STEP and readchar.readchar() == 'q': self.do_continue = False
                #STEP uses the readchar module, do or don't it's not required
                print('')
                print("------------")
                print("stack: {}".format(self.stack.elements))
                print("ip   : {}".format(self.instruction_ptr))
                print("sbp   : {}".format(self.bp))
                print("sfp   : {}".format(self.fp))
                print("acc  : {}".format(self.acc))
                print("bak  : {}".format(self.bak))
                print("stp  : {}".format(self.stp))
                print("ins  : {}".format(self.instruction_list[self.instruction_ptr]))
                print("------------")
            #DEBUG

            # The instruction which is currently being pointed to
            instruction = self.instruction_list[self.instruction_ptr]

            # If empty line, don't run a command
            if instruction == []:
                self.instruction_ptr += 1
                continue

            # The opcode of the current instruction
            #   - MOV, PSH, POP etc...
            #
            # The opcode is always the first element of the instruction
            opcode = instruction[0]

            # Index into the instructions dictionary and call it with the
            # remaining pieces of the instruction tokens
            #
            # *instruction[1:] is special
            #   > This takes all the tokens except for the first one
            #   > If there are no other tokens, it returns an empty list
            #   > The * ('splat') operator takes the list and passes each element
            #     as an argument to the function
            #   > if * recieves an empty list, it passes nothing
            #
            # Because the *instruction[1:] is so special, we don't have to write
            # any special code to handle instructions with varying argument length
            self.instructions[opcode](*instruction[1:])

            # Increment the instruction pointer to the next instruction
            self.instruction_ptr += 1

    # Push the instruction pointer onto the stack
    # Push the previous base function pointer to the stack
    # Push the previous function pointer to the stack
    # Take argument pointers
    # Increment stack ptr +3
    # Set the function pointer to STP - 1
    # Set the instruction pointer to <SRC>
    def _call(self, src, argc=None):
        old_bp = self.bp
        self.bp = self.stp + 1
        self.stack.push(self.instruction_ptr)
        self.stack.push(old_bp)
        self.stack.push(self.fp)
        if argc:
            argc = self._get_src(argc)
            for i in range(self.stp - (argc - 1), self.stp + 1):
                self.stack.push(self.stack.elements[i])
                self.stp += 1
        self.stp += 3
        self.fp = self.stp 
        self.instruction_ptr = self._get_src(src) - 1

    # Set instruction pointer to value at function pointer + 1
    # Set the stack pointer to function pointer - 1
    # Set the function pointer to the value at function pointer
    # Trim stack
    def _return(self):
        old_bp = self.bp
        self.instruction_ptr = self.stack.elements[self.bp]
        self.fp = self.stack.elements[self.bp + 2]
        self.stp = self.bp - 1
        self.bp = self.stack.elements[self.bp + 1]
        self.stack.elements = self.stack.elements[:old_bp]

    # Get the appropriate integer value for the specified source
    def _get_src(self, src):
        if src == 'ACC':
            return self.acc
        elif src == 'BAK':
            return self.bak
        elif src == 'STP':
            return self.stp
        elif src == 'SFP':
            return self.fp
        elif src == 'BSP':
            return self.bp
        elif src[0] =='[' and src[-1] ==']':
            return self.stack.elements[self._get_src(src[1:-1])]
        else:
            # If it wasn't a register or the stack, assume it is an integer
            return int(src)

    # Generally set the destination to the provided value
    def _set_dest(self, value, dest):
        if dest == 'ACC':
            self.acc = value
        elif dest == 'BAK':
            self.bak = value
        elif dest[0] == '[' and dest[-1] == ']':
            self.stack.elements[self._get_src(dest[1:-1])] = value

    # The only instruction with the DST argument
    # Overwrites the specified location with the provided value
    def _move(self, src, dest):
        self._set_dest(self._get_src(src), dest)

    # Pushes the specified value to the stack, does not overwrite
    def _push(self, src):
        self.stack.push(self._get_src(src))
        self.stp += 1

    # Removes the top value on the stack
    def _pop(self):
        self.stack.pop()
        self.stp -= 1

    # Adds the specified value to acc
    def _add(self, src):
        self.acc += self._get_src(src)

    # Subtracts the specified value from acc
    def _sub(self, src):
        self.acc -= self._get_src(src)

    # Print the specified value as a char
    def _char_print(self, src):
        print(chr(self._get_src(src)), end='')

    # Print the specified value as an integer
    def _int_print(self, src):
        print(int(self._get_src(src)), end='')

    # Unconditionally jump to specified location
    def _jmp(self, src):
        self.instruction_ptr = self._get_src(src) - 1

    # If acc equals zero, jump to specified location
    def _jez(self, src):
        if self.acc == 0:
            self.instruction_ptr = self._get_src(src) - 1

    # If acc does not equal zero, jump to specified location
    def _jnz(self, src):
        if self.acc != 0:
            self.instruction_ptr = self._get_src(src) - 1

    # If acc is greater than zero, jump to specified location
    def _jgz(self, src):
        if self.acc > 0:
            self.instruction_ptr = self._get_src(src) - 1

    # If acc is less than zero, jump to specified location
    def _jlz(self, src):
        if self.acc < 0:
            self.instruction_ptr = self._get_src(src) - 1

    # Halt program interperetation
    def _halt(self):
        self.do_continue = False


# Setup for interperetation
def main():
    if len(sys.argv) < 2: 
        print("usage: python risc.py <instruction_file>")
        sys.exit()
    program_filename = sys.argv[1]
    with open(program_filename,'r') as program_file:
        program = program_file.read()
    interpereter = Interpereter(program)
    interpereter.params(sys.argv[2:])
    interpereter.run()


if __name__ == '__main__':
    main()
