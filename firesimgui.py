import kivy

kivy.require('1.5.1')

from kivy.app import App

from ui.simwidget import SimWidget
from ui.grabber import Grabber

class FireSimApp(App):
    def build(self):
        return SimWidget()

