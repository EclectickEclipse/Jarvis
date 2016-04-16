#! /usr/local/bin/python

def cutRange():
    import sys
    term = 'broadcast '
    base_net = 'XXX.XXX.XXX.XXX'
    try: line = sys.stdin.readline()
    except: return None
    line_parse = line[(line.index(term) + len(term)):(
        line.index(term) + len(term) + len(base_net))]
    x = []
    for char in line_parse: x.append(char)
    completed = False
    while not completed:
        if x.pop() != '.': pass
        else:
            x.append('.')
            x.append('0-255')
            break

    retu = ''
    for val in x: retu += str(val)
    return retu

import sys
sys.stdout.write(cutRange())