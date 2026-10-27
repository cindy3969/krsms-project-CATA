"""DIPS 사업계획서 PDF -> 4개 분석 항목 텍스트 추출
항목: ITEM(아이템(기술) 개요 중 '개발 동기' 제외) / MOTIV(창업아이템 개발 동기 및 목적) /
      DOM(국내(내수) 시장 진출 현황 및 계획) / FOR(해외시장 진출 현황 및 계획)
- 2025 양식: 가로 2-up 페이지 -> 좌/우 반쪽을 순서대로 읽음 / 2026 양식: 세로 1단
- 헤딩은 공백·괄호를 지우고 비교 (PDF에서 '1. 아이템기술(   ) 개요'처럼 괄호가 밀리거나 번호가 빠지는 경우 대응)
"""
import re, sys, json, glob, os
import pymupdf

def page_text(p):
    r = p.rect
    if r.width > r.height * 1.2:
        mid = r.width / 2
        L = p.get_text(clip=pymupdf.Rect(0, 0, mid, r.height), sort=True)
        R = p.get_text(clip=pymupdf.Rect(mid, 0, r.width, r.height), sort=True)
        return L + "\n" + R
    return p.get_text(sort=True)

def norm(s):
    return re.sub(r"[\s()（）\[\]·‧∙ㆍ]", "", s)

NUM1 = r"(?:[1-4]\.)?"
NUM2 = r"(?:[1-4]-[1-9]\.?)?"
H_ITEM  = re.compile(rf"^{NUM1}아이템기술개요$|^{NUM1}창업아이템기술개요$")
H_MAJOR = re.compile(rf"^{NUM1}(사업화계획|사업화전략|팀구성|자금소요|투자유치계획|사업추진일정)$|^[1-4]\.(사업화|팀구성|자금|성장전략|기대효과)")
H_MOTIV = re.compile(rf"^{NUM2}창업아이템의?개발동기(및목적)?$|^{NUM2}개발동기및목적$")
H_ITEMSUB = re.compile(rf"^{NUM2}창업아이템의?(제품,?서비스혹은기술)?(소개|차별성|비즈니스모델BM|비즈니스모델|개선과제.*|기술개요.*)$|^{NUM2}아이템제품,?서비스혹은기술소개$")
H_DOM   = re.compile(rf"^{NUM2}국내내수시장진출현황및계획$")
H_FOR   = re.compile(rf"^{NUM2}해외시장진출현황및계획$")
H_FOREND = re.compile(rf"^(?:[1-4]-3\.?)?(사업추진일정.*|사업전체로드맵|투자유치.*|자금운용.*|중장기.*|사업추진일정및자금운용계획)$")
H_SUB2  = re.compile(r"^[1-4]-[1-9]\.\S")

def extract(path):
    doc = pymupdf.open(path)
    lines = []
    for p in doc:
        lines += [l.rstrip() for l in page_text(p).splitlines()]
    out = {"ITEM": [], "MOTIV": [], "DOM": [], "FOR": []}
    sec, in_item = None, False
    for raw in lines:
        k = norm(raw)
        if not k:
            continue
        short = len(k) <= 40
        if short and H_ITEM.match(k):
            in_item, sec = True, "ITEM"; continue
        if short and H_MAJOR.match(k):
            in_item, sec = False, None; continue
        if short and H_MOTIV.match(k):
            sec = "MOTIV"; continue
        if short and in_item and H_ITEMSUB.match(k):
            sec = "ITEM"; continue
        if short and H_DOM.match(k):
            in_item, sec = False, "DOM"; continue
        if short and H_FOR.match(k):
            in_item, sec = False, "FOR"; continue
        if short and sec in ("DOM", "FOR") and H_FOREND.match(k):
            sec = None; continue
        if short and H_SUB2.match(k):
            if in_item and sec == "MOTIV":
                sec = "ITEM"
            elif sec == "FOR":
                sec = None
            continue
        if sec is None:
            continue
        if k.startswith("※") or re.fullmatch(r"<.*>|-\d+-|\d{1,2}\.?", k):
            continue
        if re.fullmatch(r"순번.*|국가명.*|구분.*", k) and len(k) < 40:
            continue
        out[sec].append(raw.strip())
    return {s: "\n".join(v) for s, v in out.items()}

def meta(path):
    f = os.path.basename(path)
    year = "2025" if "2025" in os.path.basename(os.path.dirname(path)) else "2026"
    m = re.search(r"(로보틱스|첨단제조|일반|민간|부처)\s*(\d+)", f)
    track = m.group(1) if m else ""
    firm = re.sub(r"\.pdf$", "", f).split("_")[-1]
    firm = re.sub(r"^\d{8}", "", firm)
    return dict(file=f, year=year, track=track, firm=firm)

if __name__ == "__main__":
    root, outp = sys.argv[1], sys.argv[2]
    res = []
    for path in sorted(glob.glob(os.path.join(root, "*", "*.pdf"))):
        try:
            secs, err = extract(path), ""
        except Exception as e:
            secs, err = {"ITEM": "", "MOTIV": "", "DOM": "", "FOR": ""}, str(e)
        res.append({**meta(path), **secs, "error": err})
    json.dump(res, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
