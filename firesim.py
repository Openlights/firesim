import sys
from PySide import QtCore, QtGui, QtDeclarative


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    view = QtDeclarative.QDeclarativeView()
    url = QtCore.QUrl('ui/qml/firesimgui.qml')
    view.setSource(url)
    view.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
    view.show()
    sys.exit(app.exec_())