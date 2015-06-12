import time
import logging as log
import zmq

from PySide import QtCore, QtNetwork


class NetController(QtCore.QObject):

    ready_to_read = QtCore.Signal()
    data_received = QtCore.Signal(list)
    start = QtCore.Signal()

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

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:3020")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, u"")

        self.start.connect(self.run)

    @QtCore.Slot()
    def run(self):
        while self.running:
            packets = self.socket.recv_multipart()
            for packet in packets:
                self.data_received.emit(packet)
                self.packets += 1
            QtCore.QCoreApplication.processEvents()

    def frame_started(self):
        self.in_frame = True

    @QtCore.Slot()
    def frame_complete(self):
        self.in_frame = False
        self.updates += 1

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
