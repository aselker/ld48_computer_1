from uint import Uint6, UintN

asm_ref_sheet="""Commands:
add:     return sum of inputs
sub:     return difference of inputs
jmp:     jump to line no. by first input
jmpzero: jmp, if second input is 0
push:    push first input onto stack
pop:     remove top of stack, return it
swap:    swap top two stack entries
output:  send first input to OUTPUT
cust1:   run first custom assembly cmd
cust2:   run second custom assembly cmd
cust3:   run third custom assembly cmd"""

def cmd_add(asm):
    return asm.pipe1 + asm.pipe2, None


def cmd_sub(asm):
    return asm.pipe1 - asm.pipe2, None


def cmd_jmp(asm):
    return 0, asm.pipe1


def cmd_jmpzero(asm):
    if asm.pipe2 == 0:
        return 0, asm.pipe1
    else:
        return 0, None


def cmd_push(asm):
    asm.stack.append(asm.pipe1)
    return 0, None


def cmd_pop(asm):
    if len(asm.stack) == 0:
        return 0, None
    return asm.stack.pop(), None


def cmd_swap(asm):
    first = cmd_pop(asm)
    second = cmd_pop(asm)
    asm.stack.append(second)
    asm.stack.append(first)
    return 0, None


def cmd_output(asm):
    asm.output(asm.pipe1)
    return 0, None


def run_ucode_as_cmd(asm, ucode):
    input1 = Uint6(asm.pipe1).bits()
    input2 = Uint6(asm.pipe2).bits()
    addr = Uint6(asm.pc).bits()
    _, output, jump = ucode.run(input1, input2, addr)
    output = UintN.from_bits(output).number
    jump = UintN.from_bits(jump).number
    return output, jump


def cmd_cust1(asm):
    return run_ucode_as_cmd(asm, asm.ucodes[0])


def cmd_cust2(asm):
    return run_ucode_as_cmd(asm, asm.ucodes[1])


def cmd_cust3(asm):
    return run_ucode_as_cmd(asm, asm.ucodes[2])


commands = {
    "add": cmd_add,
    "sub": cmd_sub,
    "jmp": cmd_jmp,
    "jmpzero": cmd_jmpzero,
    "push": cmd_push,
    "pop": cmd_pop,
    "swap": cmd_swap,
    "output": cmd_output,
    "cust1": cmd_cust1,
    "cust2": cmd_cust2,
    "cust3": cmd_cust3,
}


def make_literal_fn(literal):
    def fn(asm):
        return literal, None

    return fn


class Asm:
    @classmethod
    def parse(cls, lines):
        cmds = []
        for line in lines:
            if type(line) is list:
                line = "".join(line)

            line = line.rstrip()

            # Blank line -> blank cmd
            if line == "":
                cmds.append([])
                continue

            subcmds = line.lower().split("|")

            ok = True
            new_subcmds = []
            for subcmd in subcmds:
                words = subcmd.strip().split(" ")
                if len(words) not in [1, 2]:
                    ok = False
                    break

                # Validate each word
                ok2 = True
                new_words = []
                for word in words:
                    if word.isdigit():
                        literal = int(word)
                        if 0 <= literal and literal < 2 ** 6:
                            new_words.append(make_literal_fn(literal))
                        else:
                            ok2 = False
                            break
                    elif word not in commands:
                        ok2 = False
                        break
                    else:
                        new_words.append(commands[word])
                if not ok2:
                    ok = False
                    break

                new_subcmds.append(new_words)

            if ok:
                cmds.append(new_subcmds)
            else:
                cmds.append(None)

        return cmds

    def __init__(self, cmds, ucodes, num_lines):
        self.cmds = cmds
        self.ucodes = ucodes
        self.num_lines = num_lines

        self.stack = []
        self.pc = 0

    def output(self, val):
        self.output_callback(self, val)

    def step(self):
        cmd = self.cmds[self.pc]
        self.pipe1 = 0
        self.pipe2 = 0
        next_pc = self.pc + 1

        for subcmd in cmd:
            next_pipe1, jump_addr_1 = subcmd[0](self)
            if len(subcmd) == 2:
                next_pipe2, jump_addr_2 = subcmd[1](self)
            else:
                next_pipe2, jump_addr_2 = 0, None

            self.pipe1 = next_pipe1 % 64
            self.pipe2 = next_pipe2 % 64

            if jump_addr_1 is not None:
                next_pc = jump_addr_1

            if jump_addr_2 is not None:
                next_pc = jump_addr_2

        if self.num_lines <= next_pc:
            self.pc = 0
            return False

        self.pc = next_pc
        return True

    def run(self):
        while self.step():
            pass


if __name__ == "__main__":
    cmds = Asm.parse(["1 1 | add | push", "pop 2 | add | jmp", "3 | push", "5 | push",])
    print("Cmds:", cmds)

    asm = Asm(cmds, [])
    asm.run()
    print("Stack:", asm.stack)
