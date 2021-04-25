from nano_editor import NanoEditor, outline_editor, chars_to_bools, bools_to_chars
from ucode import UCode

class UcodeEditor:
    def __init__(self, term):
        self.term = term

        CODE_WIDTH = 26

        self.code_editor = NanoEditor(term, (1, 1), (CODE_WIDTH, 32))
        self.code_editor.edit_callback = self._evaluate
        self.code_editor.is_focused = False

        self.reg_editors = [None] * 6
        for i in range(6):
            x = CODE_WIDTH + 4
            y = 1 + 4 * i + (0 if i < 3 else 2)
            editor = NanoEditor(term, (x, y), (6, 1))
            editor.edit_callback = self._evaluate
            editor.is_focused = False

            editor.contents = [list("000000")]

            self.reg_editors[i] = editor

        self.ucode = UCode([])
        self.cursor = [0, 0]
        self.is_editing = False

    def _evaluate(self):
        # TODO: Check if inputs have only 1's and 0's
        insts = UCode.parse(self.code_editor.contents)
        self.code_editor.highlighted_lines = [i for i, inst in enumerate(insts) if inst is None]
        if len(self.code_editor.highlighted_lines) == 0:
            input1 = chars_to_bools(self.reg_editors[0].contents[0])
            input2 = chars_to_bools(self.reg_editors[1].contents[0])
            addr = chars_to_bools(self.reg_editors[2].contents[0])

            self.ucode = UCode(insts)
            user, output, jump = self.ucode.run(input1, input2, addr)
            self.reg_editors[3].contents = [bools_to_chars(user)]
            self.reg_editors[4].contents = [bools_to_chars(output)]
            self.reg_editors[5].contents = [bools_to_chars(jump)]

            self.draw()

    def draw(self):
        # Clear the screen
        # TODO: Remove this for prettiness
        print(self.term.clear)

        if self.is_editing:
            outline_color = self.term.black_on_white if (self.cursor[0] == 0) else self.term.white_on_black
        else:
            outline_color = self.term.black_on_green if (self.cursor[0] == 0) else self.term.green_on_black
        outline_editor(self.term, self.code_editor, title="MICROCODE", color=outline_color)

        self.code_editor.draw()

        for i, editor, title in zip(
            range(len(self.reg_editors)),
            self.reg_editors,
            ["INPUT1", "INPUT2", "ADDR", "USER", "OUTPUT", "JUMP",],
        ):
            if self.is_editing or i in [3, 4, 5]:
                outline_color = (
                    self.term.black_on_white if (self.cursor == [1, i]) else self.term.white_on_black
                )
            else:
                outline_color = (
                    self.term.black_on_green if (self.cursor == [1, i]) else self.term.green_on_black
                )
            outline_editor(self.term, editor, title=title, color=outline_color)
            editor.draw()

    @property
    def _highlighted_editor(self):
        if self.cursor[0] == 0:
            return self.code_editor
        else:
            return self.reg_editors[self.cursor[1]]

    def keypress(self, inp):
        if self.is_editing:
            if inp.code == self.term.KEY_ESCAPE:
                self.is_editing = False
                self._highlighted_editor.is_focused = False
            else:
                self._highlighted_editor.keypress(inp)
        else:
            if inp.code == self.term.KEY_ESCAPE:
                return False
            elif inp.code == self.term.KEY_ENTER:
                self.is_editing = True
                self._highlighted_editor.is_focused = True
            elif inp.code == self.term.KEY_LEFT:
                if 0 < self.cursor[0]:
                    self.cursor[0] -= 1
            elif inp.code == self.term.KEY_RIGHT:
                if self.cursor[0] < 1:
                    self.cursor[0] += 1
                print(self.cursor)
            elif inp.code == self.term.KEY_UP:
                if 0 < self.cursor[1] and self.cursor[0] == 1:
                    self.cursor[1] -= 1
            elif inp.code == self.term.KEY_DOWN:
                if self.cursor[1] < 2 and self.cursor[0] == 1:
                    self.cursor[1] += 1

        self.draw()
        return True

