import curses
import time
from board import Board
from players import SimpleAIPlayer, HardAIPlayer, HumanPlayer

CODE_GRN = 1
CODE_WHT = 2
CODE_INV = 3
CODE_CYN = 4

class TerminalTicTacToe:
  """Terminal (powered by curses) base Tic-Tac-Toe."""
  def init(self, stdscr):
    self.stdscr = stdscr
    self.ht, self.wd = stdscr.getmaxyx()
    # Check for min screen dimensions
    if self.ht < self.MIN_HT or self.wd < self.MIN_WD:
      raise Exception("Screen too small: ht={}, wd={}".format(self.ht, self.wd))
    curses.start_color()
    curses.curs_set(1)
    curses.init_pair(CODE_GRN, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(CODE_WHT, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(CODE_CYN, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(CODE_INV, curses.COLOR_BLACK, curses.COLOR_WHITE)
    # Start the game loop
    self.play()    

  def display_status(self, status):
    """Helper for display bottom status"""
    self.stdscr.addstr(self.ht-1, 0, status, curses.color_pair(CODE_INV))

  def _compute_startx(self, s):
    """Helper for computing the mid point 
    and offset for laying out the given 
    string on screen."""
    slen = len(s)
    return int((self.wd//2) - (slen//2) - (slen%2))

  def display_divider(self, y):
    """Helper for displaying a horizontal
    divider onto screen."""
    x = self._compute_startx(self.DIV)
    self.stdscr.addstr(y, x, self.DIV)

  def display_header(self):
    """Helper for displaying the top header."""
    x = self._compute_startx(self.TITLE)
    self.stdscr.addstr(1, x, self.TITLE, curses.A_BOLD+curses.color_pair(CODE_CYN))
    self.display_divider(2)

  def display_description(self, y, players):
    """Helper for displaying game desc."""
    desc = "{} vs {}".format(players[0].desc, players[1].desc)
    x = self._compute_startx(desc)
    self.stdscr.addstr(y, x, desc)

  def display_board(self, board):
    """Helper for displaying the game board."""
    cells = board.cells
    y, x = 8, self._compute_startx(self.BOARD_DIV)
    self.stdscr.addstr(y, x, self.BOARD_ROW.format(*cells[:3]), curses.A_BOLD)
    self.stdscr.addstr(y+1, x, self.BOARD_DIV, curses.A_BOLD)
    self.stdscr.addstr(y+2, x, self.BOARD_ROW.format(*cells[3:6]), curses.A_BOLD)
    self.stdscr.addstr(y+3, x, self.BOARD_DIV, curses.A_BOLD)
    self.stdscr.addstr(y+4, x, self.BOARD_ROW.format(*cells[6:9]), curses.A_BOLD)

  def display_menu(self, y=15, full=True):
    """Helper for displaying the help menu"""
    menu = self.HELP_MENU if full else self.HELP_MENU[2:6]
    x = self._compute_startx(menu[0])
    for i, item in enumerate(menu, y):
      self.stdscr.addstr(i, x, item, curses.A_DIM)

  def display_message(self, msg, attrs):
    """Helper for displaying messages."""
    y, x = 5, self._compute_startx(msg)
    self.stdscr.addstr(y, x, msg, attrs)

  def _key_to_coord(self, key, coord_index):
    """If applicable, calculate where on the board
    the corresponding up,down,left,right keyboard
    input maps to. Return the updated coord_index."""
    if key == curses.KEY_DOWN and coord_index < 6:
      coord_index += 3
    elif key == curses.KEY_UP and coord_index > 2:
      coord_index -= 3
    elif (key == curses.KEY_RIGHT 
        and ((coord_index+1)%3) > 0
        and coord_index < 8):
      coord_index += 1
    elif (key == curses.KEY_LEFT
        and ((coord_index-1)%3) < 2
        and coord_index > 0):
      coord_index -= 1
    return coord_index

  def _move_cursor(self, y, x):
    """Helper for moving the cursor."""
    self.stdscr.move(y, x)

  def _new_game(self, k):
    board = Board()
    players = [HumanPlayer('X', board), HumanPlayer('O', board)]
    if k == self.KEY_HARDAI:
      players[0] = HardAIPlayer('X', board, players[1])
    elif k == self.KEY_EASYAI:
      players[0] = SimpleAIPlayer('X', board)
    return board, players

  def display_full(self, board, players, msg, msg_attrs):
    self.stdscr.clear()
    if board.is_full() or board.is_won():
      msg_attrs, msg = ((curses.color_pair(CODE_GRN), "{} has won the game!".format(players[(board.turn+1)% 2].desc))
          if board.is_won() else (0, "Tie game, let's play again"))
      # Game over reset all cursor to upper left corner
      self._move_cursor(0,0)
    else:
      msg_attrs, msg = (0, "{}'s turn".format(players[board.turn % 2].desc))
    self.display_header()
    self.display_description(3, players)
    self.display_message(msg, msg_attrs)
    self.display_board(board)
    self.display_divider(14)
    self.display_menu()
    self._move_cursor(0,0)
    self.stdscr.refresh()

  def display_partial(self):
    self.stdscr.clear()
    self.display_header()
    self.display_message(self.SPLASH, 0)
    self.display_divider(14)
    self.display_menu(full=False)
    self.stdscr.refresh()

  def play(self):
    """Set a board/players and start game loop."""
    board = None
    # List of y,x coords in relation to game cells
    # Each index holds the board coordinates, use to
    # draw the corresponding cell value.
    board_coords = [(0,0),(0,4),(0,8),(2,0),(2,4),(2,8),(4,0),(4,4),(4,8)]
    # Coordinate index we want to send the cursor to
    # 4th -> 2row/2col, (e.g, middle of the board)
    coord_index = self.START_COORD
    # Where to move cursor
    cursor_y = 0
    cursor_x = 0
    # Keyboard input, starts with null
    key = 0 
    players = []

    while key != ord('q'):
      # Main game loop

      # Current player for a turn
      player = None
      # Message and attributes
      msg_attrs = None
      msg = None
      should_continue = False

      if key in self.KEY_NEW_GAMES:
        # new game 
        board, players = self._new_game(key)
        msg_attrs, msg = 0, "{}'s turn".format(players[0].desc)
        coord_index = self.START_COORD
        self.display_full(board, players, msg, msg_attrs)
        should_continue = True
      elif board:
        player = players[board.turn % 2]
        if not (board.is_full() or board.is_won()):
          if isinstance(player, SimpleAIPlayer):
            # AI turn to play
            player.play_turn()
            # simulate thinking
            time.sleep(.5)
            coord_index = self.START_COORD
            should_continue = True
          else:
            if (key == curses.KEY_ENTER or key == 10 or key == 13 or key == 32):
              # Human player turn to play
              player.play_turn(coord_index)
              if isinstance(players[board.turn % 2], SimpleAIPlayer):
                should_continue = True
            else: 
              # Not setting cell, check if moving cursor              
              coord_index = self._key_to_coord(key, coord_index)

          cursor_y = 8 + board_coords[coord_index][0]
          cursor_x = self._compute_startx(self.BOARD_DIV) + 1 + board_coords[coord_index][1]
        self.display_full(board, players, msg, msg_attrs)
      else:
        self.display_partial()
      
      self._move_cursor(cursor_y, cursor_x)
      if should_continue:
        key = 0
        continue
      key = self.stdscr.getch()

  # Class attributes
  MIN_HT         = 20
  MIN_WD         = 26
  START_COORD    = 4
  KEY_HUMAN      = 104
  KEY_EASYAI     = 114
  KEY_HARDAI     = 99
  KEY_NEW_GAMES  = [KEY_HUMAN, KEY_EASYAI, KEY_HARDAI]
  DIV            = "--------------------------"
  TITLE          = "TIC-TAC-TOE"
  BOARD_ROW      = " {} | {} | {} "
  BOARD_DIV      = "---+---+---"
  SPLASH         = " To start game: h,r, or c  "
  HELP_MENU      = ["    arrow keys to move    ",
                    " enter/spacebar to place  ",
                    "    'h' vs human game     ",
                    "  'r' vs random AI game   ",
                    "   'c' vs hard AI game    ",
                    "       'q' to quit        "]

