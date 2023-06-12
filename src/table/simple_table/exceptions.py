

class OutOfBoundsException(Exception):
    def __init__(self, *, index:int, is_row_index=False, is_col_index=False):
        self.type = 'Table'
        if is_row_index and not is_col_index:
            self.type='Row'
        if not is_row_index and is_col_index:
            self.type='Column'
        if is_row_index and is_col_index:
            self.type='Row&Column' 
        super().__init__(f'{self.type}IndexOutOfBounds: {index}')
