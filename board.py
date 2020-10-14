class Board:
  def __init__(self):
    self.cells = [self.EMPTY_CELL] * self.NUM_CELLS
    self.wonset = None
    self.turn = 0 # count of turns taken

  def open_cells(self):
    """Returns list of ids for open cells.
    Note: board is internally represented 
    by 1D array of cells."""
    return [i for i in range(self.NUM_CELLS) if self.is_empty(i)]

  def is_won(self):
    """Return True if game is won."""
    return self.wonset is not None

  def is_full(self):
    """Return True if board is full."""
    return self.NUM_CELLS == self.turn

  def is_empty(self, i):
    return self.cells[i] == self.EMPTY_CELL
  
  def set_cell(self, i, val):
    """Set the given value for selected cell,
    return True if success (e.g False if cell 
    not empty). Internally calculate the winning 
    move and save the winning set of cells."""
    if not self.is_empty(i):
      return False
    self.cells[i] = val
    self.turn += 1
    if self.turn >= 5:
      # Enough turns for possible winner
      for s in self.WIN_SETS[i]:
        if (val == self.cells[s[0]]
          and val == self.cells[s[1]]
          and val == self.cells[s[2]]):
          self.wonset = s
    return True

  def clear_cell(self, i):
    """Clear the cell at given id"""
    if not self.is_empty(i):
      self.cells[i] = self.EMPTY_CELL
      self.turn -= 1
      if self.wonset and i in self.wonset:
        self.wonset = None
  
  def reset(self):
    self.cells = [self.EMPTY_CELL] * self.NUM_CELLS
    self.wonset = None
    self.turn = 0 # count of turns taken

  def __str__(self):
    s = []
    for i in [0,3,6]:
      s.append(' {} | {} | {} '.format(self.cells[i], self.cells[i+1], self.cells[i+2]))
      s.append('---+---+---')
    return "\n".join(s[:-1])

  NUM_CELLS = 9
  EMPTY_CELL = ' '
  # Like an adjacency list for each cell
  WIN_SETS = [
    [(0,1,2),(0,3,6),(0,4,8)],
    [(0,1,2),(1,4,7)],
    [(0,1,2),(2,5,8),(2,4,6)],
    [(3,4,5),(0,3,6)],
    [(0,4,8),(1,4,7),(2,4,6),(3,4,5)],
    [(2,5,8),(3,4,5)],
    [(0,3,6),(6,7,8),(2,4,6)],
    [(7,4,1),(6,7,8)],
    [(8,4,0),(2,5,8),(6,7,8)]]
