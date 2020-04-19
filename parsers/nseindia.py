import requests
import pandas as pd
import random
import datetime

headers = {'User-Agent': 'Mozilla/5.0'}


def get_quotes():
    session = requests.Session()

    data = session.get('https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json',headers=headers,verify=False)
    js = data.json()
    quotes = {k['symbol']: float(k['ltP'].replace(",", '')) for k in js['data']}
    quotes_time = datetime.datetime.strptime(js['time'],'%b %d, %Y %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S+0530')
    return dict(quotes=quotes,quotes_time=quotes_time)

def pull_other_info(security):
    URL_TEMPLATE = 'https://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/ajaxFOGetQuoteJSON.jsp?underlying=%(symbol)s&instrument=OPTSTK&expiry=&type=CE&strike='
    session = requests.Session()
    print(URL_TEMPLATE % dict(symbol=security))
    html = session.get(URL_TEMPLATE % dict(symbol=security),verify=False,headers=headers).text
    df_list = pd.read_html(html)
    return df_list



def pull_option_chain(security):
    URL_TEMPLATE = 'https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=234&symbol=%(symbol)s&instrument=OPTSTK'

    print(URL_TEMPLATE % dict(symbol=security))
    # if not session or random.random()>0.95:
    session = requests.Session()
    html = session.get(URL_TEMPLATE % dict(symbol=security),headers=headers,verify=False).text

    df = pd.read_html(html, attrs=dict(id='octable'), header=1)[0]
    df.columns = [
        'calls_chart',
        'calls_oi',
        'calls_chng_in_oi',
        'calls_volume',
        'calls_iv',
        'calls_ltp',
        'calls_net_chng',
        'calls_bidqty',
        'calls_bidprice',
        'calls_ask_price',
        'calls_askqty',
        'strike_price',
        'puts_bidqty',
        'puts_bidprice',
        'puts_askprice',
        'puts_askqty',
        'puts_net_chng',
        'puts_ltp',
        'puts_iv',
        'puts_volume',
        'puts_chng_in_oi',
        'puts_oi',
        'puts_chart'
    ]
    df['calls_oi'] = df['calls_oi'].apply(lambda x:int(x) if x!='-' else  0)
    df['puts_oi'] = df['puts_oi'].apply(lambda x:int(x) if x!='-' else  0)
    df = df[df['puts_chart']!='Total']

    quote_text = pd.read_html(html)[0][1][0]
    import re
    import datetime
    date_match = re.search('As on (.*) IST', quote_text)
    if date_match:
        date_pulled = datetime.datetime.strptime(date_match.group(1), '%b %d, %Y %H:%M:%S')
    else:
        date_pulled = datetime.datetime.now()

    quote_match = re.search('(\d+\.\d{2})',quote_text)
    if quote_match:
        quote = float(quote_match.group())
        df['above_below'] = df['strike_price'].apply(lambda x:x>quote)
    else:
        return pd.DataFrame(),None,None


    return df, quote, date_pulled.strftime('%Y-%m-%dT%H:%M:%S+0530')