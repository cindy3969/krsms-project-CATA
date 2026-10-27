# 한국어 Logos·Pathos·Ethos CATA 사전 구축 (McLeod et al., 2022 재현)

DIPS 초격차 스타트업 프로젝트(로보틱스·첨단제조) 사업계획서의 수사(logos·pathos·ethos)를 측정하기 위해,
McLeod et al. (2022, *JMS*)의 사전 구축 절차(Short et al., 2010)를 한국어 자원으로 다시 밟는 프로젝트.
영어 Table II를 번역해 쓰지 않고, 같은 25개 테마에서 출발해 한국어 사전과 한국어 사업계획서로 사전을 새로 만든다.

> 비공개 저장소. `data/private/`에는 지원기업 사업계획서에서 추출한 비공개 텍스트가 들어 있으므로 외부 공유 금지.

## 절차와 진행 상태

| 단계 | 원 논문 | 한국어판 | 상태 |
| --- | --- | --- | --- |
| ① 테마 | logic·emotion·moral character + Ozen & Berkman(2007) + Ekman(1992) + Aristotle 3범주 | 같은 25개 테마의 한국어 씨앗 | 완료 |
| ② 연역 | Rodale(1978) *The Synonym Finder*로 유의어 확장 | 표준국어대사전·우리말샘의 비슷한말 관계 + 뜻풀이 역검색 | 진행 중 (우리말샘 데이터 대기) |
| ③ 귀납 | 투자설명서마다 3회 이상 쓰인 단어 중 관련 단어 추가 | 사업계획서마다 3회 이상 쓰인 형태소(Kiwi 원형) 중 관련 단어 추가 | 빈도목록 4,391개, 1차 선별 279개 |
| ④ 평정 | 저자 3인, Holsti | 연구자 3인, Holsti·Krippendorff α | 대기 |
| ⑤ 전문가 | 외부 3인 추가 제안 + 5인 만장일치 | 동일 | 대기 |

## 폴더

| 경로 | 내용 |
| --- | --- |
| `scripts/extract_sections.py` | 사업계획서 PDF → 4개 항목(아이템 개요·개발 동기·국내시장·해외시장) 텍스트 추출 |
| `scripts/inductive.py` | 귀납 단계: 문서별 3회 이상 형태소 집계 (줄바꿈 조각 결합, 1음절 제외) |
| `scripts/screen_lpe.py`, `build_lpe.py` | 귀납 빈도목록 → 테마 관련 단어 1차 선별 |
| `scripts/build_index.py` | 표준국어대사전 JSON → 표제어·뜻풀이·비슷한말 색인 |
| `scripts/mcleod_cata.py` | 원 논문 Table II로 영어 CATA 점수 재현 (참고용) |
| `data/dictionaries/stdict/` | 표준국어대사전 전체 JSON (2026-10-12판) |
| `data/dictionaries/opendict/` | 우리말샘 전체 JSON (2026-10-04판) — 추가 예정 |
| `data/derived/inductive_frequency_list.csv` | 귀납 빈도목록 (형태소, 품사, 3회↑ 문서 수 등) |
| `data/derived/TableII_translation_reference.xlsx` | Table II 번역본 — 사전 구축에는 쓰지 않고 누락 대조용 |
| `data/private/business_plan_sections.json` | 사업계획서 314건의 4개 항목 추출 텍스트 (2025·2026 신규지원) |
| `data/private/inductive_counts.json` | 문서별 형태소 수(ΣPr)와 후보 예문 |
| `data/private/DIPS_LPE후보_단어목록.xlsx` | LPE 1차 선별 후보 + 평정자 입력칸 |

## 알려진 사항

- 표준국어대사전은 뜻 509,143개 중 비슷한말이 달린 뜻이 20,461개(4%)뿐이라 Rodale식 확장의 단독 자료로는 부족함 → 우리말샘 어휘 관계와 뜻풀이 역검색을 함께 사용.
- 사업계획서 314건 중 14건은 추출 확인 필요(스캔본 4, 이미지 위주 3, 제목 형식 차이 7).

## 출처

- 국립국어원 표준국어대사전, 우리말샘 — 사전 내려받기 자료. 이용 조건에 따라 출처 표시.
- McLeod, M. S., Sears, J. B., Chandler, G. N., Payne, G. T., & Brigham, K. H. (2022). Rhetoric, risk, and investment. *Journal of Management Studies*, 59(7), 1657–1687.
- Short, J. C., Broberg, J. C., Cogliser, C. C., & Brigham, K. H. (2010). Construct validation using computer-aided text analysis (CATA). *Organizational Research Methods*, 13(2), 320–347.
