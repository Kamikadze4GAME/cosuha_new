
from abc import ABC, abstractmethod
import random

class AbstractPredictor(ABC):
    '''
    Прогнозує наступну ціну на основі історії.
    Історія "згодовується" по частинам функцією feed().
    predictNext повертає прогноз на один крок вперед
    '''
    @abstractmethod
    def predictNext(self, time_delta):
        '''
        time_delta - На скільки секунд вперед робиться прогноз.
                     Цей параметр можна ігнорити.
        '''
        pass
    
    @abstractmethod
    def feed(self, new_data):
        '''
        new_data = pandas.DataFrame(index = pandas.DatetimeIndex([ ... ]),
                                    columns = ['Last', 'Open', 'High', 'Low', 'Vol.'],
                                    data = ...)
        '''
        pass

class StupidPredictor(AbstractPredictor):
    def feed(self, new_data):
        self.last_price = new_data['Last'].iloc[-1]
    
    def predictNext(self, time_delta):
        return self.last_price

class RandomPredictor(StupidPredictor):
    def predictNext(self, time_delta):
        return random.gauss(self.last_price, 1)
