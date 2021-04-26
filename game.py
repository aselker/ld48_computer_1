import os
from blessed import Terminal

from asm_editor import AsmEditor
from puzzle_list import PuzzleList

term = Terminal()
esc_delay = 0.05

print(term.home + term.clear)

# editor = AsmEditor(term, esc_delay)
editor = PuzzleList(term, esc_delay)
editor.draw()
while True:
    while term.width < 120 or term.height < 42:
        while term.width < 120:
            print(term.home + term.clear)
            print(term.white_on_black("Please resize terminal to at least 120 columns."))
            _ = term.inkey(timeout=0.1)  # Probably better way to do this?
        while term.height < 42:
            print(term.home + term.clear)
            print(term.white_on_black("Please resize terminal to at least 42 lines."))
            _ = term.inkey(timeout=0.1)  # Probably better way to do this?
        editor.draw()
    with term.cbreak(), term.hidden_cursor():
        inp = term.inkey(esc_delay=esc_delay)
        if not editor.keypress(inp):
            print(term.clear)
            break
