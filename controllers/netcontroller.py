from __future__ import division
from past.utils import old_div
import time
import logging as log
import zmq

from PyQt5 import QtCore, QtNetwork

USE_ZMQ = False


class NetController(QtCore.QObject):

    data_received = QtCore.pyqtSignal(list)
    start = QtCore.pyqtSignal()
    new_frame = QtCore.pyqtSignal(dict)

    def __init__(self, app):
        super(NetController, self).__init__()
        self.context = None
        self.socket = None
        self.app = app
        self.updates = 0
        self.packets = 0
        self.in_frame = False
        self.running = True
        self.last_time = time.clock()
        self._frame_times = []
        self._frame_start_time = 0.0
        self._frame_data = {}
        self.fps = 0

        if USE_ZMQ:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.SUB)
            self.socket.connect("tcp://localhost:3020")
            self.socket.setsockopt_string(zmq.SUBSCRIBE, u"")
            self.start.connect(self.run)
        else:
            self.socket = QtNetwork.QUdpSocket(self)
            self.socket.readyRead.connect(self.read_datagrams)
            self.socket.bind(3020, QtNetwork.QUdpSocket.ShareAddress | QtNetwork.QUdpSocket.ReuseAddressHint)

    @QtCore.pyqtSlot()
    def read_datagrams(self):
        while self.socket.hasPendingDatagrams():
            datagram = QtCore.QByteArray()
            datagram.resize(self.socket.pendingDatagramSize())
            (datagram, sender, sport) = self.socket.readDatagram(datagram.size())
            # TODO(JE): is this the best way for Py2/Py3 compatability?
            if type(datagram) is bytes:
                packet = [c for c in datagram]
            else:
                packet = [ord(c) for c in datagram.data()]
            self.packets += 1
            self.process_packet(packet)

    @QtCore.pyqtSlot()
    def run(self):
        while self.running:
            packets = self.socket.recv_multipart()
            for packet in packets:
                self.data_received.emit(packet)
                self.packets += 1
            QtCore.QCoreApplication.processEvents()

    def frame_started(self):
        self.in_frame = True

    @QtCore.pyqtSlot()
    def frame_complete(self):
        self.in_frame = False
        self.updates += 1

    def process_packet(self, packet):
        cmd = chr(packet[0])
        datalen = 0

        # Begin frame
        if cmd == 'B':
            self._frame_start_time = time.time()
            self.frame_started()

        # Unpack strand pixel data
        elif cmd == 'S':
            strand = packet[1]
            datalen = (packet[3] << 8) + packet[2]
            data = [c for c in packet[4:]]
            self._frame_data[strand] = data

        # End frame
        elif cmd == 'E':
            try:
                fps = 1.0 / (time.time() - self._frame_start_time)
            except ZeroDivisionError:
                fps = 0

            if len(self._frame_times) < 50:
                self._frame_times.append(fps)
            else:
                self.fps = sum(self._frame_times) / 50
                self._frame_times.pop(0)

            self.new_frame.emit(self._frame_data)

        else:
            log.error("Malformed packet of length %d!" % len(packet))
