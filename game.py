
import sys, traceback
import json
from datetime import datetime

import numpy as np

from PyQt4.QtGui import QApplication, QMainWindow, QMessageBox
from PyQt4 import uic

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.dates import epoch2num
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
from predictor import StupidPredictor
from trader import FearfulTrader, iterSerie2mlrow
from investing_loader import prices_to_DataFrame

class MainWindow(Ui_gameWindow):
    def __init__(self):
        super().__init__()
        
        self.hist = None
        self.lines = []
        
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
        
        # set the layout
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.canvas)
        
        self.reposition()
    
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
        self.axis        .clear()
        self.ax_basecache.clear()
        self.ax_altcache .clear()
        self.reposition()
        
        self.trader = None
    
    def reposition(self):
        self.axis           .xaxis.set_major_formatter(self.xfmt)
        self.axis           .tick_params(labelbottom=True)
        self.ax_basecache   .xaxis.set_major_formatter(self.xfmt)
        self.ax_basecache   .tick_params(labelbottom=True)
        self.ax_altcache    .xaxis.set_major_formatter(self.xfmt)
        self.ax_altcache    .tick_params(labelbottom=True)
        
        self.axis           .xaxis_date()
        self.ax_basecache   .xaxis_date()
        self.ax_altcache    .xaxis_date()
        
        self.axis           .legend()
        self.ax_basecache   .legend()
        self.ax_altcache    .legend()
        
        if self.hist is not None:
            a = epoch2num(self.hist['t'][0 ])
            b = epoch2num(self.hist['t'][-1])
            d = (b-a)*0.05
            self.axis.set_xlim(a-d, b+d)
        
        
        self.canvas.draw()
        
    def run_trade(self):
        if self.hist is None or len(self.hist['t']) == 0:
            return
            
        if self.predictor_combo.currentText() == 'StupidPredictor':
            predictor_class = StupidPredictor
        elif self.predictor_combo.currentText() == 'RandomPredictor':
            from predictor import RandomPredictor
            predictor_class = RandomPredictor
        else:
            return
        
        predictor = predictor_class()
        
        if self.trader_combo.currentText() == 'FearfulTrader':
            trader_class = FearfulTrader
        elif self.trader_combo.currentText() == 'MartingaleTrader':
            from martingaleTrader import MartingaleTrader
            trader_class = MartingaleTrader
        else:
            return
        
        self.trader = trader_class( predictor,
                                    self.basecache_spin.value(),
                                    self.altcache_spin.value(),
                                    min_bid = self.min_bid_spin.value()  )
        
        hist_df = prices_to_DataFrame(self.hist)
        for i in range(len(hist_df)):
            self.trader.feed(hist_df[i:i+1])
            try:
                dt = self.hist['t'][i+1] - self.hist['t'][i]
            except IndexError:
                dt = self.hist['t'][-1] - self.hist['t'][-2]
            self.trader.move(dt)
        
        for l in self.lines:
            try:
                l.remove()
            except Exception:
                traceback.print_exc()
        
        self.lines = []
        
        self.lines.extend(
            self.axis.plot(
                *iterSerie2mlrow(self.hist['t'], self.trader.predictions),
                label='prediction', color='C2')
        )
        self.lines.extend(
            self.ax_basecache.plot(
                *iterSerie2mlrow(self.hist['t'], self.trader.basecache),
                label='basecache', color='C0')
        )
        self.lines.extend(
            self.ax_basecache.plot(
                *iterSerie2mlrow(self.hist['t'], self.trader.cumcache),
                label='cumcache', color='C1')
        )
        self.lines.extend(
            self.ax_altcache.plot(
                *iterSerie2mlrow(self.hist['t'], self.trader.altcache),
                label='altcache', color='C0')
        )
        
        self.reposition()

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
