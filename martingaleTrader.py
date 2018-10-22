
from trader import Trader

class MartingaleTrader(Trader):
    def __init__(self, *args, min_bid=0.01, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_bid = min_bid
        self.lost = 0
        self.prev_altcache_cost = 0
    
    def make_choice(self, prediction, time_delta=None):
        cur_price = self.last_costs['Last']
        if self.lost < 0:
            self.lost = 0
        
        if prediction <= cur_price:
            self.prev_altcache_cost = 0
            return - (self.altcache.iloc[-1]*cur_price)
        else:
            cur_altcache_cost = self.altcache.iloc[-1]*cur_price
            
            self.lost += self.prev_altcache_cost - cur_altcache_cost
            bid = max(self.min_bid, self.lost*2)
            
            self.prev_altcache_cost = cur_altcache_cost
            return bid
