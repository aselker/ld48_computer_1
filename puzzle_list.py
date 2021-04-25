from nano_editor import NanoEditor, outline_editor
from asm_editor import AsmEditor

# A puzzle is a list of [title, description, inputs, outputs]
puzzles = [
    ["COUNT TO 10", "Put numbers from 1 to 10 into the output", [[]], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],],
    [
        "SQUARE",
        "Square the incoming numbers",
        [[1, 2, 3, 4, 5, 6, 7], [2, 5, 3, 1, 4]],
        [[1, 4, 9, 16, 25, 36, 49], [4, 25, 9, 1, 16]],
    ],
] * 3


class PuzzleList:
    def __init__(self, term, esc_delay):
        self.term = term
        self.esc_delay = esc_delay

        self.puzzle_buttons = []
        for i in range(6):
            x = 1 + (i % 3) * 25
            y = 1 + (2 < i) * 5
            editor = NanoEditor(self.term, (x, y), (20, 1))
            editor.is_focused = False
            editor.contents = puzzles[i][0]
            editor.contents = [list(editor.contents)]

            self.puzzle_buttons.append(editor)

        self.asm_sub_editors = [AsmEditor(self.term, esc_delay, puzzles[i]) for i in range(6)]

        self.cursor = [0, 0]
        self.is_editing = False

    def draw(self):
        print(self.term.clear)

        for i, button in enumerate(self.puzzle_buttons):
            title = "PUZZLE " + str(i + 1)
            is_highlighted = (self.cursor[1] * 3) + self.cursor[0] == i
            outline_color = self.term.black_on_green if is_highlighted else self.term.green_on_black
            outline_editor(self.term, button, title, color=outline_color)
            button.draw()

    def keypress(self, inp):
        do_draw = True
        if self.is_editing:
            self.is_editing = self.asm_sub_editors[(self.cursor[1] * 3) + self.cursor[0]].keypress(inp)
            do_draw = not self.is_editing
        else:
            if inp.code == self.term.KEY_ESCAPE:
                return False
            elif inp.code == self.term.KEY_ENTER:
                self.is_editing = True
                self.asm_sub_editors[(self.cursor[1] * 3) + self.cursor[0]].draw()
                do_draw = False

            elif inp.code == self.term.KEY_LEFT:
                if 0 < self.cursor[0]:
                    self.cursor[0] -= 1
            elif inp.code == self.term.KEY_RIGHT:
                if self.cursor[0] < 2:
                    self.cursor[0] += 1
            elif inp.code == self.term.KEY_UP:
                if 0 < self.cursor[1]:
                    self.cursor[1] -= 1
            elif inp.code == self.term.KEY_DOWN:
                if self.cursor[1] < 1:
                    self.cursor[1] += 1

        if do_draw:
            self.draw()
        return True
