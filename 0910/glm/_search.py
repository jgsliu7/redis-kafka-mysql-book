import json, sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'D:\data\redis-kafka-mysql\0910\glm'
CH = {
 'preface': r'D:\data\redis-kafka-mysql\chapters\00-preface.md',
 'ch1': r'D:\data\redis-kafka-mysql\chapters\01-introduction\chapter.md',
 'ch2': r'D:\data\redis-kafka-mysql\chapters\02-data-structures-protocols\chapter.md',
 'ch3': r'D:\data\redis-kafka-mysql\chapters\03-lifecycle\chapter.md',
 'ch4': r'D:\data\redis-kafka-mysql\chapters\04-memory-disk\chapter.md',
 'ch5': r'D:\data\redis-kafka-mysql\chapters\05-layered-architecture\chapter.md',
 'ch6': r'D:\data\redis-kafka-mysql\chapters\06-security\chapter.md',
 'ch7': r'D:\data\redis-kafka-mysql\chapters\07-cluster\chapter.md',
 'ch8': r'D:\data\redis-kafka-mysql\chapters\08-storage-format\chapter.md',
 'ch9': r'D:\data\redis-kafka-mysql\chapters\09-data-sync\chapter.md',
 'ch10': r'D:\data\redis-kafka-mysql\chapters\10-summary\chapter.md',
 '后记': r'D:\data\redis-kafka-mysql\chapters\10-epilogue.md',
 '参考文献': r'D:\data\redis-kafka-mysql\chapters\11-references.md',
}
night = json.load(open(BASE + r'\night100\_stats_data.json', encoding='utf-8'))
wave = json.load(open(BASE + r'\wave2\_stats_data.json', encoding='utf-8'))

def book(ch, ln):
    lines = open(CH[ch], encoding='utf-8').read().split('\n')
    return lines[ln-1]

def find(ch=None, line=None, kw=None, src='both', limit=30, show_op=200):
    """Search night rows and wave rows by chapter/line/keyword."""
    n = 0
    results = []
    if src in ('both','night'):
        for r in night['rows']:
            if ch and r['chapter'] != ch: continue
            if line is not None:
                if line not in r.get('lines', []) and r.get('line') != line: continue
            if kw and kw not in r['quote'] and kw not in r['opinion']: continue
            results.append(('V%03d' % r['vid'], r['perspective'], r['chapter'], r.get('line'), r['quote'][:80], r['opinion'][:show_op], r['type']))
    if src in ('both','wave'):
        for r in wave['rows']:
            if ch and r['chapter'] != ch: continue
            if line is not None and r.get('line') != line: continue
            if kw and kw not in r['quote'] and kw not in r['opinion']: continue
            results.append((r['wid'], r['reader'], r['chapter'], r.get('line'), r['quote'][:80], r['opinion'][:show_op], r.get('type','')))
    for x in results[:limit]:
        print(' | '.join(str(i) for i in x))
    print('TOTAL:', len(results))

if __name__ == '__main__':
    import argparse
    a = argparse.ArgumentParser()
    a.add_argument('--ch'); a.add_argument('--line', type=int); a.add_argument('--kw')
    a.add_argument('--src', default='both'); a.add_argument('--limit', type=int, default=30)
    a.add_argument('--show', type=int, default=200)
    A = a.parse_args()
    find(A.ch, A.line, A.kw, A.src, A.limit, A.show)
