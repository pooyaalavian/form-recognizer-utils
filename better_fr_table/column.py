from .base import Base
from enum import Enum
from .table import Table
from .cell import Cell

class ColumnType(Enum):
    UNKNOWN='UNKNOWN'
    TEXT='TEXT'
    INTEGER='INTEGER'
    FLOAT='FLOAT'
    CURRENCY='CURRENCY'
    BOOLEAN='BOOLEAN'
    DATE='DATE'
    TIME='TIME'
    DATETIME='DATETIME'
    BLOB='BLOB'

class Column(Base):
    def __init__(self, table:Table, col_index:int):
        super().__init__()
        self.type: ColumnType = ColumnType.UNKNOWN
        self.parent_table: Table = table
        self.header_name: str = ''
        self.col_index: int = col_index
    
    def cells(self)-> list[Cell]:
        return [c for c in self.parent_table.cells if self==c.col()]

    def guess_type(self):
        all_types: dict[ColumnType, int]  = {
            ColumnType.UNKNOWN: 0,
            ColumnType.TEXT: 0,
            ColumnType.INTEGER: 0,
            ColumnType.FLOAT: 0,
            ColumnType.CURRENCY: 0,
            ColumnType.BOOLEAN: 0,
            ColumnType.DATE: 0,
            ColumnType.TIME: 0,
            ColumnType.DATETIME: 0,
            ColumnType.BLOB: 0,
        } 
        cells = self.cells()
        for c in cells:
            for t in c.guess_type():
                all_types[t] += 1
        
        for t in [ColumnType.CURRENCY, ColumnType.INTEGER, ColumnType.FLOAT,  ColumnType.BOOLEAN]:
            if all_types[t] == len(cells):
                self.type = t
                return
        
        