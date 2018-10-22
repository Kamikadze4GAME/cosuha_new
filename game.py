
import sys
import json
from datetime import datetime

import numpy as np

from PyQt4.QtGui import QApplication, QMainWindow, QMessageBox
from PyQt4 import uic

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
try:
    import matplotlib.finance as fin
except:
    import mpl_finance as fin

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as md
#from matplotlib.ticker import MaxNLocator
plt.ion()

from game_window import Ui_gameWindow
from filename_chooser import init_fchooser

class MainWindow(Ui_gameWindow):
    def __init__(self):
        super().__init__()
        
        self.gameWindow = QMainWindow()
        self.setupUi(self.gameWindow)
        
        init_fchooser(self.fname_button, self.fname_edit, 'Dataset file')
        self.open_button.clicked.connect(self.load)
        self.run_button.clicked.connect(self.run_trade)
    
    def setupUi(self, gameWindow):
        super().setupUi(gameWindow)
        
        # a figure instance to plot on
        self.figure = Figure(tight_layout=True)

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self.plot_frame)
        
        # create an axis
        self.axis, self.ax_basecache, self.ax_altcache = \
            self.figure.subplots(3, 1, sharex='all')
        self.axis.tick_params(axis='x', direction='out', pad=8)
        self.xfmt = DateFormatter('%Y-%m-%d %H:%M')
        
        self.axis.xaxis_date()
        
        # set the layout
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.canvas)
    
    def load(self):
        try:
            with open(self.fname_edit.text()) as f:
                self.hist = json.load(f)
        except Exception as e:
            QMessageBox.critical(self.gameWindow, 'File load error', str(e))
            return
        
        self.clear()
        
        try:
            cs_width = (self.hist['t'][1] - self.hist['t'][0]) / (24*3600)
        except:
            cs_width = 1
        
        fin.candlestick_ochl(self.axis,
                              np.vstack((md.epoch2num(self.hist['t']),
                                         self.hist['o'],
                                         self.hist['c'],
                                         self.hist['h'],
                                         self.hist['l'])).T,
                              colorup='g',
                              colordown='r',
                              width=cs_width
                              )
        
        self.canvas.draw()
    
    def show(self):
        self.gameWindow.show()
    
    def clear(self):
        self.axis.clear()
        self.axis.xaxis.set_major_formatter(self.xfmt)
        self.axis.tick_params(labelbottom=True)
    
    def run_trade(self):
        pass
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
