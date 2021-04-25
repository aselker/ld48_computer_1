ucode_ref_sheet = """Commands:
buf (1 arg): Return arg unmodified
not (1 arg): Invert arg
and (2 arg): 1 only if both args are 1
nand(2 arg): Inverted and
or  (2 arg): 1 if either arg is 1
nor (2 arg): Inverted or
xor (2 arg): 1 if exactly one arg is 1
xnor (2 arg): Inverted xor"""


class UCode:
    @classmethod
    def parse(cls, lines):
        insts = []
        for line in lines:
            if type(line) is list:
                line = "".join(line)

            line = line.rstrip()

            # Blank line -> blank instruction
            if line == "":
                insts.append([])
                continue

            words = line.lower().split(" ")

            # Prelim len check, rm equal sign
            if len(words) < 4 or words[1] != "=":
                insts.append(None)
                continue
            del(words[1])

            # Check number of arguments
            num_args = {
                "buf": 1,
                "not": 1,
                "and": 2,
                "or": 2,
                "nand": 2,
                "nor": 2,
                "xor": 2,
                "xnor": 2,
                "if": 3,}
            if len(words) != num_args.get(words[1], -999) + 2:
                insts.append(None)
                continue

            # Check reg names
            ok = True
            for i, name in enumerate([words[0]] + words[2:]):
                if len(name) < 2 or 3 < len(name) or not name[1:].isdigit():
                    ok = False
                    break

                # Can't write to input regs
                if i==0 and name[0] in ["c", "i", "a"]:
                    ok = False
                    break

                # Check index numbers
                if name[0] in ["c"]:
                    if int(name[1:]) not in [0, 1]:
                        ok = False
                        break
                elif name[0] in ["u", "o", "a", "j"]:
                    if int(name[1:]) < 1 or 6 < int(name[1:]) :
                        ok = False
                        break
                elif name[0] in ["i"]:
                    if int(name[1:]) < 1 or 12 < int(name[1:]) :
                        ok = False
                        break
                else:
                    ok = False
                    break
            if ok:
                insts.append(words)
            else:
                insts.append(None)
                continue


        return insts



    def __init__(self, insts):
        self.insts = insts
        self.user_regs = [False] * 6
        self.output_regs = [False] * 6
        self.jump_regs = [False] * 6


    def get_reg(self, name):
        bank = name[0]
        index = int(name[1:]) - 1
        if bank == "u":
            return self.user_regs[index]
        elif bank == "c":
            return bool(index+1)
        elif bank == "i":
            return self.input_regs[index]
        elif bank == "o":
            return self.output_regs[index]
        elif bank == "a":
            return self.addr_regs[index]
        elif bank == "j":
            return self.jump_regs[index]

    def set_reg(self, name, value):
        bank = name[0]
        index = int(name[1:]) - 1
        if bank == "u":
            self.user_regs[index] = value
        elif bank == "c":
            pass
        elif bank == "i":
            self.input_regs[index] = value
        elif bank == "o":
            self.output_regs[index] = value
        elif bank == "a":
            self.addr_regs[index] = value
        elif bank == "j":
            self.jump_regs[index] = value

    def run_single_instruction(self, inst):
        if not inst:
            return

        args = [self.get_reg(arg) for arg in inst[2:]] + [False]*3 # Buffer for unused

        self.set_reg(
            inst[0],
            {
                "buf": args[0],
                "not": args[0],
                "and": args[0] and args[1],
                "or": args[0] or args[1],
                "nand": not (args[0] and args[1]),
                "nor": not (args[0] or args[1]),
                "xor": (args[0] and not args[1]) or (not args[0] and args[1]),
                "xnor": (args[0] and args[1]) or (not args[0] and not args[1]),
                "if": args[1] if args[0] else args[2],
            }[inst[1]],
        )

    def run(self, input1, input2, addr):
        assert len(input1) == 6 and len(input2) == 6
        self.input_regs = input1 + input2
        self.addr_regs = addr

        for inst in self.insts:
            self.run_single_instruction(inst)

        return self.user_regs, self.output_regs, self.jump_regs
