from .base import Base
from .row import Row
from .column import Column, ColumnType
from warnings import warn
import re
from datetime import datetime


class Cell(Base):
    def __init__(self, rows: list[Row], cols: list[Column], content: str, *, colspan: int = 1, rowspan: int = 1):
        super().__init__()
        self.rows: list[Row] = rows
        self.cols: list[Column] = cols
        self.content_raw: str = content.strip()
        self.content_numeric:str = re.sub('[^0-9\-\+\.]','',self.content_raw)
        self.colspan: int = colspan
        self.rowspan: int = rowspan
        if len(self.rows) == 0:
            raise ValueError('Cell must have at least one row')
        if len(self.cols) == 0:
            raise ValueError('Cell must have at least one column')
        if len(self.rows) != self.rowspan:
            raise ValueError(
                'Cell rowspan must be equal to the number of rows')
        if len(self.cols) != self.colspan:
            raise ValueError(
                'Cell colspan must be equal to the number of columns')

    def row(self) -> Row:
        if self.rowspan != 1:
            warn(
                f'Cell.row() called on a cell with rowspan={self.rowspan} > 1')
        return self.rows[0]

    def col(self) -> Column:
        if self.colspan != 1:
            warn(
                f'Cell.col() called on a cell with colspan={self.colspan} > 1')
        return self.cols[0]

    def get_type(self):
        return self.col().type

    def content(self) -> str | int | float | bool | datetime:
        t = self.col().type
        if t == ColumnType.TEXT:
            return self.content_raw
        if t == ColumnType.INTEGER:
            return int(self.content_raw)
        if t == ColumnType.FLOAT:
            return float(self.content_raw)
        if t == ColumnType.CURRENCY:
            return float(self.content_raw.replace('$', '').replace(',', ''))
        if t == ColumnType.BOOLEAN:
            c = self.content_raw.lower()
            ans = (
                c == 'true'
                or c == 'yes'
                or c == '1'
                or c == ':selected:'
            )
            return ans
        if t == ColumnType.DATE:
            warn('NotImplemented: Cell.content() for ColumnType.DATE')
            return self.content_raw
        if t == ColumnType.DATETIME:
            warn('NotImplemented: Cell.content() for ColumnType.DATETIME')
            return self.content_raw
        if t == ColumnType.TIME:
            warn('NotImplemented: Cell.content() for ColumnType.TIME')
            return self.content_raw
        if t == ColumnType.UNKNOWN:
            return self.content_raw
        raise NotImplementedError(f'Unimplemented ColumnType: {t.value}')

    def guess_type(self) -> list[ColumnType]:
        ans: list[ColumnType] = []
        c = self.content_raw.lower()
        if (
            c == 'true' or c == 'false'
            or c == 'yes' or c == 'no'
            or c == '1' or c == '0'
            or c == ':selected:' or c == ':unselected:'
        ):
            ans.append(ColumnType.BOOLEAN)
        currency = None
        for u in ['$', '€', '£', '¥', 'USD', 'EUR', 'GBP', 'JPY']:
            if u in c:
                currency = u
                break
        if currency is not None:
            try:
                f = float(c.replace(currency, '').replace(',', ''))
                ans.append(ColumnType.CURRENCY)
            except:
                pass

        try:
            i = int(c)
            ans.append(ColumnType.INTEGER)
        except:
            pass
        try:
            f = float(c)
            ans.append(ColumnType.FLOAT)
        except:
            pass

        ans.append(ColumnType.TEXT)
        return ans
