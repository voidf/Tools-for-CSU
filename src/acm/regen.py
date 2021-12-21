import os, sys, random, datetime

std = './a.out'

for i in os.listdir('in'):
    if i[-3:]=='.in':
        fn = i[:-3]
        fi = f'in/{fn}.in'

        with open(fi, 'r') as f:
            s = f.read()
        with open(fi, 'w') as f:
            f.write(s.replace('\r', ''))

for i in os.listdir('out'):
    if i[-4:]=='.out':
        fn = i[:-4]
        fo = f'out/{fn}.out'
        with open(fo, 'r') as f:
            s = f.read()
        with open(fo, 'w') as f:
            f.write(s.replace('\r', ''))
        
        print(fn)
        # os.system(f'{std} < {fi} > {fo}')