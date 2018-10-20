
from urllib.request import urlopen, Request
from pandas import DataFrame, DatetimeIndex
import json
import time

def load_prices_history(symbol=None, resolution=None, _from=None, to=None):
    
    if symbol is None:
        symbol=945629  #bitcoin
    if resolution is None:
        resolution=15
    
    if to is None:
        to = int(time.time())
    
    if _from is None:
        _from = to - 3600 * 24 * 14
    
    hist_req = Request('https://tvc4.forexpros.com/'
                       '6a8e228b53365fe58a6196efc7b1f3ee/'
                       '1540024500/1/1/8/history?'
                       'symbol={symbol}&resolution={resolution}&'
                       'from={_from}&to={to}'.format(
                            symbol=symbol,
                            resolution=resolution,
                            _from=_from,
                            to=to
                       ),
              headers={'User-Agent':'Mozilla/5.0 '
                                    '(X11; Linux x86_64; rv:62.0) '
                                    'Gecko/20100101 Firefox/62.0'
                      }
             )
    
    jstr = urlopen(hist_req).readall().decode('utf-8')
    return json.loads(jstr)

def prices_to_DataFrame(j):
    if j['s'] != 'ok':
        raise Exception('bad history; status: {}'.format(j['s']))
    
    return DataFrame(
        index=DatetimeIndex([t*10**9 for t in j['t']]),
        data={  'Last':j['l'],
                'Open':j['o'],
                'High':j['h'],
                'Low' :j['l'],
                'Vol.':j['vo']
        }
    )

if __name__ == '__main__':
    import argparse as ap
    parser = ap.ArgumentParser()
    parser.add_argument('--from', '-f', type=int, dest='_from', help='beginning time')
    parser.add_argument('--to', '-t', type=int, help='end time')
    parser.add_argument('--symbol', '-s', type=int, help='time serie (symbol) id')
    parser.add_argument('--resolution', '-r', type=int, help='resolution in minutes')
    parser.add_argument('fname', nargs='?', help='output fname')
    args = parser.parse_args()
    
    res = args.resolution if args.resolution else 15
    
    hist = load_prices_history(_from=args._from, to=args.to,
                               symbol=args.symbol,
                               resolution=res)
    
    
    if args.fname:
        fname = args.fname
    else:
        fname = '{} - {} interval {}m.json'.format(
                    hist['t'][0],
                    hist['t'][-1],
                    res)
    with open(fname, 'w') as f:
        json.dump(hist, f)
