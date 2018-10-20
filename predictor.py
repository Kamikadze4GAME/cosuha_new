
from abc import ABC, abstractmethod

class AbstractPredictor(ABC):
    '''
    Прогнозує наступну ціну на основі історії.
    Історія "згодовується" по частинам функцією feed().
    predictNext повертає прогноз на один крок вперед
    '''
    @abstractmethod
    def predictNext(time_delta):
        '''
        time_delta - На скільки секунд вперед робиться прогноз.
                     Цей параметр можна ігнорити.
        '''
        pass
    
    @abstractmethod
    def feed(new_data):
        '''
        new_data = pandas.DataFrame(index = pandas.DatetimeIndex([ ... ]),
                                    columns = ['Last', 'Open', 'High', 'Low', 'Vol.'],
                                    data = ...)
        '''
        pass
