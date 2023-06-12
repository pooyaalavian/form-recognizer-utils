from .base import Base
from .row import Row
from .column import Column
from .cell import Cell

class Table(Base):
    def __init__(self):
        super().__init__()
        self.rows: list[Row] = []
        self.cols: list[Column] = []
        self.cells: list[Cell] = []
        pass