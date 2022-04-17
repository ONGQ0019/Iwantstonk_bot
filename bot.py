import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import re
from datetime import datetime
import lxml
import json
from bs4 import BeautifulSoup
import fear_and_greed
from urllib.request import urlopen
from io import BytesIO
import yfinance as yf
import warnings
from flask import Flask, request
import os
import http.client
from ast import literal_eval
import psycopg2

API_KEY = '53528'
TOKEN = '53528' #fakeapi
bot = telebot.TeleBot(API_KEY)
server = Flask(__name__)

@bot.message_handler(commands=['start',"Start","START"])
def send_welcome(message):
  bot.reply_to(message, "Hello, IWantStonks_bot" + '\U0001F916'+ " is here to pull data on any NASDAQ/NYSE stock. \nUse /menu to navigate \nUse /help to seek help \nYou are welcome :)")
  bot.send_sticker(message.chat.id, sticker = 'CAACAgUAAxkBAAEEejxiWZLp4LiSd3wSCAGMWy3swn8JqQACMQQAAiPI0FacSinyMd0jSyME')

@bot.message_handler(commands=['help',"Help","HELP"])
def send_welcome1(message):
  bot.reply_to(message, "/start to start \n/menu to go to main menu  \n/market_news to view latest market news" +
  "\n/heat_map to view stocks heatmap \n/market_index to view top market indexes \n/fear_index to view market fear and greed index \n/stock_value to value any stock \n/stock_price to see price change of any stock \n/stock_news to see news of any stock \n/stock_calendar to see event dates of any stock \n/watch_list to create your own watchlist \n/summary to get market summary on your watchlist")

@bot.message_handler(commands=['menu',"MENU",'Menu'])
def send_welcomexx(message):
  markup = types.ReplyKeyboardMarkup(row_width=2)
  itembtn1 = types.KeyboardButton('/market_news')
  itembtn2 = types.KeyboardButton('/heat_map')
  itembtn3 = types.KeyboardButton('/market_index')
  itembtn4 = types.KeyboardButton('/fear_index')
  itembtn5 = types.KeyboardButton('/stock_value')
  itembtn6 = types.KeyboardButton('/stock_price')
  itembtn7 = types.KeyboardButton('/stock_news')
  itembtn8 = types.KeyboardButton('/stock_calendar')
  itembtn9 = types.KeyboardButton('/watch_list')
  itembtn10 = types.KeyboardButton('/summary')
  markup.add(itembtn1, itembtn2, itembtn3,itembtn4,itembtn5,itembtn6,itembtn7,itembtn8,itembtn9,itembtn10)
  bot.send_message(message.chat.id, "Select one of the options to get started \U0001F63C", reply_markup=markup)

@bot.message_handler(commands=['market_news'])
def send_welcome(message):
  x =1
  for each in yahoo_get_top_news_data():
    if x<4:
      bot.send_message(message.chat.id,"News article Number: " +str(x) + "\n\n" + each)
      x +=1

@bot.message_handler(commands=['heat_map'])
def send_welcome(message):
	bot.send_photo(message.chat.id, "https://finviz.com/published_map.ashx?t=sec_all&st=&f=041222&i=sec_all_122970944",caption= "Updated: "+ "https://finviz.com/map.ashx")

def yahoo_get_top_news_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                      "(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
    }

    html = requests.get('https://finance.yahoo.com/', headers=headers)
    soup = BeautifulSoup(html.text, 'lxml')

    all_script_tags = soup.select('script')
    matched_string = ''.join(re.findall(r'root\.App\.main = (.*);\n+}\(this\)\);\n+</script>', str(all_script_tags)))
    matched_string_json = json.loads(matched_string)

    matched_string_json_stream = matched_string_json['context']['dispatcher']['stores']['ThreeAmigosStore']['data']['ntk']['stream']
    list1 = []
    for top_news_result_index, top_news in enumerate(matched_string_json_stream):
        teaser = top_news['editorialContent']['teaser']
        title = top_news['editorialContent']['title']

        try:
            source = top_news['editorialContent']['content']['provider']['displayName']
        except:
            source = None

        try:
            source_site_link = top_news['editorialContent']['content']['provider']['url']
        except:
            source_site_link = None

        try:
            canonical_url = top_news['editorialContent']['content']['canonicalUrl']['url']
        except:
            canonical_url = None

        try:
            canonical_url_website = top_news['editorialContent']['content']['canonicalUrl']['site']
        except:
            canonical_url_website = None

        try:
            click_through_url = top_news['editorialContent']['content']['clickThroughUrl']['url']
        except:
            click_through_url = None

        try:
            click_through_url_website = top_news['editorialContent']['content']['clickThroughUrl']['site']
        except:
            click_through_url_website = None


        list1.append(
              f'Title: {title}\n\n'
              f'Description: {teaser}\n\n'
              f'URL: {click_through_url}\n')

    return list1

@bot.message_handler(commands=['stock_price'])
def pp2(message):
  sent = bot.send_message(message.chat.id, 'Enter a stock ticker')
  bot.register_next_step_handler(sent, get_stock_price_action)

def get_stock_price_action(message):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                      "(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
    }

    symbols = message.text.upper()
    global ticker
    ticker = yf.Ticker(str(symbols))
    info = None
    if (ticker.info['regularMarketPrice'] == None):
       bot.send_message(message.chat.id,"Invalid ticker, try again!")
       pp2(message)
    else:
        params = {
            'formatted': "true",
            'crumb': 'FI5oDlMl7HO',
            'lang': 'en-US',
            'region': 'US',
            'symbols': symbols,
            'fields': 'symbol,shortName,longName,regularMarketPrice,regularMarketChange,regularMarketChangePercent',
            'corsDomain': 'finance.yahoo.com'
        }
        yahoo_urls = requests.get('https://query2.finance.yahoo.com/v7/finance/quote', params = params, headers = headers, verify=False, timeout=10).text
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        for right_side_stock_result in json.loads(yahoo_urls)['quoteResponse']['result']:
            stock_symbol = right_side_stock_result['symbol']
            short_name = right_side_stock_result['shortName']
            region = right_side_stock_result['region']
            regular_market_time = right_side_stock_result['regularMarketTime']['fmt']
            exchange_time_zone_name = right_side_stock_result['exchangeTimezoneName']
            market_state = right_side_stock_result['marketState']
            quote_type = right_side_stock_result['quoteType']

            try:
                quote_source_name = right_side_stock_result['quoteSourceName']
            except:
                quote_source_name = None

            market = right_side_stock_result['market']
            regular_market_price = right_side_stock_result['regularMarketPrice']['fmt']
            regular_market_change = right_side_stock_result['regularMarketChange']['fmt']
            regular_market_change_percent = right_side_stock_result['regularMarketChangePercent']['fmt']
            if float(regular_market_change) >0:
              emoji = "\U0001F7E2"
            else:
              emoji = "\U0001F534"
            bot.send_photo(message.chat.id, BytesIO(urlopen("https://app.quotemedia.com/quotetools/getChart?webmasterId=102684&snap=true&chtype=LineChart&chton=some&chdon=on&chton=off&chcon=false&chfrmon=false&chmrg=0&chfill=fa8a20&chfill=fa8a20&chgrdon=off&chbgch=1a0511&chln=e82028&&chscale=1d&chbg=1a0511&chwid=610&chxyc=ffffff&chtcol=ffffff&chhig=240&symbol="+symbols).read()), caption = f'Source: {quote_source_name}\n'
                  f'Symbol: {stock_symbol}\n'
                  f'Name: {short_name}\n'
                  f'Regular market time: {regular_market_time}\n'
                  f'Market: {market}\n'
                  f'Market state: {market_state}\n'
                  f'Market price: {regular_market_price}\n'
                  f'Price change: {regular_market_change}\n'
                  f'Price % change: {regular_market_change_percent}'+ emoji)
            bot.send_message(message.chat.id,"Press /stock_price for a different stock or /menu to go to menu")

@bot.message_handler(commands=['market_index'])
def get_stock_price_action2(message):
  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    "(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
  }
  for each in ["DIA","QQQ","VTI"]:
      symbols = each
      params = {
          'formatted': "true",
          'crumb': 'FI5oDlMl7HO',
          'lang': 'en-US',
          'region': 'US',
          'symbols': symbols,
          'fields': 'symbol,shortName,longName,regularMarketPrice,regularMarketChange,regularMarketChangePercent',
          'corsDomain': 'finance.yahoo.com'
      }
      yahoo_urls = requests.get('https://query2.finance.yahoo.com/v7/finance/quote', params = params, headers = headers, verify=False, timeout=10).text
      warnings.filterwarnings('ignore', message='Unverified HTTPS request')
      for right_side_stock_result in json.loads(yahoo_urls)['quoteResponse']['result']:
          stock_symbol = right_side_stock_result['symbol']
          short_name = right_side_stock_result['shortName']
          region = right_side_stock_result['region']
          regular_market_time = right_side_stock_result['regularMarketTime']['fmt']
          exchange_time_zone_name = right_side_stock_result['exchangeTimezoneName']
          market_state = right_side_stock_result['marketState']
          quote_type = right_side_stock_result['quoteType']

          try:
              quote_source_name = right_side_stock_result['quoteSourceName']
          except:
              quote_source_name = None

          market = right_side_stock_result['market']
          regular_market_price = right_side_stock_result['regularMarketPrice']['fmt']
          regular_market_change = right_side_stock_result['regularMarketChange']['fmt']
          regular_market_change_percent = right_side_stock_result['regularMarketChangePercent']['fmt']
          if float(regular_market_change) >0:
            emoji = "\U0001F7E2"
          else:
            emoji = "\U0001F534"
          bot.send_photo(message.chat.id, BytesIO(urlopen("https://app.quotemedia.com/quotetools/getChart?webmasterId=102684&snap=true&chtype=LineChart&chton=some&chdon=on&chton=off&chcon=false&chfrmon=false&chmrg=0&chfill=fa8a20&chfill=fa8a20&chgrdon=off&chbgch=1a0511&chln=e82028&&chscale=1d&chbg=1a0511&chwid=610&chxyc=ffffff&chtcol=ffffff&chhig=240&symbol="+symbols).read()), caption =
                f'Symbol: {stock_symbol}\n'
                f'Name: {short_name}\n'
                f'Market price: {regular_market_price}\n'
                f'Price change: {regular_market_change}\n'
                f'Price % change: {regular_market_change_percent}'+ emoji)
          if symbols == "VTI" and float(regular_market_change) >0:
               bot.send_document(message.chat.id, "https://github.com/ONGQ0019/filedumps/blob/main/200w.gif?raw=true")
          elif symbols == "VTI" and float(regular_market_change) < 0:
               bot.send_document(message.chat.id, "https://github.com/ONGQ0019/filedumps/blob/main/200l.gif?raw=true")
          else:
               ccc = 111

@bot.message_handler(commands=['stock_value'])
def pp(message):
  sent = bot.send_message(message.chat.id, 'Enter a stock ticker')
  bot.register_next_step_handler(sent, getstock)


def getstock(message):
    # create url
    tens = dict(K=10e3, M=10e6, B=10e9)
    stockname = message.text.upper()
    url = 'https://sg.finance.yahoo.com/quote/'+stockname+'/key-statistics?'
    url2 = 'https://sg.finance.yahoo.com/quote/'+stockname+'/analysis?'
    url3= 'https://www.gurufocus.com/term/iv_dcf/'+stockname+'/Intrinsic-Value:-DCF-(FCF-Based)/'
    # define headers
    headers = { 'User-Agent': 'Generic user agent' }
      # get page
    page = requests.get(url, headers=headers)
    page2 = requests.get(url2, headers=headers)
    page3 = requests.get(url3, headers=headers)
    # let's soup the page
    soup = BeautifulSoup(page.text, 'html.parser')
    soup2 = BeautifulSoup(page2.text, 'html.parser')
    soup3 = BeautifulSoup(page3.text, 'html.parser')
    global cf
    try:
      cf = soup.find_all('td', {'class': 'Fw(500) Ta(end) Pstart(10px) Miw(60px)'})[59].text
      if cf != 'N/A':
        bot.send_message(message.chat.id,"Using DCF model to calculate intrinsic value...")
      else:
        bot.send_message(message.chat.id,"Cash flow not found. Using EV model to calculate intrinsic value...")
      try:
          try:
              # get company name
              company_name = soup.find('h1', {'class': 'D(ib) Fz(18px)'}).text
          except:
              print('Name not found!')
          try:
              # get price
              price = soup.find('fin-streamer', {'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
              price = price.replace(',',"")
          except:
              print('Price not found!')
          try:
              # get p/e
              pe = soup.find_all('td', {'class': 'Fw(500) Ta(end) Pstart(10px) Miw(60px)'})[3].text
          except:
              print('P/e not found!')
          try:
              # get p/s
              ps = soup.find_all('td', {'class': 'Fw(500) Ta(end) Pstart(10px) Miw(60px)'})[5].text
          except:
              print('P/s not found!')
          try:
              # get e/v
              ev = soup.find_all('td', {'class': 'Fw(500) Ta(end) Pstart(10px) Miw(60px)'})[7].text   #7
          except:
              print('P/s not found!')
          try:
              # get cf
              cf = soup.find_all('td', {'class': 'Fw(500) Ta(end) Pstart(10px) Miw(60px)'})[59].text
          except:
              print('Cash flow not found!')
          try:
              # get shareoustanding
              shareout = soup.find_all('td', {'class': 'Fw(500) Ta(end) Pstart(10px) Miw(60px)'})[18].text
              factor, exp = shareout[0:-1], shareout[-1].upper()
              shareout = int(float(factor) * tens[exp])
          except:
              print('shareout not found!')
          try:
              # get growth
              growth = soup2.find_all('td', {'class': "Ta(end) Py(10px)"})[16].text
          except:
              print('Cash flow not found!')
          try:
              # get rev growth
              revgrowth = soup2.find_all('td', {'class': "Ta(end)"})[43].text
              revgrowth = float(revgrowth.strip('%'))/100
          except:
              print('rev growth not found!')
          try:
              # get disc
              discount = soup3.find_all('p', {'class': "term_cal"})[1].text
              discount = discount[22:25]
              discount2 = re.sub('%', '', discount)
              discount2 = float(discount2)/100
          except:
              print('Discount not found!')
          try:
              # get value
              intrinsic = soup3.find_all('font', {'style': "font-size: 24px; font-weight: 700; color: #337ab7"})[0].text
              intrinsic = intrinsic.replace(':',"")
              intrinsic = intrinsic.replace(',',"")
              intrinsic = intrinsic.replace('(As of Today)',"")
              intrinsic = intrinsic.replace('USD',"")
              intrinsicnumber = float(intrinsic.replace('$',""))
          except Exception as e:
              print(e)
          try:
              # get  revenue
              revenue = soup.find_all('td', {'class': 'Fw(500) Ta(end) Pstart(10px) Miw(60px)'})[44].text
              factor, exp = revenue[0:-1], revenue[-1].upper()
              revenue2 = int(float(factor) * tens[exp])
              rev = round(((((revenue2*(1+revgrowth))*float(ev))*1)/(1+discount2))/shareout,2)
          except:
              print('revenue not found!')

          if cf == "N/A":
                    bot.send_message(message.chat.id, "Company Name: "+ company_name+ "\nCurrent Price: $"+ price + "\nForward P/E: "+pe + "\nP/S (TTM): "+ps + "\nEnterprise Value Ratio: "+ev +"\nLevered Cash Flow: "+cf+"\nForward Growth: "+growth + "\nWACC: "+ discount
                          + "\nIntrinsic Value: "+"$"+ str(rev)+ " (As of Today)")
          else:
                    bot.send_message(message.chat.id, "Company Name: "+ company_name+ "\nCurrent Price: $"+ price + "\nForward P/E: "+pe + "\nP/S (TTM): "+ps + "\nEnterprise Value Ratio: "+ev +"\nLevered Cash Flow: "+cf+"\nForward Growth: "+growth + "\nWACC: "+ discount
                          + "\nIntrinsic Value:"+ intrinsic + " (As of Today)")
          if cf != "N/A" and intrinsicnumber < float(price):
            bot.send_message(message.chat.id,"Signal: SELL"+ " \U0001F4B8	"+"\nPotential downside: "+str(max(-round(((float(price)-intrinsicnumber)/float(price))*100,2),-100))+"%")
          elif cf == 'N/A' and rev < float(price):
            bot.send_message(message.chat.id,"Signal: SELL"+ " \U0001F4B8 "+"\nPotential downside: "+str(max(-round(((float(price)-rev)/float(price))*100,2),-100))+"%")
          elif cf =='N/A' and rev >= float(price):
            bot.send_message(message.chat.id,"Signal: BUY"+ " \U0001F4B0 "+"\nPotential upside: "+str(round(((rev-float(price))/float(price))*100,2))+"%")
          elif cf != "N/A" and intrinsicnumber >= float(price):
            bot.send_message(message.chat.id,"Signal: BUY" + " \U0001F4B0 "+"\nPotential upside: "+str(round(((intrinsicnumber - float(price))/float(price))*100,2))+"%")
          bot.send_message(message.chat.id,"Press /stock_value for a different stock or /menu to go to menu")

      except Exception as e:
          print(e)

    except:
      IndexError
      bot.send_message(message.chat.id,"Invalid ticker, try again! No ETFs!")
      pp(message)

@bot.message_handler(commands=['fear_index'])
def send_welcome(message):
  x = ''.join(str(fear_and_greed.get()))
  y= x.split(",")[0]
  value = y.split("(")[1]
  description = x.split(",")[1]
  bot.send_message(message.chat.id,"Updated on "+ datetime.today().strftime('%Y-%m-%d')+" :" + "\n"+"Fear&Greed index "+value+"\n"+description.strip())


@bot.message_handler(commands=['stock_news'])
def ppcc(message):
  sent = bot.send_message(message.chat.id, 'Enter a stock ticker')
  bot.register_next_step_handler(sent, send_news)

def send_news(message):
  stockname = message.text.upper()
  try: 
    conn = http.client.HTTPSConnection("mboum.com")
    headers = {
        'X-Mboum-Secret': "K1RLM0pZLpsQyGVoXCDsxHeeZl7f7WfSxzIrorM6DLgrCYEMD4pjcnKuKkKV"
        }
    conn.request("GET", "/api/v1/ne/news/?symbol="+stockname, headers=headers)
    res = conn.getresponse()
    data = res.read()
    python_dict = literal_eval(data.decode("utf-8"))
    python_dict['data']['item'][0]
    x =1
    for each in [0,1,2]:
      bot.send_message(message.chat.id,"News article Number: " +str(x) +"\n\nTitle: "+ python_dict['data']['item'][each]['title'] + "\n\nDescription: "+ python_dict['data']['item'][each]['description'].split('.')[0]+'.' + "\n\nURL: "+ python_dict['data']['item'][each]['link'])
      x += 1
  except:
    KeyError
    bot.send_message(message.chat.id,"Invalid ticker, try again!")
    ppcc(message)


@bot.message_handler(commands=['stock_calendar'])
def ppdd(message):
  sent = bot.send_message(message.chat.id, 'Enter a stock ticker')
  bot.register_next_step_handler(sent, send_calender)

def send_calender(message):
  stockname = message.text.upper()
  try:
    conn1 = http.client.HTTPSConnection("mboum.com")
    headers = {
        'X-Mboum-Secret': "Rh5b4DcgTsMSm5wGF4XYPctN6poN5kGYQEmDmIw8czsN4I930QiZgVL8fIxV"
        }
    conn1.request("GET", "/api/v1/qu/quote/calendar-events/?symbol="+stockname, headers=headers)
    res1 = conn1.getresponse()
    data1 = res1.read()
    python_dict1 = literal_eval(data1.decode("utf-8"))
    earnlist = []
    for each in python_dict1['data']['earnings']['earningsDate']:
      earnlist.append(each['fmt'])
    try:   
      bot.send_message(message.chat.id, "Stock: " + stockname + "\nEarnings Date: " + ", ".join(str(x) for x in earnlist) +"\nDividend Date: "+ python_dict1['data']['dividendDate']['fmt'] +"\nEx-dividend Date: "+ python_dict1['data']['exDividendDate']['fmt'])
    except:
      bot.send_message(message.chat.id, "Stock: " + stockname + "\nEarnings Date: " + ", ".join(str(x) for x in earnlist))
  except:
    KeyError
    bot.send_message(message.chat.id,"Invalid ticker, try again!")
    ppdd(message)

#fake database connection
hostname = "ec2-.compute-1.amazonaws.com"
database = "de6ldr"
user = "iby"
port_id = 54
password ="2a445795d88e149d4adc019b6b92586d464"
URL = "postgres://iwxmivkpyef0ebdd4adc019b6b92586d464@ec2-52-203-118-49.compute-1.amazonaws.com:5432/de6ld0ihm6606r"

conn = psycopg2.connect(host =hostname,
                      dbname = database,
                      user = user,
                      password = password,
                      port = port_id)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS stonkdb1 (id varchar(80), name varchar(180))""")
conn.commit()

@bot.message_handler(commands=['add'])
def ppdd(message):
  sent =  bot.send_message(message.chat.id, 'Enter stock tickers in this formart \ne.g. Bili,Nio,AAPL,GOOGL')
  bot.register_next_step_handler(sent,get_user_stock)

def get_user_stock(message):
  if message.text == "/end":
    bot.send_message(message.chat.id, 'Database session ended')
  else:
    bot.send_message(message.chat.id, 'Uploading your stocks, please be patient.')
    try:
      conn = psycopg2.connect(host =hostname,
                            dbname = database,
                            user = user,
                            password = password,
                            port = port_id)
      cur = conn.cursor()
      symbols = message.text.upper().replace(" ", "").split(',')
      cur.execute('SELECT DISTINCT name FROM stonkdb1 WHERE id=%s LIMIT 10',(str(message.chat.id),))
      data = cur.fetchall()
      newdata = [i[0] for i in data]
      global ticker
      wronglist = []
      duplicates =[]
      for each in symbols:
        ticker = yf.Ticker(str(each))
        info = None
        if (ticker.info['regularMarketPrice'] == None):
          wronglist.append(each)
        elif each in newdata:
          duplicates.append(each)
      if len(wronglist) > 0:
        bot.send_message(message.chat.id,"Invalid tickers: " + str(', '.join(wronglist))+ "\nTry again or /end to end")
        ppdd(message)
        conn.close()
        cur.close()
      elif len(duplicates)> 0:
        bot.send_message(message.chat.id,"Duplicate tickers: " + str(', '.join(duplicates))+ "\nTry again or /end to end ")
        ppdd(message)
        conn.close()
        cur.close()
      else:
        stock = message.text.upper().replace(" ", "").split(',')
        for each in stock:
          cur.execute('INSERT INTO stonkdb1 (id ,name) VALUES (%s,%s)',(str(message.chat.id),each))
          conn.commit()
          newdata.append(each)
        bot.send_message(message.chat.id, "Your current watchlist: "+  str(', '.join(newdata))) 

    except:
      KeyError
      bot.send_message(message.chat.id, 'Database under maintenance')
      ppdd(message)
        
    finally:
      conn.close()
      cur.close()

@bot.message_handler(commands=['remove'])
def ppdd1(message):
  conn = psycopg2.connect(host =hostname,
                          dbname = database,
                          user = user,
                          password = password,
                          port = port_id)
  cur = conn.cursor()
  cur.execute('SELECT DISTINCT name FROM stonkdb1 WHERE id=%s LIMIT 10',(str(message.chat.id),))
  data = cur.fetchall()
  newdata = [i[0] for i in data]
  if len(newdata) < 1: 
    bot.send_message(message.chat.id, "Your current watchlist is empty, /add to add stocks")
  else:
    sent = bot.send_message(message.chat.id, "Enter stocks you want to delete \ne.g. Nio,Bili,Googl")
    bot.register_next_step_handler(sent,remover)

def remover(message):
  if message.text == "/end":
   bot.send_message(message.chat.id, 'Database session ended')
  else:
    try:
      conn = psycopg2.connect(host =hostname,
                            dbname = database,
                            user = user,
                            password = password,
                            port = port_id)
      cur = conn.cursor()
      symbols = message.text.upper().replace(" ", "").split(',')
      cur.execute('SELECT DISTINCT name FROM stonkdb1 WHERE id=%s LIMIT 10',(str(message.chat.id),))
      data = cur.fetchall()
      newdata = [i[0] for i in data]
      global ticker
      wronglist = []
      nonexist =[]
      for each in symbols:
        ticker = yf.Ticker(str(each))
        info = None
        if (ticker.info['regularMarketPrice'] == None):
          wronglist.append(each)
        elif each not in newdata:
          nonexist.append(each)
      if len(wronglist) > 0:
        bot.send_message(message.chat.id,"Invalid tickers: " + str(', '.join(wronglist))+ "\nTry again or /end to end")
        ppdd1(message)
        conn.close()
        cur.close()
      elif len(nonexist)> 0:
        bot.send_message(message.chat.id,"Non-exist tickers: " + str(', '.join(nonexist))+ "\nTry again or /end to end")
        ppdd1(message)
        conn.close()
        cur.close()
      else:
        for each in symbols:
          cur.execute('DELETE FROM stonkdb1 WHERE id =%s AND name =%s',(str(message.chat.id),each))
          conn.commit()
        bot.send_message(message.chat.id, message.text.upper()+ " Successfully deleted")
    except:
      KeyError
      bot.send_message(message.chat.id, 'Database under maintenance')
      ppdd1(message)
    finally:
      conn.close()
      cur.close()
      

    
@bot.message_handler(commands=['watch_list'])
def watchlist1(message):
  try:
    conn = psycopg2.connect(host =hostname,
                          dbname = database,
                          user = user,
                          password = password,
                          port = port_id)
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT name FROM stonkdb1 WHERE id=%s LIMIT 10',(str(message.chat.id),))
    data = cur.fetchall()
    newdata = [i[0] for i in data]
    if len(newdata) < 1: 
      bot.send_message(message.chat.id, "Your current watchlist is empty, /add to add stocks")
    else:
      bot.send_message(message.chat.id, "Your current watchlist: " + str(', '.join(newdata)) + "\n/add to add stocks \n/remove to remove stocks")
  except:
    KeyError
    bot.send_message(message.chat.id, 'Database under maintenance')
  finally:
    conn.close()
    cur.close()

@bot.message_handler(commands=['summary'])
def summarypp(message):
  try:
    conn = psycopg2.connect(host =hostname,
                          dbname = database,
                          user = user,
                          password = password,
                          port = port_id)
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT name FROM stonkdb1 WHERE id=%s LIMIT 10',(str(message.chat.id),))
    data = cur.fetchall()
    newdata = [i[0] for i in data]
    if len(newdata) < 1: 
     bot.send_message(message.chat.id, "Your current watchlist and market summary is empty, /add to add stocks")
    with open('ex.txt', 'w') as f:
      f.write('Here is your market summary: \n\n')
    headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    "(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
      }
    for each in newdata:
        params = {
        'formatted': "true",
        'crumb': 'FI5oDlMl7HO',
        'lang': 'en-US',
        'region': 'US',
        'symbols': each,
        'fields': 'symbol,regularMarketPrice,regularMarketChange,regularMarketChangePercent',
        'corsDomain': 'finance.yahoo.com'
          }
        yahoo_urls = requests.get('https://query2.finance.yahoo.com/v7/finance/quote', params = params, headers = headers, verify=False, timeout=10).text
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        for right_side_stock_result in json.loads(yahoo_urls)['quoteResponse']['result']:
            stock_symbol = right_side_stock_result['symbol']
            regular_market_price = right_side_stock_result['regularMarketPrice']['fmt']
            regular_market_change = right_side_stock_result['regularMarketChange']['fmt']
            regular_market_change_percent = right_side_stock_result['regularMarketChangePercent']['fmt']
            if float(regular_market_change) >0:
              emoji = "\U0001F7E2"
            else:
              emoji = "\U0001F534"
            with open('ex.txt', 'a') as fd:
                  fd.write(f'Symbol: {stock_symbol}\n'
                  f'Market price: {regular_market_price}\n'
                  f'Price change: {regular_market_change}\n'
                  f'Price % change: {regular_market_change_percent}'+ emoji+'\n\n')
    with open("ex.txt", 'r', encoding="utf-8") as file:
        new_list = file.read()
    bot.send_message(message.chat.id,new_list)
  except:
    bot.send_message(message.chat.id,"Your watchlist is empty, go to /add to add your stocks")
  finally:
    conn.close()
    cur.close()

  




@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://stockbot97.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
