def chars_to_bools(chars):
    # assert all([c == "0" or c == "1" for c in chars])
    return [c == "1" for c in chars] + [False]* (6-len(chars))


def bools_to_chars(bools):
    return ["1" if b else "0" for b in bools]


def draw_outline(term, start_coords, end_coords, title=None, color=None):
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


class NanoEditor:
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
        if len(self.contents) < self.size[1]:
            contents = self.contents + [[]]*(self.size[1]-len(self.contents) )
        elif len(self.contents) > self.size[1]:
            contents = self.contents[:self.size[1]]
        else:
            contents = self.contents

        for y, line in enumerate(contents):
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
            if 0 == self.cursor[0]:
                if 0 < self.cursor[1] and self.contents[self.cursor[1] - 1] == []:
                    del self.contents[self.cursor[1] - 1]
                    self.contents.append([])
                    self.cursor[1] -= 1
            else:
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
