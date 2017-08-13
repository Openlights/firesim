import array
import time
import numpy as np

from PyQt5.QtCore import (QObject, Qt, QPoint, QPointF, QRect, QRectF, QSizeF,
                          QMargins, pyqtSignal, pyqtSlot, pyqtProperty)
from PyQt5.QtGui import (QPainter, QColor, QFont, QPen, QFontMetrics,
                         QOpenGLVersionProfile, QSurfaceFormat,
                         QOpenGLShader, QOpenGLShaderProgram, QVector2D,
                         QVector4D, QMatrix4x4, QOpenGLBuffer)
from PyQt5.QtQuick import QQuickPaintedItem
from PyQt5.QtQml import QQmlListProperty

from controllers.canvascontroller import CanvasController
from models.pixelgroup import *


class CanvasView(QQuickPaintedItem):
    """
    CanvasView is responsible for drawing the simulation scene and the GUI
    chrome related to manipulating the scene.
    """

    ENABLE_OPENGL = True

    def __init__(self, parent):
        super(CanvasView, self).__init__()
        self.parent = parent
        self.controller = CanvasController(self)
        self._model = self.controller.model

        self.setRenderTarget(QQuickPaintedItem.FramebufferObject)
        self.setFillColor(QColor(0, 0, 0, 255))
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setAcceptHoverEvents(True)
        self.forceActiveFocus()

        #self.renderer = CanvasRenderer()

        self.cursor_loc = None

        self.gl = None

        self._last_render_times = []
        self._fps = 0

        self.windowChanged.connect(self.on_window_changed)

    selection_changed = pyqtSignal()
    model_changed = pyqtSignal()

    @pyqtProperty(QObject, notify=model_changed)
    def model(self):
        return self._model

    @model.setter
    def model(self, val):
        self._model = val

    @pyqtProperty(QQmlListProperty, notify=selection_changed)
    def selection(self):
        return QQmlListProperty(PixelGroup, self, self.controller.selected)

    def geometryChanged(self, old_rect, new_rect):
        pass

    def on_window_changed(self, window):
        if self.ENABLE_OPENGL:
            self.init_opengl()

    @pyqtSlot()
    def on_resize(self):
        pass

    @pyqtSlot()
    def init_opengl(self):
        ctx = self.window().openglContext()
        if ctx is not None:
            v = QOpenGLVersionProfile()
            v.setVersion(2, 0)
            self.gl = ctx.versionFunctions(v)
            self.gl.initializeOpenGLFunctions()
            print("Initialized OpenGL rendering")
        else:
            print("No opengl context")
            return

        vertex_shader = '''
#version 120
attribute highp vec4 posAttr;
attribute lowp vec4 colAttr;
varying lowp vec4 col;

void main() {
    col = colAttr;
    gl_Position = posAttr;
}
 '''

        fragment_shader = '''
#version 120

vec4 blur5(sampler2D image, vec2 uv, vec2 resolution, vec2 direction) {
    vec4 color = vec4(0.0);
    vec2 off1 = vec2(1.3333333333333333) * direction;
    color += texture2D(image, uv) * 0.29411764705882354;
    color += texture2D(image, uv + (off1 / resolution)) * 0.35294117647058826;
    color += texture2D(image, uv - (off1 / resolution)) * 0.35294117647058826;
    return color;
}

void main (void)
{
    gl_FragColor = vec4(0, 0, 0, 0);
}
'''

        self.program = QOpenGLShaderProgram(self)

        self.program.addShaderFromSourceCode(QOpenGLShader.Vertex,
                vertex_shader)

        self.program.addShaderFromSourceCode(QOpenGLShader.Fragment,
                fragment_shader)

        self.program.link()

        self.pos_attr = self.program.attributeLocation('posAttr')

        self.vertices = np.array([
                 0.0,  0.707,
                -0.5, -0.5,
                 0.5, -0.5
            ], dtype=np.float32)

        self.buf = QOpenGLBuffer()
        self.buf.create()
        self.buf.bind()
        self.buf.setUsagePattern(QOpenGLBuffer.StaticDraw)
        self.buf.allocate(self.vertices, self.vertices.nbytes)

        self.buf.release()


    def scene_to_canvas(self, coord):
        """
        Returns a scene coordinate tuple (x, y) transformed to canvas space
        """
        canvas_width, canvas_height = self.model.scene.extents
        scale_x = self.width() / canvas_width
        scale_y = self.height() / canvas_height
        scale = min(scale_x, scale_y)
        # TODO: add offets to center the view when aspect ratio is wrong
        scaled = (coord[0] * scale, coord[1] * scale)
        return scaled

    def canvas_to_scene(self, coord):
        """
        Returns a canvas coordinate tuple (x, y) transformed to scene space
        """
        canvas_width, canvas_height = self.model.scene.extents
        scale_x = canvas_width / self.width()
        scale_y = canvas_height / self.height()
        scale = max(scale_x, scale_y)
        # TODO: add offets to center the view when aspect ratio is wrong
        scaled = (coord[0] * scale, coord[1] * scale)
        return scaled

    def paint(self, painter):

        start = time.time()

        if self.ENABLE_OPENGL:
            if self.gl is not None:
                painter.beginNativePainting()

                gl = self.gl
                ratio = self.window().devicePixelRatio()
                w = self.window().width() * ratio
                h = self.window().height() * ratio

                gl.glViewport(0, 0, w, h)
                gl.glMatrixMode(gl.GL_PROJECTION)
                gl.glLoadIdentity()

                gl.glOrtho(0, w, h, 0, -10, 10)

                gl.glMatrixMode(gl.GL_MODELVIEW)
                gl.glLoadIdentity()

                gl.glEnable(gl.GL_SCISSOR_TEST)
                gl.glScissor(0, 0, w, h)

                gl.glClearColor(0.0, 0.0, 0.0, 1.0)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)

                gl.glPointSize(15.0 if self.model.blurred else 5.0)

                gl.glBegin(gl.GL_POINTS)

                for pg in self.model.scene.pixel_groups:
                    if type(pg) == LinearPixelGroup:
                        colors = self.model.color_data.get(pg.strand, None)
                        if colors is None:
                            continue

                        colors = colors[pg.offset:pg.offset + pg.count]

                        x1, y1 = self.scene_to_canvas(pg.start)
                        x2, y2 = self.scene_to_canvas(pg.end)

                        y1 = self.height() - y1
                        y2 = self.height() - y2
                        dx = (x2 - x1) / pg.count
                        dy = (y2 - y1) / pg.count

                        x, y = x1, y1
                        for i in range(pg.count):

                            r, g, b = colors[i]
                            gl.glColor4f(r / 255, g / 255, b / 255, 1)
                            gl.glVertex2f(x, y)

                            x += dx
                            y += dy

                gl.glEnd()

                gl.glDisable(gl.GL_SCISSOR_TEST)

                painter.endNativePainting()
            else:
                if self.window().openglContext() is not None:
                    self.init_opengl()

        painter.setRenderHint(QPainter.Antialiasing)

        selected = [pg for pg in self.model.scene.pixel_groups
                    if pg.selected or pg.hovering]
        s = set(selected)
        unselected = [pg for pg in self.model.scene.pixel_groups if pg not in s]

        for pg in unselected:
            self.painters[pg.__class__](self, painter, pg)

        for pg in selected:
            self.painters[pg.__class__](self, painter, pg)

        self._render_pixels_this_frame = False

        # Debug - cursor drawing
        # if self.cursor_loc is not None:
        #     x, y = self.cursor_loc.x(), self.cursor_loc.y()
        #     painter.setPen(QPen(QColor(255, 255, 0, 255),
        #                               1,
        #                               Qt.SolidLine,
        #                               Qt.RoundCap,
        #                               Qt.RoundJoin))
        #     painter.drawLine(QPointF(x - 5, y),QPointF(x + 5, y))
        #     painter.drawLine(QPointF(x, y - 5),QPointF(x, y + 5))

        try:
            frame_time = 1.0 / (time.time() - start)
        except ZeroDivisionError:
            frame_time = 0

        if len(self._last_render_times) < 20:
            self._last_render_times.append(frame_time)
        else:
            self._fps = sum(self._last_render_times) / 20
            self._last_render_times.pop(0)

        # Stats
        f = QFont()
        f.setPointSize(8)
        painter.setFont(f)
        painter.setPen(QColor(160, 150, 150, 200))
        painter.drawText(8, 16, "Net %d pps" % self.gui.netcontroller.fps)
        painter.drawText(8, 32, "GUI %d fps" % self._fps)

    def _paint_linear_pixel_group(self, painter, pg):
        x1, y1 = self.scene_to_canvas(pg.start)
        x2, y2 = self.scene_to_canvas(pg.end)

        ax, ay = min(x1, x2), min(y1, y2)
        bx, by = max(x1, x2), max(y1, y2)

        if self.model.design_mode:
            # Bounding box (debug)
            # c = QColor(255, 0, 255, 250) if pg.selected else QColor(255, 255, 0, 250)
            # if pg.selected:
            #     self._draw_bounding_box(painter, pg, c)

            if pg.selected or pg.hovering:
                painter.setPen(QPen(QColor(100, 100, 255, 170),
                                          6,
                                          Qt.SolidLine,
                                          Qt.RoundCap,
                                          Qt.RoundJoin))
                painter.drawLine(QPointF(x1, y1),QPointF(x2, y2))

            painter.setPen(QPen(QColor(100, 100, 100, 200),
                                      2,
                                      Qt.SolidLine,
                                      Qt.RoundCap,
                                      Qt.RoundJoin))
            painter.drawLine(QPointF(x1, y1),QPointF(x2, y2))

            if pg.selected:
                self._draw_drag_handle(painter, pg.start_handle)
                self._draw_drag_handle(painter, pg.end_handle)

            if pg.selected or pg.hovering:
                self._draw_address(painter, pg, (0, 0))

    painters = {
        LinearPixelGroup: _paint_linear_pixel_group
    }

    def _draw_bounding_box(self, painter, pg, color):
        x, y, w, h = pg.bounding_box()
        x, y = self.scene_to_canvas((x, y))
        w, h = self.scene_to_canvas((w, h))
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.setPen(QPen(color, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(x, y, w, h)

    def _draw_drag_handle(self, painter, handle):
        x, y = self.scene_to_canvas(handle.pos)

        if handle.dragging:
            color = QColor(50, 255, 100, 150)
            rect = QRectF(x - 5, y - 5, 10, 10)
        elif handle.hovering:
            color = QColor(50, 100, 255, 150)
            rect = QRectF(x - 5, y - 5, 10, 10)
        else:
            color = QColor(200, 200, 200, 200)
            rect = QRectF(x - 4, y - 4, 8, 8)

        painter.setPen(QPen(color, 1, Qt.SolidLine))
        painter.setBrush(color)
        painter.drawRoundedRect(rect, 2, 2)

    def _draw_address(self, painter, pg, offset):
        x1, y1 = self.scene_to_canvas(pg.start)
        x2, y2 = self.scene_to_canvas(pg.end)
        label_pos = QPoint((x1 + x2) / 2 + offset[0], (y1 + y2) / 2 + offset[1])

        label_font = QFont()
        label_font.setPointSize(8)
        painter.setFont(label_font)

        label_string = "%d:%d" % (pg.strand, pg.offset)
        fm = QFontMetrics(label_font)
        text_rect = fm.boundingRect(label_string)
        text_rect += QMargins(5, 2, 5, 2)
        label_rect = QRect(label_pos - QPoint(12, 7), text_rect.size())

        painter.setBrush(QColor(128, 64, 128, 220))
        painter.setPen(QColor(100, 100, 100, 100))
        painter.drawRoundedRect(label_rect, 5, 5)
        painter.setPen(QColor(255, 255, 255, 255))
        painter.drawText(label_rect, Qt.AlignCenter, label_string)

    def hoverMoveEvent(self, event):
        self.controller.on_hover_move(event)

    def mouseMoveEvent(self, event):
        self.controller.on_mouse_move(event)

    def mousePressEvent(self, event):
        self.controller.on_mouse_press(event)

    def mouseReleaseEvent(self, event):
        self.controller.on_mouse_release(event)

    def keyPressEvent(self, event):
        event.accept()
        self.controller.on_key_press(event)

    def keyReleaseEvent(self, event):
        event.accept()
        self.controller.on_key_release(event)


class CanvasRenderer(QObject):

    def __init__(self):
        super(QObject, self).__init__()

    @pyqtSlot()
    def paint(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
