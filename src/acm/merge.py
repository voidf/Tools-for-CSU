import xlrd, xlwt, datetime, json
from dataclasses import dataclass, field

@dataclass
class Player():
    pen: int
    sol: int
    name: str
    nick: str
    details: dict = field(default_factory=dict)
    star: bool = False
    ps: str = ''


csuoj =             'A.xlsx'        # csuoj导出xlsx表
luogu =             'A.json'        # 洛谷导出json
luogu_isnot_star =  'wk.json'       # 洛谷非打星选手
T2t =               'T2tid.json'    # 洛谷题号转换
tctr =              11              # 题数

output =            'op.xls'        # 输出文件名

def set_style(name='Times New Roman', height=200, star=False, bold=False, format_str='', center=False):
    style = xlwt.XFStyle()  # 初始化样式
 
    font = xlwt.Font()  # 为样式创建字体
    font.name = name  # 'Times New Roman'
    font.bold = bold
    font.height = height
 
    borders= xlwt.Borders() # 为样式创建边框
    borders.left= 6
    borders.right= 6
    borders.top= 6
    borders.bottom= 6
 
    style.font = font
    style.borders = borders
    style.num_format_str= format_str
    
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


csuoj = xlrd.open_workbook(csuoj).sheet_by_index(0)

with open(luogu, 'r', encoding='utf-8') as f:
    luogu = json.load(f)

with open(T2t, 'r', encoding='utf-8') as f:
    T2t = json.load(f)

with open(luogu_isnot_star, 'r', encoding='utf-8') as f:
    luogu_isnot_star = json.load(f)

header = []

plr = []

dt = datetime.datetime.strptime('0', '%S')

read_time = lambda x: int((datetime.datetime.strptime(x, '%H:%M:%S')-dt).total_seconds())
write_time = lambda x: f"{x//3600:0>2}:{x%3600//60:0>2}:{x%60:0>2}"

for rid in range(csuoj.nrows):
    if rid == 0:
        for cid in range(csuoj.ncols):
            header.append(csuoj.row(rid)[cid].value)
    else:
        cr = csuoj.row(rid)
        p = Player(
            pen=read_time(cr[3].value),
            sol=int(cr[2].value),
            name=cr[1].value,
            nick=cr[-3].value
        )
        if cr[-1].value:
            print(p, end=' ')
            p.ps = cr[-1].value
            p.pen -= int(cr[-1].value) * 20 * 60
            print('change to', p)
        for cid in range(4, csuoj.ncols-7):
            if cr[cid].value.strip():
                tid = chr(65+cid-4)
                p.details[tid] = {}
                con = cr[cid].value.strip().split()
                if len(con)>1:
                    p.details[tid]['score'] = eval(con[1])
                    p.details[tid]['runningTime'] = read_time(con[0])
                else:
                    if '(' in con[0]:
                        p.details[tid]['score'] = eval(con[0])
                    else:
                        p.details[tid]['runningTime'] = read_time(con[0])
                        p.details[tid]['score'] = 0
        plr.append(p)

for itm in luogu['scoreboard']['result']:
    usr = itm['user']
    if usr['name'] in luogu_isnot_star:
        p = Player(itm['runningTime'], itm['score'], usr['name'], luogu_isnot_star.get(usr['name']))
    else:
        p = Player(itm['runningTime'], itm['score'], usr['name'], str(usr['uid']), star=True)
    for k, v in itm['details'].items():
        p.details[T2t[k]] = v
    plr.append(p)
    
print(len(plr))

import functools

def plrcmp(x1: Player, x2: Player) -> bool:
    if x1.sol > x2.sol:
        return -1
    elif x1.sol < x2.sol:
        return 1
    else:
        if x1.pen < x2.pen:
            return -1
        elif x1.pen > x2.pen:
            return 1
        else:
            return 0

plr.sort(key=functools.cmp_to_key(plrcmp))

owb = xlwt.Workbook()
ows = owb.add_sheet('flitered')

colwid = []
def clen(s):
    l = 0
    for i in s:
        if ord(i)<256: l+=1
        else: l+=2
    return l
def updcolwid(ind, ite): colwid[ind] = max(colwid[ind], clen(str(ite)))


for p, i in enumerate(header):
    ows.write(0, p, i, set_style())
    colwid.append(clen(i))


rks = 1
for p, i in enumerate(plr):
    ows.row(1+p).height = 500
    if i.star:
        ows.write(1+p, 0, '*', set_style())
    else:
        ows.write(1+p, 0, rks, set_style())
        rks+=1

    ows.write(1+p, 1, i.name, set_style(star=i.star))
    updcolwid(1, i.name)

    ows.write(1+p, 2, str(i.sol), set_style())
    updcolwid(2, i.sol)

    ows.write(1+p, 3, write_time(i.pen), set_style(center=True))
    updcolwid(3, write_time(i.pen))

    for k, v in i.details.items():
        ofs = ord(k) - 65
        ostl = []
        if 'runningTime' in v:
            ostl.append(write_time(v['runningTime']))
        if v['score']!='0':
            ostl.append(f"(-{abs(v['score'])})")
        ostr = '\n'.join(ostl)
        if ostr:
            ows.write(1+p, 4+ofs, ostr, set_style(center=True))
            updcolwid(4+ofs, max(ostl, key=lambda x: clen(x)))
    ows.write(1+p, 4+tctr+0, i.nick, set_style())
    updcolwid(4+tctr+0, i.nick)
    if i.ps:
        ows.write(1+p, 4+tctr+2, f"已经去掉{i.ps}个cin罚时", set_style())
        updcolwid(4+tctr+2, f"已经去掉{i.ps}个cin罚时")

print(colwid)

for p, i in enumerate(colwid):
    ows.col(p).width = i * 300

owb.save(output)