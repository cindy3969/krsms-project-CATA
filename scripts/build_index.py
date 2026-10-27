"""표준국어대사전(2026-10-12판) JSON -> 표제어별 뜻풀이·비슷한말 색인"""
import json, glob, re, pickle
from collections import defaultdict
def clean(w):
    return re.sub(r"[\d\-\^ ]", "", w or "")
idx = defaultdict(list)       # 표제어 -> [sense dict]
for f in sorted(glob.glob('/tmp/claude-0/stdict/*.json')):
    for it in json.load(open(f, encoding='utf-8'))['channel']['item']:
        wi = it['word_info']; w = clean(wi['word'])
        for p in wi.get('pos_info', []):
            for cp in p.get('comm_pattern_info', []):
                for s in cp.get('sense_info', []):
                    rel = [(x['type'], clean(x.get('word'))) for x in s.get('lexical_info', []) if x.get('word')]
                    idx[w].append(dict(word=wi['word'], pos=p.get('pos', ''), sense=s['sense_code'],
                                       defn=s.get('definition', ''), typ=s.get('type', ''),
                                       cat=[c.get('cat') for c in s.get('cat_info', [])] if s.get('cat_info') else [],
                                       syn=[w2 for t, w2 in rel if t == '비슷한말'],
                                       ant=[w2 for t, w2 in rel if t == '반대말'],
                                       ref=[w2 for t, w2 in rel if t == '참고 어휘']))
pickle.dump(dict(idx), open('/home/claude/stdict/index.pkl', 'wb'))
print('headwords', len(idx), 'senses', sum(len(v) for v in idx.values()),
      'senses with 비슷한말', sum(1 for v in idx.values() for s in v if s['syn']))
