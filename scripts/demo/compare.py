import json,re,sys
sys.path.insert(0,'/home/claude')
from screen_lpe import SCREEN
from kiwipiepy import Kiwi
k=Kiwi()
lex={}
for dim,th in SCREEN.items():
    for t,ws in th.items():
        for w in ws.split(): lex.setdefault(w.lstrip('!'),set()).add(dim)
S=json.load(open('demo/sentences.json'))
lab={}
for line in open('demo/labels.txt'):
    sid,rest=line.strip().split(' ',1); c,why=rest.split('|',1); lab[sid]=(c,why)
CONTENT={'NNG','NNP','VV','VA','XR','MAG','SL','NR'}
for s in S:
    hits={'Logos':[],'Pathos':[],'Ethos':[]}; npr=0
    for t in k.tokenize(s['text']):
        tag=t.tag.split('-')[0]
        if tag not in CONTENT: continue
        npr+=1
        f=t.form+'다' if tag in('VV','VA') else t.form
        for cand in (f,t.form,t.form+'하다'):
            if cand in lex:
                for d in lex[cand]: hits[d].append(t.form)
                break
    s['hits']=hits; s['npr']=npr; s['code'],s['why']=lab[s['sid']]
json.dump(S,open('demo/scored.json','w'),ensure_ascii=False)
for doc in ('A','B'):
    ss=[s for s in S if s['sid'][0]==doc]
    NP=sum(s['npr'] for s in ss)
    dl={d:sum(len(s['hits'][d]) for s in ss) for d in hits}
    coded=[s for s in ss if s['code']!='N']
    sl={c:sum(c in s['code'] for s in coded)/len(coded) for c in 'LPE'}
    print(doc,ss[0]['firm'],'sent',len(ss),'coded',len(coded),'ΣPr',NP)
    print(' dict counts',dl,' L P E %',{d:round(v/NP*100,2) for d,v in dl.items()},' PE=',round((dl['Pathos']+dl['Ethos'])/dl['Logos'],3))
    print(' sent share',{c:round(v,3) for c,v in sl.items()},' PE=',round((sl['P']+sl['E'])/sl['L'],3))
    # sentence-level agreement
    for c,d in (('L','Logos'),('P','Pathos'),('E','Ethos')):
        tp=sum(1 for s in coded if c in s['code'] and s['hits'][d]); fn=sum(1 for s in coded if c in s['code'] and not s['hits'][d])
        fp=sum(1 for s in coded if c not in s['code'] and s['hits'][d])
        print(f'  {c}: coded {tp+fn}, dict hit&coded {tp}, missed {fn}, dict hit but not coded {fp}')
