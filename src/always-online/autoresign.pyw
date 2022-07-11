import requests, time, traceback, datetime
import logging
logging.basicConfig(
    filename='resign.log',
    filemode='w',
    level=logging.INFO,  
	format='%(asctime)s<%(filename)s:%(lineno)d>[%(levelname)s]%(message)s',
	datefmt='%H:%M:%S'
)
t1 = 0

DDl = ['#####@zndx']
pwl = ["####"]

def reconnect():
    lnk = 'http://119.39.119.2/a70.htm'
    global t1
    t1^=1
    dt = {
        "DDDDD":DDl[t1],
        "upass":pwl[t1],
        "R1":"0",
        "R2":"",
        "R3":"0",
        "R6":"0",
        "para":"00",
        "0MKKey":"123456",
        "buttonClicked":"",
        "redirect_url":"",
        "err_flag":"",
        "username":"",
        "password":"",
        "user":"",
        "cmd":"",
        "Login":"",
        "v6ip":""
    }

    h1 = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding":"gzip, deflate",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Cache-Control":"no-cache",
        "Connection":"keep-alive",
        "DNT":"1",
        "Host":"119.39.119.2",
        "Pragma":"no-cache",
        "Referer":"http://119.39.119.2/",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }

    hds = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding":"gzip, deflate",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Cache-Control":"no-cache",
        "Connection":"keep-alive",
        "Content-Length":"164",
        "Content-Type":"application/x-www-form-urlencoded",
        "DNT":"1",
        "Host":"119.39.119.2",
        "Origin":"http://119.39.119.2",
        "Pragma":"no-cache",
        "Referer":"http://119.39.119.2/a70.htm",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }

    res = requests.get('http://119.39.119.2/a70.htm', headers=h1)
    logging.debug('GET:', res)
    # print(res.headers)
    # print(res.text)

    res = requests.post(lnk, headers=hds, data=dt)
    logging.debug("POST:", res)

    logging.info(f'reconnect at {datetime.datetime.now()}')
    logging.debug('====================')

def checkconnect():
    try:
        r = requests.get('https://www.baidu.com', timeout=5)
        logging.debug('check connect:', r)
    except:
        logging.critical(traceback.format_exc())
        reconnect()

while True:
    checkconnect()
    time.sleep(25)
    # print(res.headers)
    # print(res.text)