import sys
import iqoptionapi
import os
print('exe', sys.executable)
print('pkg', os.path.dirname(iqoptionapi.__file__))
for root, dirs, files in os.walk(os.path.dirname(iqoptionapi.__file__)):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            if any(k in path.lower() for k in ['buy','candles','ws','http']):
                print(path)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                        txt = fh.read()
                        if 'eur' in txt.lower() or 'active' in txt.lower() or 'buy' in txt.lower():
                            print('\tcontains interesting keywords')
                except Exception as e:
                    print('err', e)
print('done')
