class UCode:
    @classmethod
    def split_insts(cls, string):
        insts = [inst.split(" ") for inst in string.split("\n")]
        for inst in insts:
            del inst[1] # Equal sign
            if len(inst) == 3:
                inst.append("")
        return insts

    def __init__(self, insts):
        self.user_regs = [False] * 6
        self.output_regs = [False] * 12
        self.jump_regs = [False] * 6

        self.insts = insts

    def get_reg(self, name):
        bank = name[0]
        index = int(name[1]) - 1
        if bank == "r":
            return self.user_regs[index]
        elif bank == "c":
            return bool(index)
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
        index = int(name[1]) - 1
        if bank == "r":
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
        arg1 = self.get_reg(inst[2])
        arg2 = self.get_reg(inst[3]) if inst[3] else False

        self.set_reg(
            inst[0],
            {
                "buf": arg1,
                "not": arg1,
                "and": arg1 and arg2,
                "or": arg1 or arg2,
                "nand": not (arg1 and arg2),
                "nor": not (arg1 or arg2),
                "xor": (arg1 and not arg2) or (not arg1 and arg2),
                "xnor": (arg1 and arg2) or (not arg1 and not arg2),
            }[inst[1]],
        )

    def run(self, input1, input2, addr):
        assert len(input1) == 6 and len(input2) == 6
        self.input_regs = input1 + input2
        self.addr_regs = addr

        for inst in self.insts:
            self.run_single_instruction(inst)

        return self.output_regs, self.jump_regs
