import random
import math
from abc import ABC, abstractmethod


class Player(ABC):
  def __init__(self, id, board, desc):
    self.id = id
    self.board = board
    self.desc = desc

  @abstractmethod
  def play_turn(self, *args):
    pass


class HumanPlayer(Player):
  def __init__(self, id, board):
    super().__init__(id, board, "Human ({})".format(id))

  def play_turn(self, id):
    self.board.set_cell(id, self.id)
    return id


class SimpleAIPlayer(Player):
  """Naive AI that randomly plays an open cell."""
  def __init__(self, id, board, desc=None):
    if desc is None:
      desc = 'Easy AI ({})'.format(id)
    super().__init__(id, board, desc)
    
  def play_turn(self):
    cells = self.board.open_cells()
    if cells:
      i = cells[random.randint(0, len(cells)-1)]
      self.board.set_cell(i, self.id)


class HardAIPlayer(SimpleAIPlayer):
  def __init__(self, id, board, other):
    super().__init__(id, board, 'Hard AI ({})'.format(id))
    self.oplayer = other

  def play_turn(self, *args):
    if self.board.turn < 2:
      if self.board.is_empty(4):
        self.board.set_cell(4, self.id)
        return 4
      else:
        self.board.set_cell(0, self.id)
        return 0
    # More then a couple of turns already
    # do minimax to get optimal placement
    _, i = self.minimax(True)
    self.board.set_cell(i, self.id) 
    return i

  def minimax(self, is_max):
    """Return the max score and index to select.

    Minimax implementation that maximizes specifically 
    for this player. This implementation adds a depth 
    utility to help ensure shorter paths are preferred over
    longer (i.e, earlier vs further outcomes into future).
    
    We also hack it a bit to return the id of cells with 
    maximal value, vs having the caller also keeping track
    of max value/index.
    """
    if self.board.is_won():
      depth = self.board.turn
      return ((10-depth,None) 
        if self.board.cells[self.board.wonset[0]] == self.id 
        else (depth-10,None))
    elif self.board.is_full():
      return 0,None

    m_index = None
    m_score, val = ((-math.inf,self.id) if is_max else (math.inf,self.oplayer.id))

    for i in self.board.open_cells():
      self.board.set_cell(i, val)
      score, index = self.minimax(not is_max)
      self.board.clear_cell(i)
      if ((is_max and m_score < score) or 
          ((not is_max) and m_score > score)):
        m_score = score
        m_index = i
    return m_score, m_index


