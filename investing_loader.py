
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from pandas import DataFrame
import re
from datetime import datetime

req = Request('https://www.investing.com/crypto/'
              'currency-pairs?c1=189&c2=12',
              headers={'User-Agent':'Mozilla/5.0 '
                                    '(X11; Linux x86_64; rv:62.0) '
                                    'Gecko/20100101 Firefox/62.0'
                      }
             )

def load_prices_page():
    return urlopen(req).read()

class Prices:
    def __init__(self, page=None, date_time=None):
        
        if date_time is None or page is None:
            date_time = datetime.now()
        if page is None:
            page = load_prices_page()
        
        self.date_time = date_time
        
        self.page = page
        html_table = BeautifulSoup(page)\
                    .find('table', id='crypto_currencies_189')
        
        head = html_table.find('thead')
        columns = [ tag.text for tag in head('th')[1:-1] ]
        ex_name_columns = list(filter(lambda i: columns[i] == 'Exchange', range(len(columns))))
        if len(ex_name_columns) != 1:
            raise Exception("Bad number of columns with exchange's name.",
                            ex_name_columns)
        ex_name_column = ex_name_columns[0]
        del ex_name_columns
        del columns[ex_name_column]
        
        def remove_spaces(s):
            s = re.sub(r'^\s+', '', s)
            s = re.sub(r'\s+$', '', s)
            return s
        columns = [remove_spaces(s) for s in columns]
        
        rows  = []
        row_index = []
        for row in html_table.find('tbody')('tr'):
            fields = row('td')
            row_index.append(fields[ex_name_column+1].text)
            rows.append([f.text for f in fields[1:ex_name_column+1] + fields[ex_name_column+2:-1]])
        
        self.table = DataFrame(data=rows, columns=columns, index=row_index, dtype=str)
    
    @classmethod
    def vol_conv(s):
        m = re.match(r'([\d.]+)\s*([KkMmGg])\s*$', s)
        num = float(m.group(1))
        exp = m.group(2).lower()
        
        if exp == '':
            pass
        elif exp == 'k':
            num *= 1000
        elif exp == 'm':
            num *= 1000000
        elif exp == 'g':
            num *= 1000000000
        
        return num
    
    @classmethod
    def val_conv(s):
        return float(s.relace(',','')
    
    def time_conv(self, s):
        m = re.match(r'(?P<h>\d\d):(?P<m>\d\d):(?P<s>\d\d)', s)
    
    
    def __getitem__(self, key):
        serie = self.table.loc[key]
        
        vol = self.vol_conv(serie['Vol.'])



