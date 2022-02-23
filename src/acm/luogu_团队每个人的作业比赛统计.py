import os
os.system('pip install pydantic xlwt requests brotli')

from time import sleep
from pydantic import BaseModel
from typing import *
import xlwt
import datetime
import json
import requests

class Config:
    """首选项区，配置都在这里写，
    底下除了EditThisCookie导出的东西得贴你自己的，
    其它不用管。
    别实例化这个类"""
    output = '寒假集训比赛.xls'          # 输出文件名
    group_id = 40846                    # 洛谷团队id


class LuoguUser(BaseModel):
    """洛谷用户对象的json序列化映射"""
    ccfLevel: int
    color: str
    isAdmin: bool
    isBanned: bool
    name: str
    slogan: str = None
    uid: int  # 主键


class LuoguMember(BaseModel):
    """洛谷团队成员，带实名信息"""
    permission: int
    realName: str
    type: int
    user: LuoguUser
    form_item: list = []  # 放表格内容用


class LuoguProblemHost(BaseModel):
    """洛谷出题人"""
    id: int
    isPremium: bool
    name: str


class LuoguContest(BaseModel):
    """洛谷比赛实体"""
    endTime: int
    host: LuoguProblemHost
    id: int
    invitationCodeType: int
    name: str
    problemCount: int
    rated: bool
    ruleType: int
    startTime: int
    visibilityType: int


class G:
    """定义变量区，别实例化这个类"""
    members: List[LuoguMember] = []  # 团队所有成员信息
    headers: List[str] = ['昵称']  # 表头
    ses: requests.Session = requests.session()  # 放登录信息以便爬
    sleep_time: float = 30  # 触发反爬时歇逼时间

    @staticmethod
    def get(*args, **kwargs):
        r = G.ses.get(*args, **kwargs)
        while r.status_code != 200:
            print(f'anti-spider detected, sleep for {G.sleep_time}s')
            sleep(G.sleep_time)
            r = G.ses.get(*args, **kwargs)
        return r

    @staticmethod
    def post(*args, **kwargs):
        r = G.ses.post(*args, **kwargs)
        while r.status_code != 200:
            print(f'anti-spider detected, sleep for {G.sleep_time}s')
            sleep(G.sleep_time)
            r = G.ses.post(*args, **kwargs)
        return r


def prework():
    # EditThisCookie导出的网站cookies贴在这里
    export_cookies = """"""
    import http.cookiejar
    # c = http.cookiejar.CookieJar()
    for cookie in json.loads(export_cookies):
        G.ses.cookies.set_cookie(
            http.cookiejar.Cookie(version=0, name=cookie['name'], value=cookie['value'], port=None, port_specified=False, domain=cookie['domain'], domain_specified=False, domain_initial_dot=False,
                                  path=cookie['path'], path_specified=True, secure=cookie['secure'], expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
        )
    G.ses.headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "dnt": "1",
        "pragma": "no-cache",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    }


prework()


def multipage_spider(baseurl: str,  route: List[str], callback: Callable[[dict], None], params: dict = {},):
    j = G.get(f"{baseurl}", params={'page': 1, **params}).json()
    jj = j
    for r in route:
        jj = jj[r]
    done = jj['perPage']
    i = 2
    callback(j)

    while done < jj['count']:
        j = G.get(f"{baseurl}", params={'page': 1, **params}).json()
        callback(j)
        jj = j
        for r in route:
            jj = jj[r]
        done += jj['perPage']
        i += 1


def handle_members():
    for i in G.get(f'https://www.luogu.com.cn/api/team/members/{Config.group_id}').json()['members']:
        G.members.append(LuoguMember.parse_obj(i))
    # print(G.members)


handle_members()


def handle_homework():
    homework_id = []

    def work(j: dict):
        for i in j['trainings']['result']:
            homework_id.append(i['id'])
            G.headers.append(i['title'])
    multipage_spider(f'https://www.luogu.com.cn/api/team/trainings/{Config.group_id}', [
                     'trainings'], work, {'homework': True})
    # print(homework_id)
    for p, hw in enumerate(homework_id):
        print(f'homework({p+1}/{len(homework_id)})')
        d = {}
        for i in G.get(f'https://www.luogu.com.cn/api/training/scoreboard/{hw}').json()['scoreboard']:
            u = LuoguUser.parse_obj(i['user'])
            d[u.uid] = i['totalScore']
        for i in G.members:
            i.form_item.append(d.get(i.user.uid, 0))


handle_homework()


def handle_contests():
    """爬比赛"""
    contests: List[LuoguContest] = []  # 团队所有比赛表

    def work(j: dict):
        """处理api/team/contests的json，塞进contests里"""
        for i in j['result']:
            contests.append(LuoguContest.parse_obj(i))

    lnk = f"https://www.luogu.com.cn/api/team/contests/{Config.group_id}"
    j = G.get(lnk).json()['contests']
    done = j['perPage']
    nextpagectr = 2
    work(j)
    while done < j['count']:
        j = G.get(f"{lnk}?page={nextpagectr}").json()['contests']
        work(j)
        done += j['perPage']
        nextpagectr += 1

    # print(contests)
    def work(d: dict, j: dict):
        """将fe/api/contest/scoreboard的json表示的个人得分写入d中，d以LuoguUser的uid为键"""
        for i in j['result']:
            u: LuoguUser = LuoguUser.parse_obj(i['user'])
            d[u.uid] = i['score']

    for p, c in enumerate(contests):
        print(f'contests({p+1}/{len(contests)})')
        G.headers.append(c.name)

        d = {}
        nextpagectr = 1
        lnk = f'https://www.luogu.com.cn/fe/api/contest/scoreboard/{c.id}?page='
        j = G.get(lnk+str(nextpagectr)).json()['scoreboard']
        work(d, j)

        done = j['perPage']
        while done < j['count']:
            nextpagectr += 1
            j = G.get(lnk+str(nextpagectr)).json()['scoreboard']
            work(d, j)
            done += j['perPage']

        for i in G.members:
            i.form_item.append(d.get(i.user.uid, 0))


handle_contests()


# def read_time(x): return int((datetime.datetime.strptime(x, '%H:%M:%S')-dt).total_seconds())


# def write_time(x): return f"{x//3600:0>2}:{x%3600//60:0>2}:{x%60:0>2}"


def getxls(plr: List[LuoguMember]):
    def set_style(name='Times New Roman', height=200, star=False, bold=False, format_str='', center=False):
        style = xlwt.XFStyle()  # 初始化样式

        font = xlwt.Font()  # 为样式创建字体
        font.name = name  # 'Times New Roman'
        font.bold = bold
        font.height = height

        borders = xlwt.Borders()  # 为样式创建边框
        borders.left = 6
        borders.right = 6
        borders.top = 6
        borders.bottom = 6

        style.font = font
        # style.borders = borders
        # style.num_format_str = format_str

        if star:
            pat = xlwt.Pattern()
            pat.pattern = xlwt.Pattern.SOLID_PATTERN
            pat.pattern_fore_colour = xlwt.Style.colour_map['yellow']
            style.pattern = pat
        if center:
            ali = xlwt.Alignment()
            ali.horz = xlwt.Alignment.HORZ_CENTER
            style.alignment = ali
        return style

    owb = xlwt.Workbook()
    ows = owb.add_sheet('A')

    colwid = []

    def clen(s):
        l = 0
        for i in s:
            if ord(i) < 256:
                l += 1
            else:
                l += 2
        return l

    def updcolwid(ind, ite): colwid[ind] = max(colwid[ind], clen(str(ite)))

    for p, i in enumerate(G.headers):  # 写表头
        ows.write(0, p, i, set_style())
        colwid.append(clen(i))

    for p, i in enumerate(plr):
        p = p + 1
        ows.row(p).height = 500
        ows.write(p, 0, i.realName, set_style())
        updcolwid(0, i.realName)

        for q, j in enumerate(i.form_item):
            q += 1
            ows.write(p, q, j, set_style())
            updcolwid(q, str(j))

        # ows.write(1+p, 2, str(i.sol), set_style())
        # updcolwid(2, i.sol)

        # ows.write(1+p, 3, write_time(i.pen), set_style(center=True))
        # updcolwid(3, write_time(i.pen))

        # for k, v in i.details.items():
        #     ofs = ord(k) - 65
        #     ostl = []
        #     if 'runningTime' in v:
        #         ostl.append(write_time(v['runningTime']))
        #     if v['score'] != '0':
        #         ostl.append(f"(-{abs(v['score'])})")
        #     ostr = '\n'.join(ostl)
        #     if ostr:
        #         ows.write(1+p, 4+ofs, ostr, set_style(center=True))
        #         updcolwid(4+ofs, max(ostl, key=lambda x: clen(x)))
        # ows.write(1+p, 4+tctr+0, i.nick, set_style())
        # updcolwid(4+tctr+0, i.nick)

    print(colwid)

    for p, i in enumerate(colwid):
        ows.col(p).width = i * 300

    owb.save(Config.output)


getxls(G.members)
