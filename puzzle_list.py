from info_screen import InfoScreen
from nano_editor import NanoEditor, outline_editor
from asm_editor import AsmEditor

# A puzzle is a list of [title, description, inputs, outputs]
puzzles = [
    ["COUNT TO 10", "Output numbers from 1 to 10 in order", [[]], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],],
    [
        "POWER OF 2",
        "For each input, output the nth power of 2",
        [[5, 4, 3, 2, 1, 0], [3, 1, 4, 5, 2, 3, 5, 0]],
        [[1, 2, 4, 8, 16, 32], [8, 2, 16, 32, 4, 8, 32, 1]],
    ],
    [
        "SUM",
        "Sum together sets of inputs terminated by\n0s, output the sums",
        [[0, 4, 6, 2, 0, 5, 9, 0, 1], [0, 19, 17, 20, 0, 13, 3, 8, 6, 0, 14, 0, 4]],
        [[12, 14, 1], [56, 30, 14, 4]],
    ],
    [
        "MOD 8",
        "For each input, output its remainder when\ndivided by 8",
        [[0, 1, 2, 4, 8, 12, 15], [43, 53, 2, 4, 1, 39, 28]],
        [[7, 4, 0, 4, 2, 1, 0], [3, 5, 2, 4, 1, 7, 4]],
    ],
    [
        "SQUARE",
        "For each input, square it and output the\nresult",
        [[7, 6, 5, 4, 3, 2, 1], [4, 1, 3, 5, 2]],
        [[1, 4, 9, 16, 25, 36, 49], [4, 25, 9, 1, 16]],
    ],
    [
        "SORT",
        "Given exactly 10 unique inputs, output\nthem sorted",
        [[3, 1, 4, 5, 9, 2, 6, 8, 7, 0], [39, 48, 0, 63, 29, 23, 47, 8, 25, 61]],
        [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 8, 23, 25, 29, 39, 47, 48, 61, 63]],
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
        for i in range(6):
            x = 1 + (i % 3) * 25
            y = 6 + (2 < i) * 5
            editor = NanoEditor(self.term, (x, y), (20, 1))
            editor.is_focused = False
            editor.contents = puzzles[i][0]
            editor.contents = [list(editor.contents)]

            self.puzzle_buttons.append(editor)

        self.info_screen = InfoScreen(self.term)
        self.asm_sub_editors = [AsmEditor(self.term, esc_delay, puzzles[i]) for i in range(6)]

        self.cursor = [0, 0]
        self.is_editing = False

    def draw(self):
        print(self.term.clear)

        is_highlighted = self.cursor[1]==0
        outline_color = self.term.black_on_green if is_highlighted else self.term.green_on_black
        # outline_color = self.term.white_on_black
        outline_editor(self.term, self.info_button, "DEEPER BROS. (R) DIGITAL COMPUTER v0.23", outline_color)
        self.info_button.draw()

        for i, button in enumerate(self.puzzle_buttons):
            title = "PROGRAM " + str(i + 1)
            is_highlighted = (self.cursor[1] * 3) + self.cursor[0] == i+3
            outline_color = self.term.black_on_green if is_highlighted else self.term.green_on_black
            outline_editor(self.term, button, title, color=outline_color)
            button.draw()

    def keypress(self, inp):
        do_draw = True
        if self.is_editing:
            if self.cursor[1] == 0:
                self.is_editing = self.info_screen.keypress(inp)
            else:
                self.is_editing = self.asm_sub_editors[(self.cursor[1] * 3) + self.cursor[0] - 3].keypress(inp)
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
                    self.asm_sub_editors[(self.cursor[1] * 3) + self.cursor[0] - 3].draw()
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
                if self.cursor[1] < 2:
                    self.cursor[1] += 1

        if do_draw:
            self.draw()
        return True
