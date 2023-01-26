from ucode import UCode

insts = UCode.parse(
    [
        "o1 = buf i10",
        "o2 = buf i2",
        "o3 = and i3 i4",
    ]
)
print(insts)

input1 = [True, False, True, False, False, False]
input2 = input1.copy()  # laaazy
addr = input1.copy()  # lol

ucode = UCode(insts)
print(ucode.run(input1, input2, addr))
