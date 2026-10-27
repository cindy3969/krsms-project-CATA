"""연역 단계 (Rodale 대응): 25개 테마 씨앗 → 국어사전으로 후보 확장
경로 A  어휘 관계: 씨앗(테마에 맞는 뜻만)의 '비슷한말' → 1단계, 1단계의 '비슷한말' → 2단계 (양방향 링크)
경로 B  뜻풀이 역검색: 뜻풀이의 '머리말(맨 끝 어절)'이 씨앗 어간인 표제어
        예) 환희 '매우 기뻐함. 또는 큰 기쁨' → 끝 어절 '기쁨' = 씨앗 → 후보
공통 필터: 일반어, 품사 명사·동사·형용사·부사·어근(품사 없음), 접사·의존명사·감탄사 제외, 2음절 이상
사용: python deductive_expand.py <index.pkl> <out.json>
"""
import pickle, re, sys, json
from collections import defaultdict

# 테마 -> (씨앗 목록 [(표제어, 뜻 선택 부분문자열 or None)], 뜻풀이 머리말 어간 정규식)
THEMES = {
 "Logos": {
  "logic(논리)":          ([("논리", None), ("이치", "조리"), ("합리", None)], r"(논리|이치|조리|사리|합리)$"),
  "efficiency(효율)":     ([("효율", "노력"), ("능률", "일정한 시간")], r"(효율|능률)$"),
  "effective(효과)":      ([("효과", "보람"), ("효력", "보람"), ("효용", None)], r"(효과|효력|효용|보람|좋은 결과)$"),
  "profitability(수익성)": ([("수익성", None), ("수익", None), ("이익", "총수입|보탬"), ("이윤", None)], r"(수익|이익|이윤|이득|소득|남은 돈|이문)$"),
  "method(방법)":         ([("방법", "수단"), ("방식", "형식")], r"(방법|방식|수단|방도|방책|방안)$"),
  "technique(기법)":      ([("기법", "기교"), ("기술", "능력|가공")], r"(기법|기술|기교|솜씨|재주)$"),
  "scientific(과학)":     ([("과학", None), ("과학적", None)], r"(과학|과학적인 것|체계적인 지식)$"),
 },
 "Pathos": {
  "emotion(감정)":        ([("감정", "기분"), ("정서", "감정"), ("감성", "이성")], r"(감정|정서|감성|느낌|기분|마음의 움직임)$"),
  "happiness(기쁨)":      ([("기쁨", None), ("행복", "만족"), ("즐거움", None)], r"(기쁨|기뻐함|기쁜 마음|기쁜 느낌|즐거움|즐거워함|행복|흐뭇함|흡족함)$"),
  "sadness(슬픔)":        ([("슬픔", None)], r"(슬픔|슬퍼함|슬픈 마음|슬픈 느낌|서러움|서러워함|비통함|애통함|비탄)$"),
  "fear(두려움)":         ([("두려움", None), ("공포", "두렵"), ("무서움", None)], r"(두려움|두려워함|무서움|무서워함|공포|겁|겁을 냄|두렵고 무서움|불안)$"),
  "surprise(놀람)":       ([("놀라움", None), ("놀람", None)], r"(놀람|놀라움|놀라워함|깜짝 놀람|경악)$"),
  "anger(분노)":          ([("분노", None), ("노여움", None)], r"(분노|노여움|성을 냄|성냄|화를 냄|화가 남|분개|분함|분하게 여김|격분)$"),
  "disgust(혐오)":        ([("혐오", None), ("역겨움", None)], r"(혐오|미워함|싫어함|미워하고 꺼림|역겨움|증오|꺼림)$"),
 },
 "Ethos": {
  "moral(도덕)":          ([("도덕", "준칙")], r"(도덕|도리|양심|윤리)$"),
  "character(성품)":      ([("성품", "됨됨이"), ("인격", "품격"), ("품성", None)], r"(성품|인격|품성|품격|됨됨이|인품|성격)$"),
  "wisdom(지혜)":         ([("지혜", "이치")], r"(지혜|슬기|총명)$"),
  "intelligence(지능)":   ([("지능", "지혜와 재능|지적 활동"), ("지성", "지각|지적인 사고")], r"(지능|지성|지혜|재능|지적 능력)$"),
  "discern(분별)":        ([("분별", "구별|판단"), ("식별", "알아봄")], r"(분별|식별|구별|분별함|가려냄|판별)$"),
  "virtue(덕)":           ([("덕", "인격적 능력|너그|어진 덕"), ("미덕", None)], r"(덕|덕행|미덕|어진 덕|덕성)$"),
  "excellence(탁월)":     ([("탁월하다", None), ("우수", "뛰어남"), ("뛰어나다", None)], r"(뛰어나다|뛰어남|탁월하다|탁월함|우수하다|우수함|훌륭하다|훌륭함|썩 좋다)$"),
  "goodness(선함)":       ([("선", "착하여|최고 이상"), ("착하다", None), ("선량하다", None)], r"(착하다|착함|선량하다|선량함|어질다|어짊|선하다)$"),
  "goodwill(호의)":       ([("호의", "친절"), ("선의", "착한 마음|좋은 뜻")], r"(호의|선의|친절|친절함|인정|자비|좋은 뜻|베풂)$"),
  "ethical(윤리)":        ([("윤리", "도리"), ("윤리적", None)], r"(윤리|도리|윤리적임|도덕적임)$"),
  "social(사회)":         ([("사회", "공동생활|집단"), ("사회적", None)], r"(사회|공동체|공동생활|사회적인 것)$"),
 },
}
OKPOS = {"명사", "동사", "형용사", "부사", "품사 없음"}

def ok(w, s):
    return s["typ"] == "일반어" and s["pos"] in OKPOS and len(w) >= 2

def segments(defn):
    d = re.sub(r"[‘’“”'\"()「」\[\]]", "", defn)
    return [p.strip() for p in re.split(r"\.\s*또는|[.;]|,\s*또는", d) if p.strip()]

def head_eojeols(defn):
    """뜻풀이를 '. 또는', ';' 등으로 나눈 각 구절의 마지막 어절"""
    d = re.sub(r"[‘’“”'\"()「」\[\]]", "", defn)
    parts = re.split(r"\.\s*또는|[.;]|,\s*또는", d)
    heads = []
    for p in parts:
        toks = p.strip().split()
        if toks:
            heads.append(toks[-1])
            # 'A고 B' 병렬: '두렵고 무서움' -> '두렵고'도 머리말로 인정
            if len(toks) >= 2 and re.search(r"(고|며|하고)$", toks[-2]):
                heads.append(toks[-2])
    return heads

def main(idx_path, out_path):
    idx = pickle.load(open(idx_path, "rb"))
    synG = defaultdict(set)
    for w, ss in idx.items():
        for s in ss:
            for t in s["syn"]:
                synG[w].add(t); synG[t].add(w)
    rows = []           # (dim, theme, word, path, level, via, defn)
    seed_log = []
    for dim, themes in THEMES.items():
        for theme, (seeds, head_re) in themes.items():
            seen = {}
            hre = re.compile(r"(^|\s)" + head_re)
            seed_words = set()
            for sw, sel in seeds:
                senses = [s for s in idx.get(sw, []) if s["typ"] == "일반어" and (sel is None or re.search(sel, s["defn"]))]
                seed_log.append(dict(dim=dim, theme=theme, seed=sw, n_senses=len(senses),
                                     senses=[s["defn"][:60] for s in senses]))
                if not senses:
                    continue
                seed_words.add(sw)
                seen.setdefault(sw, ("씨앗", 0, "", senses[0]["defn"]))
                # 경로 A: 선택한 뜻의 비슷한말(1단계) + 역방향 링크
                lvl1 = set(t for s in senses for t in s["syn"])
                if sel is None:   # 뜻을 하나로 특정한 씨앗은 역방향 링크를 쓰지 않음(다른 뜻의 비슷한말 유입 방지)
                    lvl1 |= {w for w in synG.get(sw, ()) if any(sw in x["syn"] for x in idx.get(w, []))}
                for t in lvl1:
                    if t in idx and any(ok(t, x) for x in idx[t]):
                        seen.setdefault(t, ("A 비슷한말", 1, sw, next(x["defn"] for x in idx[t] if ok(t, x))))
                for t1 in lvl1:
                    for t2 in synG.get(t1, ()):
                        if t2 in idx and any(ok(t2, x) for x in idx[t2]):
                            seen.setdefault(t2, ("A 비슷한말", 2, t1, next(x["defn"] for x in idx[t2] if ok(t2, x))))
            # 경로 B: 뜻풀이 머리말 역검색
            for w, ss in idx.items():
                if w in seen:
                    continue
                for s in ss:
                    if not ok(w, s) or s["cat"] or s["defn"].startswith("→"):          # 전문 분야 뜻(화학·법률 등) 제외
                        continue
                    if any(len(seg.split()) <= 4 and hre.search(seg) for seg in segments(s["defn"])):
                        seen[w] = ("B 뜻풀이", 1, "머리말", s["defn"])
                        break
            for w, (path, lvl, via, defn) in seen.items():
                rows.append(dict(dim=dim, theme=theme, word=w, path=path, level=lvl, via=via, defn=defn[:120]))
    json.dump(dict(rows=rows, seeds=seed_log), open(out_path, "w", encoding="utf-8"), ensure_ascii=False)
    from collections import Counter
    print("rows", len(rows), "unique words", len({r["word"] for r in rows}))
    print(Counter((r["dim"], r["path"]) for r in rows))
    for t in sorted({(r["dim"], r["theme"]) for r in rows}):
        n = [r for r in rows if (r["dim"], r["theme"]) == t]
        print(t, len(n), Counter(r["path"] for r in n))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
