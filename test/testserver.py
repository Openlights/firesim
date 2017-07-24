from __future__ import print_function
from builtins import range
import msgpack
import signal
import colorsys
import math

from PyQt5 import QtCore, QtNetwork


class TestServer(QtCore.QObject):

    ready_to_read = QtCore.pyqtSignal()

    def __init__(self):
        super(TestServer, self).__init__()
        self.socket = None
        self.timer = None
        self.h = 0.0

    def init_socket(self):
        self.socket = QtNetwork.QUdpSocket(self)
        #self.socket.bind(QtNetwork.QHostAddress.LocalHost, 3020)
        self.socket.readyRead.connect(self.read_datagrams)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.demo_write)
        self.timer.start(10)

    @QtCore.pyqtSlot()
    def read_datagrams(self):
        while self.socket.hasPendingDatagrams():
            datagram = QtCore.QByteArray()
            datagram.resize(self.socket.pendingDatagramSize())
            (sender, sport) = self.socket.readDatagram(datagram.data(), datagram.size())

    def write(self, data):
        packed = msgpack.packb(data)
        datagram = QtCore.QByteArray(packed)
        self.socket.writeDatagram(datagram, QtNetwork.QHostAddress.LocalHost, 3020)
        #print "wrote %d bytes" % datagram.size()

    @QtCore.pyqtSlot()
    def demo_write(self):
        for strand in range(5):
            r, g, b = [int(255.0 * c) for c in colorsys.hsv_to_rgb(math.fmod((self.h + (0.2 * strand)), 1.0), 1.0, 1.0)]
            self.write([strand, -1, -1, r, g, b])
        self.h += 0.004

def sigint_handler(signal, frame):
    global app
    app.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    app = QtCore.QCoreApplication(["testserver"])
    print("Press Ctrl-C to quit")
    nc = TestServer()
    nc.init_socket()
    app.exec_()
