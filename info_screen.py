import textwrap

from nano_editor import NanoEditor, outline_editor

info_text = [
    """Thank you for purchasing DEEPER BROS. (R) DIGITAL COMPUTER v0.23!  

Your new computer comes with a beautiful 4-color display, a 5 Hz CPU, and a built-in programming environment.  Use the arrow keys to navigate, ENTER to select, and ESC to exit.

The DEEPER BROS. (R) DIGITAL COMPUTER v0.23 is programmed using two languages: Deep Assembly language, and Deeper Microcode.  Programs are written in Deep Assembly, and Deeper Microcode is used to create custom Deep Assembly commands.

NOTE: Programming the DEEPER BROS. (R) DIGITAL COMPUTER v0.23 is not for the faint of heart.  At DEEPER BROS. INC., we have not yet had success building programs 7, 8, or 9.  Good luck.""",
    """DEEP ASSEMBLY
Each line of Deep Assembly consists of commands or pairs of commands, separated by pipe characters (|).  This is an example program:

    4|JMP
    OUTPUT
    16 POP|PUSH JMPZERO
    POP 1|ADD POP|SWAP ADD|PUSH

The fundamental data type of Deep Assembly is the 6-bit integer, representing any number from 0 to 63.  If a command would result in a number outside that range, such as "32 32 | ADD", the number wraps to the range of 0-63.  Each command recieves two such numbers as inputs.  If the command is before the first | on the line, such as the OUTPUT above, then its inputs are 0.  Otherwise, its inputs are the outputs of the commands before the last |.  If there was only one command before the last |, then the second input is set to 0.  For example, the above JMP's inputs are 4 and 0.  The following is a list of commands:

    FIRST:   return the first input
    SECOND:  return the second input
    ADD:     return sum of inputs
    SUB:     return difference of inputs
    JMP:     jump to line no. by first input
    JMPZERO: JMP, if second input is 0
    PUSH:    push first input onto stack
    POP:     remove top of stack, return it
    SWAP:    swap top two stack entries
    APPEND:  add first input after stack
    OUTPUT:  send first input to Output
    CUST1:   run first custom assembly cmd
    CUST2:   run second custom assembly cmd
    CUST3:   run third custom assembly cmd

Instructions with no explicit return value, such as PUSH, return their first input.  Normally, after every line executes, execution continues to the next line.  A JMP or JMPZERO command will redirect execution.  PUSH, POP, SWAP, and APPEND all interact with the Stack, which can be used to store and recover numbers, and is also how the program takes input.  OUTPUT appends to the write-only Output list.  CUST1, CUST2, and CUST3 are custom, user-editable Deep Assembly commands written in Deeper Microcode; see page 3 for details.  The program finishes when execution continues after the last line of code, or immediately if the Output is correct.""",
    """DEEPER MICROCODE
Deeper Microcode is a simple language, with no flow control.  The fundamental data type of Deeper Microcode is the bit; input and output is in the form of registers that represent numbers, but Deeper Microcode only works with single bits.  For example, the number 3 is equivalent to the bits 000011.  Each line is a single command.  This is an example program:

    U1 = BUF I10
    U2 = XOR I3 I4
    O1 = IF U1 U2 I1

Each location, such as "U1", is written as a letter (the register name) and a number (the bit index in the register).  There are six registers:
    C is the two-bit Constant register.  C0 is 0, C1 is 1.
    I is the 12-bit Input register.  The first and second inputs to the CUST1 / CUST2 / CUST3 command in Deep Assembly
        are I1 thru I6 and I7 thru I12, respectively.
    A is the six-bit Address register.  It holds the line number of Deep Assembly that is currently executing.
    U is the six-bit User register.  It has no special purpose, and can be used for temporary storage.
    O is the six-bit Output register.  The CUST1 / CUST2 / CUST3 command will output this value after the Deeper
        Microcode program finishes.
    J is the six-bit Jump register.  After the Deep Assembly line with the CUST1 / CUST2 / CUST3 command is finished, 
        execution will continue from this line.

C, I, and A can only be read from, not written to.  U, O, and J can both be written to and read from.  U and O are initialized to 0.  J is initialized to A + 1, so that if J is not edited, Deep Assembly execution continues as normal on the next line.  The following is a list of Deeper Microcode commands:

    BUF  (1 arg): Return arg unmodified
    NOT  (1 arg): Invert arg
    AND  (2 arg): 1 only if both args are 1
    NAND (2 arg): Inverted and
    OR   (2 arg): 1 if either arg is 1
    NOR  (2 arg): Inverted or
    XOR  (2 arg): 1 if exactly one arg is 1
    XNOR (2 arg): Inverted xor
    IF   (3 arg): Second arg if first is 1, otherwise third arg

Using an incorrect number of arguments (e.g. "U1 = OR I1"), or incorrect spacing (e.g. "U1=BUF I10"), is an error.""",
    """EDITING AND RUNNING CODE
The DEEPER BROS. (R) DIGITAL COMPUTER v0.23 comes with code editors and execution environments for both Deep Assembly and Deeper Microcode.

In the Deep Assembly editor, you may edit the assembly code, and also launch Deeper Microcode sub-editors for the three custom commands.  Also, the stack and output are displayed for your convenience.  Any lines with errors in the Deep Assembly code are highlighted in red.  When there are no errors, you may run the program

Each Deep Assembly program has a goal, such as squaring numbers.  Input is given as the starting Stack.  Output is taken from the write-only Output list.  Each task comes with several test cases; after one passes successfully, the next begins automatically.  The program is considered successful if all test cases pass.

The Deeper Microcode editor lets you test your custom commands with arbitrary inputs.  The Input and Address registers are editable (note that any character other than "1" is interepreted as "0" when editing the registers).  The microcode executes automatically when the program is valid.  Like the Deep Assembly editor, invalid lines are highlighted in red.

Both editors also show convenient language reference sheets.""",
]


class InfoScreen:
    def __init__(self, term):
        self.term = term

        self.WIDTH = 118
        self.HEIGHT = 38
        self.info_screen = NanoEditor(self.term, (1, 1), (self.WIDTH, self.HEIGHT))
        self.info_screen.is_focused = False

        self.current_screen = 0
        self.num_screens = len(info_text)

    def _fill_screen(self):
        text = info_text[self.current_screen]
        wrapped = []
        for line in text.split("\n"):
            if line == "":
                wrapped.append([])
            else:
                wrapped += textwrap.wrap(line, width=self.WIDTH)

        if 0 < self.current_screen:
            bottom_bar = "<- PREV"
        else:
            bottom_bar = "       "

        if self.current_screen < self.num_screens - 1:
            bottom_bar += " " * (self.WIDTH - 14) + "NEXT ->"

        wrapped = [list(line) for line in wrapped]
        wrapped += [[]] * (self.HEIGHT - len(wrapped) - 1)
        wrapped += [list(bottom_bar)]
        self.info_screen.contents = wrapped

    def draw(self):
        print(self.term.clear)

        self._fill_screen()

        outline_color = self.term.white_on_black
        title = (
            "INFO PAGE " + str(self.current_screen + 1) + " OF " + str(self.num_screens)
        )
        outline_editor(self.term, self.info_screen, title, outline_color)
        self.info_screen.draw()

    def keypress(self, inp):
        if inp.code == self.term.KEY_ESCAPE:
            return False
        elif inp.code == self.term.KEY_LEFT:
            if 0 < self.current_screen:
                self.current_screen -= 1
        elif inp.code == self.term.KEY_RIGHT:
            if self.current_screen < self.num_screens - 1:
                self.current_screen += 1

        self.draw()
        return True
