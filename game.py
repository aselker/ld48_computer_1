import os
from blessed import Terminal

from asm_editor import AsmEditor
from puzzle_list import PuzzleList

class OverviewScreen:
    """
    TODO: What is this actually for?
    """

    def __init__(self, term):
        self.term = term

        self.box_names = [
            ["Puzzle 1", "Puzzle 2", "Puzzle 3", "Puzzle 4"],
            ["Asm 1", "Asm 2", "Asm 3", "Asm 4"],
            ["Ucode 1", "Ucode 2", "Ucode 3", "Ucode 4"],
        ]

        assert not any([any([8 < len(name) for name in names]) for names in self.box_names])
        self.cursor = [0, 0]

    def draw(self):
        # TODO: Overwrite the whole screen
        for y, names in enumerate(self.box_names):
            for x, name in enumerate(names):
                is_highlighted = [x, y] == self.cursor
                box_color = self.term.black_on_white if is_highlighted else self.term.white_on_black
                print(self.term.move_xy(10 + 30 * x, 5 + 13 * y) + box_color(" " * 10))
                print(
                    self.term.move_xy(10 + 30 * x, 6 + 13 * y)
                    + box_color(" ")
                    + self.term.white_on_black(name)
                )
                print(self.term.move_xy(19 + 30 * x, 6 + 13 * y) + box_color(" "))
                print(self.term.move_xy(10 + 30 * x, 7 + 13 * y) + box_color(" " * 10))

    def keypress(self, inp):
        if inp.code == self.term.KEY_LEFT:
            if 0 < self.cursor[0]:
                self.cursor[0] -= 1
        elif inp.code == self.term.KEY_RIGHT:
            if self.cursor[0] < 3:
                self.cursor[0] += 1
        elif inp.code == self.term.KEY_UP:
            if 0 < self.cursor[1]:
                self.cursor[1] -= 1
        elif inp.code == self.term.KEY_DOWN:
            if self.cursor[1] < 2:
                self.cursor[1] += 1

        self.draw()

term = Terminal()
esc_delay = 0.05

while term.width < 100:
    print(term.home + term.clear)
    print(term.white_on_black("Please resize terminal to at least 100 columns."))
    _ = term.inkey(timeout=0.1)  # Probably better way to do this?
while term.height < 40:
    print(term.home + term.clear)
    print(term.white_on_black("Please resize terminal to at least 40 lines."))
    _ = term.inkey(timeout=0.1)  # Probably better way to do this?

print(term.home + term.clear)

# editor = AsmEditor(term, esc_delay)
editor = PuzzleList(term, esc_delay)
editor.draw()
while True:
    with term.cbreak(), term.hidden_cursor():
        inp = term.inkey(esc_delay=esc_delay)
        if not editor.keypress(inp):
            print(term.clear)
            break
