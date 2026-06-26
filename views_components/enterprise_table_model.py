from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any, Dict

class EnterpriseTableModel(QAbstractTableModel):
    def __init__(self, data: List[Dict[str, Any]], headers: List[str], translated_headers: List[str] = None, parent=None):
        super().__init__(parent)
        self._data = data
        self._headers = headers
        self._translated_headers = translated_headers or headers

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            row_data = self._data[index.row()]
            # We assume keys in dict match order of headers or use mapping?
            # Better: use explicit key mapping
            key = self._headers[index.column()]
            return str(row_data.get(key, ""))

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section < len(self._translated_headers):
                return self._translated_headers[section]
            return self._headers[section]
        return None

    def update_data(self, new_data: List[Dict[str, Any]]):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()
