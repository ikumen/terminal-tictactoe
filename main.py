import curses
import traceback
from game import TerminalTicTacToe

def main():
  try:
    curses.wrapper(TerminalTicTacToe().init)
  except Exception as e:
    print(e)
    traceback.print_exc()

if __name__ == "__main__":
  main()