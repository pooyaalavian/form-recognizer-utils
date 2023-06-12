from azure.ai.formrecognizer import AnalyzeResult, DocumentTable, DocumentTableCell
from .exceptions import OutOfBoundsException


class SimpleRow:
    def __init__(self, parent: 'SimpleTable'):
        self._parent = parent
        pass 
    
    def id(self)->int:
        return self._parent.rows.index(self)
    
    def cells(self)->list['SimpleCell']:
        return self._parent.cells[self.id()]

class SimpleCol:
    def __init__(self, parent: 'SimpleTable'):
        self._parent = parent
        pass 
    
    def id(self)->int:
        return self._parent.cols.index(self)
    
    def cells(self)->list['SimpleCell']:
        id = self.id()
        return [row[id] for row in self._parent.cells]
    
class SimpleCell:
    def __init__(self, parent: 'SimpleTable', original_cell: DocumentTableCell):
        self._parent = parent
        self._cell = original_cell
        pass 
    
class SimpleTable:
    '''SimpleTable is a table whose cells are all 1x1 span.
    
    Initialize with a FormRecognizer table [DocumentTable].
    self.grid[i][j] will return the cell at row i, col j. 
    
    If the algorithm detects header row is not the first row, but row r,
    then self.grid[i][j] returns the cell originally at position [i+r][j].
    If you ask for i>n_rows-r, you get an OutOfBoundsException.
    
    If a column is all empty, it will be dropped.
    If a row is all empty, it will be dropped.
    '''
    def __init__(self, fr_table:DocumentTable):
        self._fr_table_ = fr_table
        if not self.is_simple_table():
            raise ValueError('This table is not a simple table')
        
        self.n_rows = fr_table.row_count
        self.n_cols = fr_table.column_count
        self.valid_rows:list[int] = []
        self.valid_cols:list[int] = []
        
        self._all_rows: list[SimpleRow] = [SimpleRow(self) for i in range(self.n_rows)]
        self._all_cols: list[SimpleCol] = [SimpleCol(self) for j in range(self.n_cols)]
        self._all_cells: list[list[SimpleCell]]=[]
        self.extract_grid()
        return 
        
    def is_simple_table(self)->bool:
        cells = self._fr_table_.cells
        for c in cells:
            if c.column_span is not None and c.column_span>1:
                return False
            if c.row_span is not None and c.row_span>1:
                return False 
        return True
    
    def extract_grid(self):
        for r in self.rows:
            tmp = []
            for c in self.cols:
                tmp.append(None)
            self.cells.append(tmp)
                
        for cell in  self._fr_table_.cells:
            if self.cells[cell.row_index, cell.column_index] is not None:
                raise ValueError(f'Rewriting a cell at [{cell.row_index}, {cell.column_index}]')
            self.cells[cell.row_index, cell.column_index] = SimpleCell(self,cell)
        return 
        
    def find_header_row(self):
        self.header_row:SimpleRow = None
        for row in self.rows:
            if row.is_header():
                self.header_row = row
                break 
        if self.header_row is None:
            self.header_row = self.rows[0]
        
    def row(self, *, row:SimpleRow=None, id:int=None):
        if row is not None:
            self._all_rows