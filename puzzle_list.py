from info_screen import InfoScreen
from nano_editor import NanoEditor, outline_editor
from asm_editor import AsmEditor

# A puzzle is a list of [title, description, inputs, outputs]
puzzles = [
    [
        "COUNT TO 10",
        "Output numbers from 1 to 10 in order",
        [[]],
        [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],
    ],
    [
        "POWER OF 2",
        "For each input, output the nth power of 2",
        [[5, 4, 3, 2, 1, 0], [3, 1, 4, 0, 2, 3, 5, 0]],
        [[1, 2, 4, 8, 16, 32], [1, 32, 8, 4, 1, 16, 2, 8]],
    ],
    [
        "SUM",
        "Sum together sets of inputs terminated by\n0s, output the sums",
        [[0, 4, 6, 2, 0, 5, 9, 0, 1], [0, 19, 17, 20, 0, 13, 3, 8, 6, 0, 14, 0, 4]],
        [[1, 14, 12], [4, 14, 30, 56]],
    ],
    [
        "MOD 8",
        "For each input, output its remainder when\ndivided by 8",
        [[0, 1, 2, 4, 8, 12, 15], [43, 53, 2, 4, 1, 39, 28]],
        [[7, 4, 0, 4, 2, 1, 0], [4, 7, 1, 4, 2, 5, 3]],
    ],
    [
        "SQUARE",
        "For each input, square it and output the\nresult",
        [[7, 6, 5, 4, 3, 2, 1], [4, 1, 3, 5, 2]],
        [[1, 4, 9, 16, 25, 36, 49], [4, 25, 9, 1, 16]],
    ],
    [
        "COMPARE",
        "For each pair of inputs, output 1 if the\nsecond is greater, and 0 otherwise",
        [[14, 23, 25, 21, 27, 27, 19, 37, 28, 16], [56, 35, 56, 21, 30, 36, 11, 11]],
        [[1, 0, 0, 1, 0], [0, 0, 1, 1]],
    ],
    [
        "MOD",
        "For each pair of inputs, output the\nremainder when the second is divided by\nthe first.",
        [[26, 12, 63, 17, 8, 10, 8, 2], [30, 11, 8, 1, 1, 9]],
        [[0, 8, 12, 2], [1, 0, 8]],
    ],
    [
        "SORT",
        "Given unique inputs less than 10, output\nthem sorted in increasing order.",
        [[3, 1, 4, 5, 9, 2, 6, 8, 7, 0], [1, 7, 9, 4, 3, 5, 6, 0]],
        [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 3, 4, 5, 7, 9]],
    ],
    [
        "PRIME",
        "For each input, output 1 if it is prime,\nand 0 otherwise.  Inputs will all be 2 or\nmore.",
        [[10, 9, 8, 7, 6, 5, 4, 3, 2], [21, 19, 18, 17, 15, 14, 13, 12]],
        [[1, 1, 0, 1, 0, 1, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1, 0]],
    ],
]


class PuzzleList:
    def __init__(self, term, esc_delay):
        self.term = term
        self.esc_delay = esc_delay

        self.info_button = NanoEditor(self.term, (8, 1), (54, 1))
        self.info_button.is_focused = False
        self.info_button.contents = "Info + programming instructions"
        # self.info_button.contents = "Please see manual for instructions"
        self.info_button.contents = [list(self.info_button.contents)]

        self.puzzle_buttons = []
        for i in range(9):
            x = 1 + (i % 3) * 25
            y = 6 + (int(i / 3)) * 5
            editor = NanoEditor(self.term, (x, y), (20, 1))
            editor.is_focused = False
            editor.contents = puzzles[i][0]
            editor.contents = [list(editor.contents)]

            self.puzzle_buttons.append(editor)

        self.info_screen = InfoScreen(self.term)
        self.asm_sub_editors = [
            AsmEditor(self.term, esc_delay, puzzles[i]) for i in range(len(puzzles))
        ]

        self.cursor = [0, 0]
        self.is_editing = False

    def draw(self):
        print(self.term.clear)

        is_highlighted = self.cursor[1] == 0
        outline_color = (
            self.term.black_on_green if is_highlighted else self.term.green_on_black
        )
        # outline_color = self.term.white_on_black
        outline_editor(
            self.term,
            self.info_button,
            "DEEPER BROS. (R) DIGITAL COMPUTER v0.23",
            outline_color,
        )
        self.info_button.draw()

        for i, button in enumerate(self.puzzle_buttons):
            title = "PROGRAM " + str(i + 1)
            is_highlighted = (self.cursor[1] * 3) + self.cursor[0] == i + 3
            outline_color = (
                self.term.black_on_green if is_highlighted else self.term.green_on_black
            )
            outline_editor(self.term, button, title, color=outline_color)
            button.draw()

    def keypress(self, inp):
        do_draw = True
        if self.is_editing:
            if self.cursor[1] == 0:
                self.is_editing = self.info_screen.keypress(inp)
            else:
                self.is_editing = self.asm_sub_editors[
                    (self.cursor[1] * 3) + self.cursor[0] - 3
                ].keypress(inp)
            do_draw = not self.is_editing
        else:
            if inp.code == self.term.KEY_ESCAPE:
                return False
            elif inp.code == self.term.KEY_ENTER:
                self.is_editing = True
                if self.cursor[1] == 0:
                    self.info_screen.draw()
                    do_draw = False
                else:
                    self.asm_sub_editors[
                        (self.cursor[1] * 3) + self.cursor[0] - 3
                    ].draw()
                    do_draw = False
            elif inp.code == self.term.KEY_LEFT:
                if 0 < self.cursor[0] and self.cursor[1] != 0:
                    self.cursor[0] -= 1
            elif inp.code == self.term.KEY_RIGHT:
                if self.cursor[0] < 2 and self.cursor[1] != 0:
                    self.cursor[0] += 1
            elif inp.code == self.term.KEY_UP:
                if 0 < self.cursor[1]:
                    self.cursor[1] -= 1
            elif inp.code == self.term.KEY_DOWN:
                if self.cursor[1] < 3:
                    self.cursor[1] += 1

        if do_draw:
            self.draw()
        return True
