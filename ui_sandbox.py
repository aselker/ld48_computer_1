import os
from blessed import Terminal

from asm import Asm
from ucode import UCode


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


class NanoEditor:
    """
    TODO:
        * Insert in middle of line?
    """

    def __init__(self, term, origin, size, contents=None):
        self.term = term
        self.origin = origin
        self.size = size
        self.cursor = [0, 0]
        self.is_focused = True
        self.highlighted_lines = []

        if contents is None:
            self.contents = [[] for _ in range(self.size[1])]
        else:
            self.contents = contents

        self.legal_chars = (
            [chr(d) for d in range(ord("0"), ord("9") + 1)]
            + [chr(c) for c in range(ord("A"), ord("Z") + 1)]
            + list(" |=!@#$%^&*().")
        )

    def edit_callback(self):
        """Meant to be overwritten"""
        pass

    def draw(self):
        for y, line in enumerate(self.contents):
            line = "".join(line)

            line_color = (
                self.term.white_on_black if (y not in self.highlighted_lines) else self.term.black_on_red
            )
            cursor_color = (
                # self.term.black_on_green if (y not in self.highlighted_lines) else self.term.black_on_white
                self.term.black_on_green
            )

            if self.cursor[1] == y and self.is_focused:
                assert self.cursor[0] <= len(line)
                assert self.cursor[0] <= self.size[0] - 1
                colored_line = line_color(line[: self.cursor[0]])
                if len(line) == self.cursor[0]:  # cursor is hanging out after the line
                    colored_line += cursor_color(" ")
                    # One extra char for cursor
                    colored_line += line_color(" " * (self.size[0] - len(line) - 1))
                elif len(line) == self.cursor[0] + 1:  # cursor is on last char of line
                    colored_line += cursor_color(line[self.cursor[0]])
                    colored_line += line_color(" " * (self.size[0] - len(line)))
                else:
                    colored_line += cursor_color(line[self.cursor[0]])
                    colored_line += line_color(line[self.cursor[0] + 1 :])
                    colored_line += line_color(" " * (self.size[0] - len(line)))
            else:
                colored_line = line_color(line)
                colored_line += line_color(" " * (self.size[0] - len(line)))

            print(self.term.move_xy(self.origin[0], self.origin[1] + y) + colored_line)

    def keypress(self, inp):
        if inp.code == self.term.KEY_LEFT:
            if 0 < self.cursor[0]:
                self.cursor[0] -= 1
        elif inp.code == self.term.KEY_RIGHT:
            if self.cursor[0] < self.size[0] - 1 and self.cursor[0] < len(self.contents[self.cursor[1]]):
                self.cursor[0] += 1
        elif inp.code == self.term.KEY_HOME:
            self.cursor[0] = 0
        elif inp.code == self.term.KEY_END:
            self.cursor[0] = len(self.contents[self.cursor[1]])
        elif inp.code == self.term.KEY_UP:
            if 0 < self.cursor[1]:
                self.cursor[1] -= 1
                self.cursor[0] = min(self.cursor[0], len(self.contents[self.cursor[1]]))
        elif inp.code == self.term.KEY_DOWN:
            if self.cursor[1] < self.size[1] - 1:
                self.cursor[1] += 1
                self.cursor[0] = min(self.cursor[0], len(self.contents[self.cursor[1]]))
        elif inp.code == self.term.KEY_BACKSPACE:
            if 0 < self.cursor[0]:
                del self.contents[self.cursor[1]][self.cursor[0] - 1]
                self.cursor[0] -= 1
        elif inp.code == self.term.KEY_DELETE:
            if self.cursor[0] < len(self.contents[self.cursor[1]]):
                del self.contents[self.cursor[1]][self.cursor[0]]
        elif inp.code == self.term.KEY_ENTER:
            if self.contents[-1] == [] and self.cursor[1] < self.size[1] - 1:
                self.contents.pop()
                self.contents.insert(self.cursor[1] + 1, [])
                self.cursor[0] = 0
                self.cursor[1] += 1
        elif inp.upper() in self.legal_chars:
            if len(self.contents[self.cursor[1]]) < self.size[0]:
                self.contents[self.cursor[1]].insert(self.cursor[0], inp.upper())
                if self.cursor[0] < self.size[0] - 1:
                    self.cursor[0] += 1

        self.edit_callback()
        self.draw()


def draw_outline(term, start_coords, end_coords, title=None, color=None):
    # "─│┌┐└┘"
    if color == None:
        color = term.green_on_black
    print(
        term.move_xy(start_coords[0], start_coords[1])
        + color("┌" + "─" * (end_coords[0] - start_coords[0] - 1) + "┐")
    )
    for y in range(start_coords[1] + 1, end_coords[1]):
        print(term.move_xy(start_coords[0], y) + color("│"))
        print(term.move_xy(end_coords[0], y) + color("│"))
    print(
        term.move_xy(start_coords[0], end_coords[1])
        + color("└" + "─" * (end_coords[0] - start_coords[0] - 1) + "┘")
    )

    if title is not None:
        assert len(title) <= end_coords[0] - start_coords[0] - 1
        print(term.move_xy(start_coords[0] + 1, start_coords[1]) + color(title))


def outline_editor(term, editor, title, color=None):
    draw_outline(
        term,
        (editor.origin[0] - 1, editor.origin[1] - 1,),
        (editor.origin[0] + editor.size[0], editor.origin[1] + editor.size[1],),
        title=title,
        color=color,
    )


def chars_to_bools(chars):
    assert all([c == "0" or c == "1" for c in chars])
    return [c == "1" for c in chars]


def bools_to_chars(bools):
    return ["1" if b else "0" for b in bools]


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

            code = UCode(insts)
            user, output, jump = code.run(input1, input2, addr)
            self.reg_editors[3].contents = [bools_to_chars(user)]
            self.reg_editors[4].contents = [bools_to_chars(output)]
            self.reg_editors[5].contents = [bools_to_chars(jump)]

            self.draw()

    def draw(self):
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
                raise NotImplementedError
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


class AsmEditor:
    def __init__(self, term):
        self.term = term

        self.CODE_WIDTH = 32
        self.CODE_HEIGHT = 24
        self.STACK_WIDTH = 9
        self.STACK_HEIGHT = 32

        self.stack_editor = NanoEditor(term, (1, 1), (self.STACK_WIDTH, self.STACK_HEIGHT))
        self.stack_editor.is_focused = False

        self.code_editor = NanoEditor(term, (self.STACK_WIDTH + 5, 1), (self.CODE_WIDTH, self.CODE_HEIGHT))
        self.code_editor.edit_callback = self._parse
        self.code_editor.is_focused = False

        # Ucode editor buttons, and RUN button
        self.left_buttons = []
        for i in range(4):
            x = self.STACK_WIDTH + self.CODE_WIDTH + 8
            y = 1 + 4 * i
            editor = NanoEditor(term, (x, y), (7, 1))
            editor.is_focused = False
            editor.contents = "EDIT" if i < 3 else "RUN ASM"
            editor.contents = [list(editor.contents)]

            self.left_buttons.append(editor)

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

    def _begin_execution(self):
        if len(self.code_editor.highlighted_lines) != 0:
            return

        # TODO: Add ucodes
        self.asm = Asm(Asm.parse(self.code_editor.contents), [], self.CODE_HEIGHT)
        self.is_executing = True
        while self.is_executing:
            with term.cbreak(), term.hidden_cursor():
                inp = term.inkey(esc_delay=esc_delay, timeout=0.2)
            if inp.code == self.term.KEY_ESCAPE:
                self.is_executing = False
                self.draw()
                break

            self.asm.step()
            self.stack_editor.contents = [list(f"{val:>02} {val:>06b}") for val in self.asm.stack]
            self.stack_editor.contents.reverse()

            if self.CODE_HEIGHT - 1 <= self.asm.pc or all(
                ["".join(line).strip() == "" for line in self.code_editor.contents[self.asm.pc :]]
            ):
                self.is_executing = False
                self.draw()
                break

            self.draw()

    def draw(self):
        # Clear the screen
        # TODO: Remove this for prettiness
        print(self.term.clear)

        if self.is_editing:
            outline_colors = self.term.white_on_black, self.term.black_on_white
        else:
            outline_colors = self.term.green_on_black, self.term.black_on_green

        outline_editor(self.term, self.stack_editor, title="STACK", color=self.term.white_on_black)
        self.stack_editor.draw()

        outline_editor(
            self.term, self.code_editor, title="ASSEMBLY CODE", color=outline_colors[self.cursor[0] == 0]
        )
        self.code_editor.draw()

        for i, button in enumerate(self.left_buttons):
            title = ["UCODE1", "UCODE2", "UCODE3", "EXECUTE"][i]
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
        if self.is_editing:
            if inp.code == self.term.KEY_ESCAPE:
                self.is_editing = False
                self._highlighted_editor.is_focused = False
            else:
                self._highlighted_editor.keypress(inp)
        else:
            if inp.code == self.term.KEY_ESCAPE:
                raise NotImplementedError
            elif inp.code == self.term.KEY_ENTER:
                if self.cursor[0] == 0:
                    self.is_editing = True
                    self._highlighted_editor.is_focused = True
                elif self.cursor == [1, 3]:
                    self._begin_execution()
                else:
                    raise NotImplementedError
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
                if self.cursor[1] < 3 and self.cursor[0] == 1:
                    self.cursor[1] += 1

        self.draw()


term = Terminal()
esc_delay = 0.05

while term.width < 120:
    print(term.home + term.clear)
    print(term.white_on_black("Please resize terminal to at least 120 columns."))
    _ = term.inkey(timeout=0.1)  # Probably better way to do this?
while term.height < 40:
    print(term.home + term.clear)
    print(term.white_on_black("Please resize terminal to at least 40 lines."))
    _ = term.inkey(timeout=0.1)  # Probably better way to do this?

print(term.home + term.clear)

editor = AsmEditor(term)
# editor = UcodeEditor(term)
editor.draw()
while True:
    with term.cbreak(), term.hidden_cursor():
        inp = term.inkey(esc_delay=esc_delay)
        editor.keypress(inp)


Screen(term)
