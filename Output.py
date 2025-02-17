import curses
from typing import Literal
import numpy as np


class Console:
    def __init__(self):
        self.console = curses.initscr()
        curses.noecho()
        self.console.keypad(True)
        self.width = 0
        self.height = 0

    def console_clear(self):
        self.console.clear()
        self.width = 0
        self.height = 0
        self.console.refresh()

    def returnToCommandLine(self):
        curses.endwin()


    def print(self, input: str, end: str="\n"):
        string = input + end
        self.console.addstr(self.height, self.width, string)
        # Calc Height
        linesCount = self._countLines(string)
        self.height += linesCount - 1

        # Calc Width

        if string.endswith("\n"):
            self.width = 0
        else:
            self.width = len(string.splitlines()[-1])

        self.console.refresh()

    def input(self, msg: str = "", type: Literal["password", "normal"] = "normal") -> str:
        cursor = 0
        curses.noecho()
        input = ""
        if not msg == "":
            self.print(msg)
        while True:
            c = self.console.getkey()
            if c == "\n":
                break
            elif "KEY_LEFT" == c:
                cursor = np.clip(cursor-1, len(input)*-1, 0)
                self.console.move(self.height, self.width +cursor)
                continue
            elif "KEY_RIGHT" == c:
                cursor = np.clip(cursor+1, len(input)*-1, 0)
                self.console.move(self.height, self.width +cursor)
                continue

            elif "KEY_HOME" == c:
                cursor = cursor = np.clip(len(input)*-1, len(input)*-1, 0)
                self.console.move(self.height, self.width + cursor)
                continue
            elif "KEY_END" == c:
                cursor = 0
                self.console.move(self.height, self.width + cursor)
                continue
            elif c == "KEY_DC":
                if cursor == 0:
                    continue
                part1 = input[0: len(input)+cursor]
                part2 = input[len(input)+cursor+1: len(input)]
                input = part1 + part2
                self.console_clear()
                cursor = np.clip(cursor+1, len(input)*-1, 0)
                if not msg == "":
                    self.print(msg)
                if type == "normal":
                    self.print(input, end = "")if len(input)> 0 else None
                else:
                    input_to_print = ""
                    for _ in input:
                        input_to_print += "*"
                    self.print(input_to_print, end = "")if len(input)> 0 else None

                self.console.move(self.height, self.width +cursor)
                continue

            elif c in ["KEY_UP", "KEY_DOWN",
                     "KEY_F(1)", "KEY_F(2)", "KEY_F(3)",
                     "KEY_F(4)", "KEY_F(5)", "KEY_F(6)",
                     "KEY_F(7)", "KEY_F(8)", "KEY_F(9)",
                     "KEY_F(10)", "KEY_RESIZE", "KEY_F(12)",
                     "KEY_NPAGE", "KEY_PPAGE",
                     "KEY_IC", "KEY_BTAB",
                     "KEY_F(14)", "KEY_F(13)",
                     "KEY_SUP", "KEY_SDOWN", "KEY_SRESIZE"
                     "KEY_SDC", "KEY_SNPAGE", "KEY_SPPAGE",
                     "KEY_SIC", "KEY_SBTAB", "KEY_SLEFT",
                     "KEY_SRIGHT"
                     ]:
                continue
            elif ord(c)== 9:
                if cursor == 0:
                    continue


            elif ord(c) == 8:
                if input == "":
                    continue
                if cursor == 0:
                    input = input[0: len(input)-1]

                else:
                    part1 = input[0: len(input)+cursor]
                    part1 = part1[0: len(part1)-1]
                    part2 = input[len(input)+cursor: len(input)]
                    input = part1 + part2
                self.console_clear()
                cursor = np.clip(cursor, len(input)*-1, 0)if len(input)> 0 else 0
                if not msg == "":
                    self.print(msg)
                if type == "normal":
                    self.print(input, end = "")if len(input)> 0 else None
                else:
                    input_to_print = ""
                    for _ in input:
                        input_to_print += "*"
                    self.print(input_to_print, end = "")if len(input)> 0 else None
                self.console.move(self.height, self.width +cursor)
                continue
            if cursor == 0:
                input += c
            else:
                part1 = input[0: len(input)+cursor]
                part2 = input[len(input)+cursor: len(input)]
                input = part1 + c + part2
            cursor = np.clip(cursor, len(input)*-1, 0)
            self.console_clear()
            self.console.move(self.height, self.width + cursor)
            if not msg == "":
                self.print(msg)
            if type == "normal":
                self.print(input, end = "")if len(input)> 0 else None
            else:
                input_to_print = ""
                for _ in input:
                    input_to_print += "*"
                self.print(input_to_print, end = "")if len(input)> 0 else None
        return input


    def selection_input(self, options: list[str], cursor:int = 0, msg: str = "")-> str:
        self.console_clear()
        if cursor >= len(options):
            cursor=0
        while True:
            self.console_clear()
            if not msg == "":
                self.print(msg)
            for pos, option in enumerate(options):
                self.print("{} {}".format(">"if pos == cursor else " ", option))
            c = self.console.getch()
            if c == curses.KEY_UP:
                cursor = (cursor -1)%len(options)
                continue
            elif c == curses.KEY_DOWN:
                cursor = (cursor +1)%len(options)
                continue
            elif c == curses.KEY_ENTER or c==10:
                self.console_clear()
                break
        return options[cursor]

    def _countLines(self, string: str) -> int:
        return string.count('\n') + 1
