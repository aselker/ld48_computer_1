from asm import Asm, asm_ref_sheet
from nano_editor import NanoEditor, outline_editor, chars_to_bools, bools_to_chars
from ucode_editor import UcodeEditor


class AsmEditor:
    def __init__(self, term, esc_delay, puzzle):
        self.term = term
        self.esc_delay = esc_delay
        self.puzzle = puzzle

        self.CODE_WIDTH = 42
        self.CODE_HEIGHT = 32
        self.STACK_WIDTH = 9
        self.STACK_HEIGHT = 32

        self.stack_editor = NanoEditor(term, (1, 1), (self.STACK_WIDTH, self.STACK_HEIGHT))
        self.stack_editor.is_focused = False

        # Fill the stack
        self.asm = Asm(Asm.parse([]), [], self.CODE_HEIGHT)
        self.asm.stack = self.puzzle[2][0].copy()
        self._fill_stack_editor()

        self.code_editor = NanoEditor(term, (self.STACK_WIDTH + 6, 1), (self.CODE_WIDTH, self.CODE_HEIGHT))
        self.code_editor.edit_callback = self._parse
        self.code_editor.is_focused = False

        self.output_editor = NanoEditor(
            term, (self.STACK_WIDTH + self.CODE_WIDTH + 19, 1), (self.STACK_WIDTH, self.STACK_HEIGHT)
        )
        self.output_editor.is_focused = False

        self.info_editor = NanoEditor(
            term, (self.STACK_WIDTH * 2 + self.CODE_WIDTH + 22, 1), (41, self.STACK_HEIGHT)
        )
        self.info_editor.is_focused = False
        info = ["Goal:"] + self.puzzle[1].split("\n") + [""] + asm_ref_sheet.split("\n")
        self.info_editor.contents = [list(line) for line in info]

        # Ucode editor buttons, and RUN button
        self.left_buttons = []
        for i in range(4):
            x = self.STACK_WIDTH + self.CODE_WIDTH + 9
            y = 1 + 4 * i + (0 if i < 3 else 2)
            editor = NanoEditor(self.term, (x, y), (7, 1))
            editor.is_focused = False
            editor.contents = "EDIT" if i < 3 else ""
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
            self.left_buttons[-1].contents = [list("")]
        else:
            self.left_buttons[-1].contents = [list("FIX ERR")]

    def _num_to_dec_bin(self, val):
        return f"{val:>02} {val:>06b}"

    def _fill_stack_editor(self):
        self.stack_editor.contents = [list(self._num_to_dec_bin(val)) for val in self.asm.stack]
        self.stack_editor.contents.reverse()
        # self.stack_editor.contents = self.stack_editor.contents + [[]] * ( self.stack_editor.size[1] - len(self.asm.stack))

    def _begin_execution(self):
        if len(self.code_editor.highlighted_lines) != 0:
            return

        def output_callback(_, val):
            self.output.append(val)
            self.output_editor.contents = [list(self._num_to_dec_bin(val)) for val in self.output]

        ucodes = [editor.ucode for editor in self.ucode_sub_editors]
        self.asm = Asm(Asm.parse(self.code_editor.contents), ucodes, self.CODE_HEIGHT)
        self.asm.output_callback = output_callback

        total_steps = 0
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
            self._fill_stack_editor()

            # Check for success, even when the prog is not in the process of finishing, beucase that way the
            # machine doesn't have to know when to stop.
            success = self.output == self.puzzle[3][test_case]
            if success:
                if len(self.puzzle[3]) <= test_case + 1:
                    win_editor = NanoEditor(self.term, (30, 8), (32, 4))
                    win_editor.is_focused = False
                    win_editor.contents = [
                        "Your code took " + str(total_steps) + " steps, and",
                        "passed all of the test cases.",
                    ]
                    win_editor.contents = [list(line) for line in win_editor.contents]
                    outline_editor(self.term, win_editor, title="SUCCESS!", color=self.term.black_on_green)
                    win_editor.draw()
                    with self.term.cbreak(), self.term.hidden_cursor():
                        _ = self.term.inkey(esc_delay=self.esc_delay)
                    self.is_executing = False
                    self.draw()
                    break
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

            total_steps += 1
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
            self.term, self.code_editor, title="DEEP ASSEMBLY", color=outline_colors[self.cursor[0] == 0]
        )
        self.code_editor.draw()

        outline_editor(self.term, self.output_editor, title="OUTPUT", color=self.term.white_on_black)
        self.output_editor.draw()

        outline_editor(self.term, self.info_editor, title="INFO", color=self.term.white_on_black)
        self.info_editor.draw()

        for i, button in enumerate(self.left_buttons):
            title = ["CUST1", "CUST2", "CUST3", "EXECUTE"][i]
            outline_editor(self.term, button, title=title, color=outline_colors[self.cursor == [1, i]])
            button.draw()

        # Draw the execution arrow
        if self.is_executing:
            arrow_y = self.asm.pc + 1
        else:
            arrow_y = 1
        print(self.term.move_xy(self.STACK_WIDTH + 4, arrow_y) + self.term.red_on_black("→"))

        # Line numbers
        for y in range(self.CODE_HEIGHT):
            if y + 1 != arrow_y:
                print(self.term.move_xy(self.STACK_WIDTH + 3, y + 1) + self.term.white_on_black(str(y)))

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
