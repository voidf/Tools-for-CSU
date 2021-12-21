import os, sys, random, datetime
import string
charset = string.digits + string.ascii_letters + string.punctuation

def randstr(l):
    return ''.join(random.choices(charset, k=l))

exe1 = 'sol.py'

exe2 = '44.exe'

f_prefix = 'X_huge'

for i in range(22):

    # tc = random.randint(1,10)
    # T = 4000
    # tc = 4000
    # n = random.randint(3,9191)
    # tc = random.randint(1,4000)

    # lee = random.randint(1, 2000)
    # fn = f'IN/test_{i}.in'
    fn = f'in/{f_prefix}_{i}.in'
    fo = f'out/{f_prefix}_{i}.out'

    with open(fn, 'w') as f:
        n = random.randint(0, int(2e7+4e6))
        

        # for ti in range(n):
            # t = random.randint(1,int(T))

            # x = random.randint(int(-1e9),int(1e9))
            # y = random.randint(int(-1e9),int(1e9))
        f.write(f"{n}\n")
    st = datetime.datetime.now()
    res1 = os.popen(f'{exe1} < {fn} > {fo}').read().strip()
    ed = datetime.datetime.now()
    print(f'{exe1} < {fn} > {fo}')
    print(f"{i}:",(ed-st).microseconds/1000,"ms")

    # res2 = os.popen(f'{exe2} < test.data').read().strip()
    # if res1!=res2:
    #     print(f"{exe1} ====>")
    #     print(res1)
    #     print('DIFFERS =====')
    #     print(res2)
    #     print(f"{exe2} <====")
        # break
    if i%1000 == 0:
        print(f'testing {i+1}th data...')