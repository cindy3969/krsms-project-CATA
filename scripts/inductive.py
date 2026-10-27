"""귀납 단계: 사업계획서별로 3회 이상 등장한 내용 형태소를 모아 후보 목록 생성
(McLeod et al., 2022: 'compiled words used at least three times in a prospectus')
"""
import json, re, sys
from collections import Counter, defaultdict
from kiwipiepy import Kiwi

SECS = ["ITEM", "MOTIV", "DOM", "FOR"]
KEEP = {"NNG", "VV", "VA", "XR", "MAG"}
TEMPLATE = set("아이템 기술 개요 창업 개발 동기 목적 국내 내수 시장 진출 현황 계획 해외 추가 비즈니스 모델 차별성 개선 과제 고도화 목표 분석 유통 채널 판매 내용 시기 금액 실적 예상 순번 국가".split())

kiwi = Kiwi()
docs = json.load(open(sys.argv[1], encoding="utf-8"))
MIN_CHARS = 150

def join_wrapped(t):
    """PDF 줄바꿈으로 단어 중간이 끊긴 것(다\n양하게)을 이어 붙임. 글머리표로 시작하는 줄은 새 줄로 유지."""
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    out = lines[:1]
    for l in lines[1:]:
        p = out[-1]
        if re.search(r"[가-힣]$", p) and re.match(r"[가-힣]", l) and not re.match(r"^[◦○●▪▶ŸØ•\-–□■]", l):
            out[-1] = p + l
        else:
            out.append(l)
    return "\n".join(out)

def lemma(t):
    tag = t.tag.split("-")[0]
    return (t.form + "다", tag) if tag in ("VV", "VA") else (t.form, tag)

doc_counts = []           # per doc Counter of (lemma, tag)
sec_tokens = []           # per doc per section total content tokens (ΣPr 후보)
kwic = {}
for d in docs:
    c = Counter()
    ntok = {}
    for s in SECS:
        txt = join_wrapped(d[s]) if len(d[s]) >= MIN_CHARS else ""
        n = 0
        for sent in kiwi.split_into_sents(txt) if txt else []:
            toks = kiwi.tokenize(sent.text)
            for t in toks:
                tag = t.tag.split("-")[0]
                if tag in ("NNG", "NNP", "VV", "VA", "XR", "MAG", "SL", "NR"):
                    n += 1            # 분모: 내용 형태소 수
                if tag in KEEP and len(lemma(t)[0]) >= 2:   # 1음절 명사·부사(줄바꿈 조각, 의존적 명사) 제외, 용언은 '높다'처럼 원형 기준
                    key = lemma(t)
                    c[key] += 1
                    if key not in kwic and 12 <= len(sent.text) <= 160:
                        kwic[key] = (d["firm"], s, sent.text.strip())
        ntok[s] = n
    doc_counts.append(c)
    sec_tokens.append(ntok)

valid = [i for i, d in enumerate(docs) if sum(len(d[s]) >= MIN_CHARS for s in SECS) >= 3]
nvalid = len(valid)
agg = defaultdict(lambda: {"docs3": 0, "docs1": 0, "total": 0})
for i in valid:
    for k, v in doc_counts[i].items():
        a = agg[k]
        a["total"] += v
        a["docs1"] += 1
        if v >= 3:
            a["docs3"] += 1
cands = {k: v for k, v in agg.items() if v["docs3"] >= 1}
out = dict(n_docs=len(docs), n_valid=nvalid,
           cands=[dict(form=k[0], tag=k[1], **v, kwic=kwic.get(k), template=k[0] in TEMPLATE) for k, v in cands.items()],
           sec_tokens=[dict(firm=docs[i]["firm"], year=docs[i]["year"], track=docs[i]["track"], file=docs[i]["file"],
                            **{f"chars_{s}": len(docs[i][s]) for s in SECS},
                            **{f"tok_{s}": sec_tokens[i][s] for s in SECS}) for i in range(len(docs))])
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print("docs", len(docs), "valid", nvalid, "candidates(>=3 in >=1 doc)", len(cands))
