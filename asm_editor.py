from asm import Asm
from nano_editor import NanoEditor, outline_editor
from ucode_editor import UcodeEditor


def chars_to_bools(chars):
    assert all([c == "0" or c == "1" for c in chars])
    return [c == "1" for c in chars]

def bools_to_chars(bools):
    return ["1" if b else "0" for b in bools]


class AsmEditor:
    def __init__(self, term, esc_delay, puzzle):
        self.term = term
        self.esc_delay = esc_delay
        self.puzzle = puzzle

        self.CODE_WIDTH = 32
        self.CODE_HEIGHT = 24
        self.STACK_WIDTH = 9
        self.STACK_HEIGHT = 32

        self.stack_editor = NanoEditor(term, (1, 1), (self.STACK_WIDTH, self.STACK_HEIGHT))
        self.stack_editor.is_focused = False

        self.code_editor = NanoEditor(term, (self.STACK_WIDTH + 5, 1), (self.CODE_WIDTH, self.CODE_HEIGHT))
        self.code_editor.edit_callback = self._parse
        self.code_editor.is_focused = False

        self.output_editor = NanoEditor(
            term, (self.STACK_WIDTH + self.CODE_WIDTH + 18, 1), (self.STACK_WIDTH, self.STACK_HEIGHT)
        )
        self.output_editor.is_focused = False

        # Ucode editor buttons, and RUN button
        self.left_buttons = []
        for i in range(4):
            x = self.STACK_WIDTH + self.CODE_WIDTH + 8
            y = 1 + 4 * i + (0 if i < 3 else 2)
            editor = NanoEditor(self.term, (x, y), (7, 1))
            editor.is_focused = False
            editor.contents = "EDIT" if i < 3 else "RUN ASM"
            editor.contents = [list(editor.contents)]

            self.left_buttons.append(editor)

        self.ucode_sub_editors = [UcodeEditor(self.term) for _ in range(3)]

        self.output = []
        self.cursor = [0, 0]
        self.is_editing = False
        self.is_executing = False

    def _parse(self):
        cmds = Asm.parse(self.code_editor.contents)
        self.code_editor.highlighted_lines = [i for i, cmd in enumerate(cmds) if cmd is None]
        if len(self.code_editor.highlighted_lines) == 0:
            self.left_buttons[-1].contents = [list("RUN ASM")]
        else:
            self.left_buttons[-1].contents = [list("FIX ERR")]

    def _num_to_dec_bin(self, val):
        return f"{val:>02} {val:>06b}"

    def _begin_execution(self):
        if len(self.code_editor.highlighted_lines) != 0:
            return

        def output_callback(_, val):
            self.output.append(val)
            self.output_editor.contents = [list(self._num_to_dec_bin(val)) for val in self.output]

        ucodes = [editor.ucode for editor in self.ucode_sub_editors]
        self.asm = Asm(Asm.parse(self.code_editor.contents), ucodes, self.CODE_HEIGHT)
        self.asm.output_callback = output_callback


        test_case = 0
        self.asm.stack = self.puzzle[2][test_case].copy()
        self.output = []
        self.is_executing = True
        while self.is_executing:
            with self.term.cbreak(), self.term.hidden_cursor():
                inp = self.term.inkey(esc_delay=self.esc_delay, timeout=0.2)
            if inp.code == self.term.KEY_ESCAPE:
                self.is_executing = False
                self.draw()
                break

            self.asm.step()
            self.stack_editor.contents = [list(self._num_to_dec_bin(val)) for val in self.asm.stack]
            self.stack_editor.contents.reverse()

            # Check for success, even when the prog is not in the process of finishing, beucase that way the
            # machine doesn't have to know when to stop.
            success = self.output == self.puzzle[3][test_case]
            if success:
                if len(self.puzzle[3]) <= test_case + 1:
                    raise NotImplementedError("A winner is you")
                else:
                    # Reset and start again!
                    test_case += 1
                    self.asm.stack = self.puzzle[2][test_case].copy()
                    self.asm.pc = 0
                    self.output = []

            if self.CODE_HEIGHT - 1 <= self.asm.pc or all(
                ["".join(line).strip() == "" for line in self.code_editor.contents[self.asm.pc :]]
            ):
                self.is_executing = False
                self.draw()
                break

            self.draw()

    def draw(self):
        print(self.term.clear)

        if self.is_editing or self.is_executing:
            outline_colors = self.term.white_on_black, self.term.black_on_white
        else:
            outline_colors = self.term.green_on_black, self.term.black_on_green

        outline_editor(self.term, self.stack_editor, title="STACK", color=self.term.white_on_black)
        self.stack_editor.draw()

        outline_editor(
            self.term, self.code_editor, title="ASSEMBLY CODE", color=outline_colors[self.cursor[0] == 0]
        )
        self.code_editor.draw()

        outline_editor(self.term, self.output_editor, title="OUTPUT", color=self.term.white_on_black)
        self.output_editor.draw()

        for i, button in enumerate(self.left_buttons):
            title = ["CUSTOM1", "CUSTOM2", "CUSTOM3", "EXECUTE"][i]
            outline_editor(self.term, button, title=title, color=outline_colors[self.cursor == [1, i]])
            button.draw()

        # Draw the execution arrow
        if self.is_executing:
            arrow_y = self.asm.pc + 1
        else:
            arrow_y = 1
        print(self.term.move_xy(self.STACK_WIDTH + 3, arrow_y) + self.term.red_on_black("→"))

    @property
    def _highlighted_editor(self):
        if self.cursor[0] == 0:
            return self.code_editor
        else:
            return self.left_buttons[self.cursor[1]]

    def keypress(self, inp):
        do_draw = True
        if self.is_editing:
            if self.cursor[0] == 0:
                if inp.code == self.term.KEY_ESCAPE:
                    self.is_editing = False
                    self._highlighted_editor.is_focused = False
                else:
                    self._highlighted_editor.keypress(inp)
            else:
                editor = self.ucode_sub_editors[self.cursor[1]]
                self.is_editing = editor.keypress(inp)
                do_draw = not self.is_editing
        else:
            if inp.code == self.term.KEY_ESCAPE:
                return False
            elif inp.code == self.term.KEY_ENTER:
                if self.cursor[0] == 0:
                    self.is_editing = True
                    self._highlighted_editor.is_focused = True
                elif self.cursor == [1, 3]:
                    self._begin_execution()
                else:
                    self.is_editing = True
                    self.ucode_sub_editors[self.cursor[1]].draw()
                    do_draw = False
            elif inp.code == self.term.KEY_LEFT:
                if 0 < self.cursor[0]:
                    self.cursor[0] -= 1
            elif inp.code == self.term.KEY_RIGHT:
                if self.cursor[0] < 1:
                    self.cursor[0] += 1
            elif inp.code == self.term.KEY_UP:
                if 0 < self.cursor[1] and self.cursor[0] == 1:
                    self.cursor[1] -= 1
            elif inp.code == self.term.KEY_DOWN:
                if self.cursor[1] < 3 and self.cursor[0] == 1:
                    self.cursor[1] += 1

        if do_draw:
            self.draw()
        return True
