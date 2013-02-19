import msgpack
import signal
import sys

from PySide import QtCore, QtNetwork


class TestServer(QtCore.QObject):

    ready_to_read = QtCore.Signal()

    def __init__(self):
        super(TestServer, self).__init__()
        self.socket = None
        self.timer = None

    def init_socket(self):
        self.socket = QtNetwork.QUdpSocket(self)
        #self.socket.bind(QtNetwork.QHostAddress.LocalHost, 3020)
        self.socket.readyRead.connect(self.read_datagrams)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.demo_write)
        self.timer.start(100)

    @QtCore.Slot()
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

    @QtCore.Slot()
    def demo_write(self):
        self.write([-1, -1, -1, 255, 0, 255])

def sigint_handler(signal, frame):
    global app
    app.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    app = QtCore.QCoreApplication(["testserver"])
    print "Press Ctrl-C to quit"
    nc = TestServer()
    nc.init_socket()
    app.exec_()
