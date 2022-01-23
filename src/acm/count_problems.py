import functools
import requests
import xlrd
import xlwt
import datetime
import json
from dataclasses import dataclass, field
"""
依赖库：xlrd xlwt requests
cmd中跑命令安装：
pip install xlrd,xlwt,requests

环境：建议Python 3.8+，可能3.7+可以用

"""

# 填比赛id
lnks = [
    ('464516', 1),
    ('466424', 2),
    ('466991', 2),
    ('469629', 2),
    ('469630', 2),
]
output = 'tj.xls'        # 输出文件名


@dataclass
class Player():
    pen: int
    sol: int
    name: str
    nick: str
    score: int = 0

    details: dict = field(default_factory=dict)
    star: bool = False
    ps: str = ''


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
    style.borders = borders
    style.num_format_str = format_str

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


plrd = {}
plr = []

tctr = 0

dt = datetime.datetime.strptime('0', '%S')


def read_time(x): return int(
    (datetime.datetime.strptime(x, '%H:%M:%S')-dt).total_seconds())


def write_time(x): return f"{x//3600:0>2}:{x%3600//60:0>2}:{x%60:0>2}"


for task, weight in lnks:
    r = requests.post(f"https://vjudge.net/contest/rank/single/{task}")
    print(task, r)
    j = json.loads(r.text)
    for k, v in j['participants'].items():
        k = int(k)
        if k not in plrd:
            plrd[k] = Player(0, 0, v[0], v[1])
        plrd[k].details = {}

    for uid, tid, sta, ti in j['submissions']:
        uid = int(uid)
        if sta:
            penalty = plrd[uid].details.get(tid, 0)
            if penalty < 0:
                continue
            else:
                plrd[uid].pen += 1200*penalty+ti
                plrd[uid].sol += 1
                plrd[uid].score += weight

                plrd[uid].details[tid] = -1
        else:
            penalty = plrd[uid].details.get(tid, 0)
            if penalty >= 0:
                plrd[uid].details[tid] = penalty+1


for k, v in plrd.items():
    plr.append(v)


# for itm in luogu['scoreboard']['result']:
#     usr = itm['user']
#     if usr['name'] in luogu_isnot_star:
#         p = Player(itm['runningTime'], itm['score'], usr['name'], luogu_isnot_star.get(usr['name']))
#     else:
#         p = Player(itm['runningTime'], itm['score'], usr['name'], str(usr['uid']), star=True)
#     for k, v in itm['details'].items():
#         p.details[T2t[k]] = v
#     plr.append(p)

print(len(plr))


def plrcmp(x1: Player, x2: Player) -> bool:
    if x1.score > x2.score:
        return -1
    elif x1.score < x2.score:
        return 1
    else:
        if x1.pen < x2.pen:
            return -1
        elif x1.pen > x2.pen:
            return 1
        else:
            return 0


# plr.sort(key=functools.cmp_to_key(plrcmp))
plr.sort(key=lambda x: (-x.score, -x.sol, x.pen))

owb = xlwt.Workbook()
ows = owb.add_sheet('flitered')

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


for p, i in enumerate(['排名', '用户id', '题数', '分数', '罚时', '昵称']):
    ows.write(0, p, i, set_style())
    colwid.append(clen(i))


rks = 1
for p, i in enumerate(plr):
    ows.row(1+p).height = 500
    if i.star:
        ows.write(1+p, 0, '*', set_style())
    else:
        ows.write(1+p, 0, rks, set_style())
        rks += 1

    ows.write(1+p, 1, i.name, set_style(star=i.star))
    updcolwid(1, i.name)

    ows.write(1+p, 2, str(i.sol), set_style())
    updcolwid(2, i.sol)

    ows.write(1+p, 3, str(i.score), set_style())
    updcolwid(3, i.score)

    ows.write(1+p, 4, write_time(i.pen), set_style(center=True))
    updcolwid(4, write_time(i.pen))

    # for k, v in i.details.items():
    #     ofs = ord(k) - 65
    #     ostl = []
    #     if 'runningTime' in v:
    #         ostl.append(write_time(v['runningTime']))
    #     if v['score']!='0':
    #         ostl.append(f"(-{abs(v['score'])})")
    #     ostr = '\n'.join(ostl)
    #     if ostr:
    #         ows.write(1+p, 4+ofs, ostr, set_style(center=True))
    #         updcolwid(4+ofs, max(ostl, key=lambda x: clen(x)))
    ows.write(1+p, 5+tctr+0, i.nick, set_style())
    updcolwid(5+tctr+0, i.nick)
    # if i.ps:
    # ows.write(1+p, 4+tctr+2, f"已经去掉{i.ps}个cin罚时", set_style())
    # updcolwid(4+tctr+2, f"已经去掉{i.ps}个cin罚时")

print(colwid)

for p, i in enumerate(colwid):
    ows.col(p).width = i * 300

owb.save(output)
