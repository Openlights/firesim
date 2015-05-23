import time
import logging as log

from PySide import QtCore, QtNetwork


class NetController(QtCore.QObject):

    ready_to_read = QtCore.Signal()
    data_received = QtCore.Signal()

    def __init__(self, app):
        super(NetController, self).__init__()
        self.socket = None
        self.app = app
        self.updates = 0
        self.packets = 0
        self.in_frame = False
        self.running = True
        self.last_time = time.clock()
        self.socket = QtNetwork.QUdpSocket(self)
        self.socket.readyRead.connect(self.read_datagrams)
        self.socket.bind(3020, QtNetwork.QUdpSocket.ShareAddress | QtNetwork.QUdpSocket.ReuseAddressHint)

    @QtCore.Slot()
    def read_datagrams(self):
        while self.socket.hasPendingDatagrams() and self.running:
            datagram = QtCore.QByteArray()
            datagram.resize(self.socket.pendingDatagramSize())
            (datagram, sender, sport) = self.socket.readDatagram(datagram.size())
            packet = [ord(c) for c in datagram.data()]
            self.packets += 1
            self.app.scenecontroller.process_command(packet)

    def frame_started(self):
        self.in_frame = True

    def frame_complete(self):
        self.in_frame = False
        self.updates += 1
        self.data_received.emit()

    def get_stats(self):
        dt = time.clock() - self.last_time
        if dt == 0:
            return 0
        ups = self.updates / dt
        pps = self.packets / dt
        self.last_time = time.clock()
        self.updates = 0
        self.packets = 0
        return {'pps': pps, 'ups': ups}
