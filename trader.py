
from abc import ABC, abstractmethod
from pandas import Series, DatetimeIndex
import numpy as np
from matplotlib.dates import epoch2num

class Trader(ABC):
    def __init__(self, predictor, start_basecache=1000, start_altcache=0):
        self.basecache = Series(index=[0], data=[start_basecache])
        self.altcache  = Series(index=[0], data=[start_altcache])
        self.predictions= Series()
        self.predictor = predictor
        self.iter_counter = 0
        
        self.cumcache = Series()
        
    def feed(self, new_data):
        '''
        new_data = pandas.DataFrame(index = pandas.DatetimeIndex([ ... ]),
                                    columns = ['Last', 'Open', 'High', 'Low', 'Vol.'],
                                    data = ...)
        '''
        
        if len(new_data) == 0:
            return
        
        if self.iter_counter > 0 and \
           self.iter_counter not in self.cumcache.index:
            self.cumcache = self.cumcache.append(
                                Series(index=[self.iter_counter],
                                       data =[self.last_costs['Last'] * self.altcache.iloc[-1] + self.basecache.iloc[-1]])
                            )
        
        if len(new_data) > 1:
            assert self.basecache.index[-1] == self.altcache.index[-1]
            assert len(self.basecache) == len(self.altcache)
            
            prices = new_data['Last'].iloc[:-1].reindex(range(self.iter_counter+1,
                                                              self.iter_counter+len(new_data)))
            
            cumcache = prices * self.altcache.iloc[-1] + self.basecache.iloc[-1]
            
            self.cumcache = \
                self.cumcache.append(cumcache)
        
        self.predictor.feed(new_data)
        self.last_costs = new_data.iloc[-1]
        self.iter_counter += len(new_data)
    
    def move(self, time_delta):
        assert self.basecache.index[-1] == self.altcache.index[-1]
        assert len(self.basecache) == len(self.altcache)
        
        prediction = self.predictor.predictNext(time_delta)
        self.predictions = \
            self.predictions.append(
                Series( index=[self.iter_counter+1],
                        data =[prediction] ))
        
        buy = self.make_choice(prediction, time_delta)
        if -buy > self.altcache.iloc[-1]:
            buy = -self.altcache.iloc[-1]
        
        buy_cost = buy * self.last_costs['Last']
        if buy_cost > self.basecache.iloc[-1]:
            buy_cost = self.basecache.iloc[-1]
            buy = buy_cost / self.last_costs['Last']
        
        self.basecache = \
            self.basecache.append(
                Series( index=[self.iter_counter],
                        data =[self.basecache.iloc[-1] - buy_cost]))
        self.altcache = \
            self.altcache.append(
                Series( index=[self.iter_counter],
                        data =[self.altcache.iloc[-1] + buy]))
        
        self.cumcache = self.cumcache.append(
                                Series(index=[self.iter_counter],
                                       data =[self.last_costs['Last'] * self.altcache.iloc[-1] + self.basecache.iloc[-1]])
                            )
        
    @abstractmethod
    def make_choice(self, prediction, time_delta=None):
        '''
        Returns how many of altcache to buy.
        Negative values means "sell".
        '''
        return 0

def iterSerie2timeSerie(time, serie):
    return serie.reindex(
            DatetimeIndex(
                np.append(np.asarray(time),
                          [time[-1] + (time[-1] - time[-2])]
                         )[serie.index-1]*10**9) 
           )

def iterSerie2mlrow(time, serie):
    return epoch2num(np.append(np.asarray(time),
                               [time[-1] + (time[-1] - time[-2])]
                              )[serie.index-1]
                    ), np.asarray(serie)

class FearfulTrader(Trader):
    def make_choice(self, prediction, time_delta=None):
        return 0
