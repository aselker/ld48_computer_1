from blessed import Terminal


class NanoEditor:
    def __init__(self, n_lines=32, n_cols=40):
        self.cursor = (0, 0)
        self.contents = [[]]


box_names = [
    ["Puzzle 1", "Puzzle 2", "Puzzle 3", "Puzzle 4"],
    ["Asm 1", "Asm 2", "Asm 3", "Asm 4"],
    ["Ucode 1", "Ucode 2", "Ucode 3", "Ucode 4"],
]

term = Terminal()

while term.width < 120:
    print(term.home + term.clear)
    print(term.white_on_black("Please resize terminal to at least 120 columns."))
    _ = term.inkey(timeout=0.1)  # Probably better way to do this?
while term.height < 40:
    print(term.home + term.clear)
    print(term.white_on_black("Please resize terminal to at least 40 lines."))
    _ = term.inkey(timeout=0.1)  # Probably better way to do this?

print(term.home + term.clear)

"""
with term.cbreak(), term.hidden_cursor():
    inp = term.inkey()

print(term.move_down(2) + term.move_right(20))
print("You pressed " + term.bold(repr(inp)))
"""

assert not any([any([8 < len(name) for name in names]) for names in box_names])
selection = [0, 0]

while True:
    for y, names in enumerate(box_names):
        for x, name in enumerate(names):
            is_highlighted = [x,y] == selection
            box_color = term.black_on_white if is_highlighted else term.white_on_black
            print(term.move_xy(10 + 30 * x, 5 + 13 * y) + box_color(" " * 10))
            print(term.move_xy(10 + 30 * x, 6 + 13 * y) + box_color(" ") + term.white_on_black(name))
            print(term.move_xy(19 + 30 * x, 6 + 13 * y) + box_color(" "))
            print(term.move_xy(10 + 30 * x, 7 + 13 * y) + box_color(" " * 10))

    with term.cbreak(), term.hidden_cursor():
        inp = term.inkey()
    if inp.code == term.KEY_LEFT:
        if 0 < selection[0]:
            selection[0] -= 1
    elif inp.code == term.KEY_RIGHT:
        if selection[0] < 3:
            selection[0] += 1
    elif inp.code == term.KEY_UP:
        if 0 < selection[1]:
            selection[1] -= 1
    elif inp.code == term.KEY_DOWN:
        if selection[1] < 2:
            selection[1] += 1
    elif inp.code == term.KEY_ESCAPE:
        break


