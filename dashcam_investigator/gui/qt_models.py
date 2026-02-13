from PySide6 import QtCore, QtGui


class PandasTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(PandasTableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self._data.index[section])


class VideoListModel(QtCore.QAbstractListModel):
    def __init__(self, data):
        super(VideoListModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self._data[index.row()].name
        if role == QtCore.Qt.DecorationRole:
            if self._data[index.row()].flagged:
                return QtGui.QColor("red")
            else:
                return QtGui.QColor("white")

    def rowCount(self, index):
        return len(self._data)


class NavigationListModel(QtCore.QAbstractListModel):
    def __init__(self, data):
        super(NavigationListModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self._data[index.row()]

    def rowCount(self, index):
        return len(self._data)
