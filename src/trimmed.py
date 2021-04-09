import sys


class Interpereter:
    def __init__(self, instructions):
        self.do_continue = True
        self.instruction_list = list(self._parse_instructions(instructions))
        self.instruction_ptr = 0
        self.stack = []
        self.acc = 0
        self.bak = 0
        self.instructions = {
            "MOV":self._move,
            "PSH":self._push,
            "POP":self._pop,
            "ADD":self._add,
            "SUB":self._sub,
            "CHP":self._char_print,
            "INP":self._int_print,
            "JMP":self._jmp,
            "JEZ":self._jez,
            "JNZ":self._jnz,
            "JGZ":self._jgz,
            "JLZ":self._jlz,
            "HLT":self._halt
        }

    def run(self):
        while self.do_continue and self.instruction_ptr < len(self.instruction_list):
            instruction = self.instruction_list[self.instruction_ptr]
            opcode = instruction[0]
            self.instructions[opcode](*instruction[1:])
            self.instruction_ptr += 1

    def _parse_instructions(self, instructions):
        for line in instructions.splitlines():
            yield line.split()

    def _get_src(self, src):
        if src == 'ACC': return self.acc
        elif src == 'BAK': return self.bak
        elif src == 'STK': return self.stack[-1]
        else: return int(src)

    def _move(self, src, dest):
        if dest == 'ACC': self.acc = self._get_src(src)
        elif dest == 'BAK': self.bak = self._get_src(src)
        elif dest == 'STK': self.stack[-1] = self._get_src(src)

    def _push(self, src):
        self.stack.append(self._get_src(src))

    def _pop(self):
        self.stack.pop()

    def _add(self, src):
        self.acc += self._get_src(src)

    def _sub(self, src):
        self.acc -= self._get_src(src)

    def _char_print(self, src):
        print(chr(self._get_src(src)), end='')

    def _int_print(self, src):
        print(int(self._get_src(src)), end='')

    def _jmp(self, src):
        self.instruction_ptr = self._get_src(src) - 2

    def _jez(self, src):
        if self.acc == 0:
            self.instruction_ptr = self._get_src(src) - 2

    def _jnz(self, src):
        if self.acc != 0:
            self.instruction_ptr = self._get_src(src) - 2

    def _jgz(self, src):
        if self.acc > 0:
            self.instruction_ptr = self._get_src(src) - 2

    def _jlz(self, src):
        if self.acc < 0:
            self.instruction_ptr = self._get_src(src) - 2

    def _halt(self):
        self.do_continue = False


def main():
    with open(sys.argv[1],'r') as program_file:
        program = program_file.read()
    interpereter = Interpereter(program)
    interpereter.run()


if __name__ == "__main__":
    main()

