from blessed import Terminal


class OverviewScreen:
    """
    TODO: What is this actually for?
    """

    def __init__(self):

        self.box_names = [
            ["Puzzle 1", "Puzzle 2", "Puzzle 3", "Puzzle 4"],
            ["Asm 1", "Asm 2", "Asm 3", "Asm 4"],
            ["Ucode 1", "Ucode 2", "Ucode 3", "Ucode 4"],
        ]

        assert not any([any([8 < len(name) for name in names]) for names in self.box_names])
        self.cursor = [0, 0]

        self.draw()

    def draw(self):
        # TODO: Overwrite the whole screen
        for y, names in enumerate(self.box_names):
            for x, name in enumerate(names):
                is_highlighted = [x, y] == self.cursor
                box_color = term.black_on_white if is_highlighted else term.white_on_black
                print(term.move_xy(10 + 30 * x, 5 + 13 * y) + box_color(" " * 10))
                print(term.move_xy(10 + 30 * x, 6 + 13 * y) + box_color(" ") + term.white_on_black(name))
                print(term.move_xy(19 + 30 * x, 6 + 13 * y) + box_color(" "))
                print(term.move_xy(10 + 30 * x, 7 + 13 * y) + box_color(" " * 10))

    def keypress(self, inp):
        if inp.code == term.KEY_LEFT:
            if 0 < self.cursor[0]:
                self.cursor[0] -= 1
        elif inp.code == term.KEY_RIGHT:
            if self.cursor[0] < 3:
                self.cursor[0] += 1
        elif inp.code == term.KEY_UP:
            if 0 < self.cursor[1]:
                self.cursor[1] -= 1
        elif inp.code == term.KEY_DOWN:
            if self.cursor[1] < 2:
                self.cursor[1] += 1

        self.draw()


class NanoEditor:
    def __init__(self, origin, size, contents=None):
        self.origin = origin
        self.size = size
        self.cursor = [0, 0]

        if contents is None:
            self.contents = [[] for _ in range(self.size[1])]
        else:
            self.contents = contents

        self.legal_chars = (
            [chr(d) for d in range(ord("0"), ord("9") + 1)]
            + [chr(c) for c in range(ord("A"), ord("Z") + 1)]
            + list(" =!@#$%^&*().")
        )

        self.draw()

    def draw(self):
        for y, line in enumerate(self.contents):
            line = "".join(line)
            if self.cursor[1] == y:
                assert self.cursor[0] <= len(line)
                assert self.cursor[0] <= self.size[0] - 1
                colored_line = term.white_on_black(line[: self.cursor[0]])
                if len(line) == self.cursor[0]:  # cursor is hanging out after the line
                    colored_line += term.black_on_white(" ")
                    # One extra char for cursor
                    colored_line += term.white_on_black(" " * (self.size[0] - len(line) - 1))
                elif len(line) == self.cursor[0] + 1:  # cursor is on last char of line
                    colored_line += term.black_on_white(line[self.cursor[0]])
                    colored_line += term.white_on_black(" " * (self.size[0] - len(line)))
                else:
                    colored_line += term.black_on_white(line[self.cursor[0]])
                    colored_line += term.white_on_black(line[self.cursor[0] + 1 :])
                    colored_line += term.white_on_black(" " * (self.size[0] - len(line)))
            else:
                colored_line = term.white_on_black(line)
                colored_line += term.white_on_black(" " * (self.size[0] - len(line)))

            print(term.move_xy(self.origin[0], self.origin[1] + y) + colored_line)

    def keypress(self, inp):
        if inp.code == term.KEY_LEFT:
            if 0 < self.cursor[0]:
                self.cursor[0] -= 1
        elif inp.code == term.KEY_RIGHT:
            if self.cursor[0] < self.size[0] - 1 and self.cursor[0] < len(self.contents[self.cursor[1]]):
                self.cursor[0] += 1
        elif inp.code == term.KEY_UP:
            if 0 < self.cursor[1]:
                self.cursor[1] -= 1
                self.cursor[0] = min(self.cursor[0], len(self.contents[self.cursor[1]]))
        elif inp.code == term.KEY_DOWN:
            if self.cursor[1] < self.size[1] - 1:
                self.cursor[1] += 1
                self.cursor[0] = min(self.cursor[0], len(self.contents[self.cursor[1]]))
        elif inp.upper() in self.legal_chars:
            if self.cursor[0] < self.size[0]:
                if self.cursor[0] == len(self.contents[self.cursor[1]]):
                    self.contents[self.cursor[1]].append(" ")
                self.contents[self.cursor[1]][self.cursor[0]] = inp.upper()
                if self.cursor[0] < self.size[0] - 1:
                    self.cursor[0] += 1

        self.draw()


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


class Screen:
    def __init__(self):
        self.go_to_state(("overview", 0))
        while True:
            with term.cbreak(), term.hidden_cursor():
                inp = term.inkey()
            if inp.code == term.KEY_ESCAPE:
                if self.state[0] == "overview":
                    break
                elif self.state[0] == "editor":
                    self.go_to_state(("overview", 0))
            if inp.code == term.KEY_ENTER:
                if self.state[0] == "overview":
                    self.go_to_state(("editor", 0))
                elif self.state[0] == "editor":
                    pass
            else:
                self.screen.keypress(inp)

    def go_to_state(self, new_state):
        self.state = new_state
        if self.state[0] == "overview":
            self.screen = OverviewScreen()
        elif self.state[0] == "editor":
            self.screen = NanoEditor((5, 2), (24, 32))


Screen()
