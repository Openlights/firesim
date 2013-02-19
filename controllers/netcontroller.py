import msgpack
import logging as log

from PySide import QtCore, QtNetwork, QtGui


class NetController(QtCore.QObject):

    ready_to_read = QtCore.Signal()

    def __init__(self, app):
        super(NetController, self).__init__()
        self.socket = None
        self.app = app
        self.init_socket()

    def init_socket(self):
        self.socket = QtNetwork.QUdpSocket(self)
        self.socket.readyRead.connect(self.read_datagrams)
        self.socket.bind(3020)
        log.info("Listening on UDP 3020")

    @QtCore.Slot()
    def read_datagrams(self):
        while self.socket.hasPendingDatagrams():
            datagram = QtCore.QByteArray()
            datagram.resize(self.socket.pendingDatagramSize())
            (datagram, sender, sport) = self.socket.readDatagram(datagram.size())
            msg = msgpack.unpackb(datagram.data())
            self.app.scenecontroller.net_set(msg[0], msg[1], msg[2], msg[3])
