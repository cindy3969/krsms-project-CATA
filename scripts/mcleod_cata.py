"""
McLeod et al. (2022, JMS) logos/pathos/ethos CATA replication demo
- Dictionary: Table II (891 base words, transcribed from the paper)
- Scoring:   L = ΣL/ΣPr, P = ΣP/ΣPr, E = ΣE/ΣPr ; PE Rhetoric = (P+E)/L
- Stems:     paper says "appropriate stem words were also counted where suitable"
             -> here approximated with inflectional variants (s/es/ed/ing/...)
             (an ASSUMPTION; the paper does not specify the exact rule or program)
"""
import re
from collections import Counter

def split(s):
    return [w.strip() for w in s.split(",") if w.strip()]

TABLE_II = {
 "logos": {
  "logic": split("logic, reason, judicious, logistic, politic, astute, infer, cogent, synthesis, sane, sound-judgment, good-sense, sober, presence-of-mind, analytic, common-sense, deductive, inductive, consequence, rational, practical, pragmatic, sensible, advisable, well-advised, well-argued, well-grounded, well-founded, plausible"),
  "efficiency": split("efficiency, yield, minimum, maximum, bargain, rate, stabilize, steady, supply, reduce, residual, consolidate, generate, qualification, prepare, productive, produce, adept, economic, metric, deficiency, cost, capacity"),
  "effective": split("effective, allowance, contingent, award, reward, eligible, realize, retain, benefit, notable, persistent, responsible, effectual, adequate, sufficient, function, operate, actual, real, effect"),
  "profitability": split("profitability, account, expense, accumulate, asset, loss, compensation, refund, transaction, hedge, tax, amortize, annuity, amount, capita, bonds, balance sheet, bankrupt, purchase, bid, loan, insurance, endowment, lease, fee, average, cash, estimate, receivable, finance, collateral, credit, commodity, stock, convertible, rent, exchange, liability, invest, incentive, performance, derivative, debt, equity, overdraft, deposit, dividend, fund, dollar, price, currency, margin, premium, liquidate, settlement, sale, sell, expenditures, earn, proceeds, revenue, win, paid, EBIT, EBITDA, gain, figures, income, numbers, net, bottom-line, remunerative, recompense, fruitful, surplus, lucrative, excess, pay, advantage, well-paying, efficacy, money, opportunity, time, worthwhile, increment, valuable, augmentation, invaluable, conducive, improve, better, budget, exploit, achieve, capital"),
  "method": split("method, plan, activities, allocate, contract, assign, authorize, model, require, policy, impose, structure, restructure, expect, unconditional, conditional, modify, orchestrate, mode, uniform, process, constant, procedure, business-like, means, step-by-step, tabulation, exact, formula, meticulous, strategy, practice, regulate, order, scheme, system, straighten-out, design, lay-out, discipline, centralize, routine, normalize, program, standard, arrange, code, alphabetize, guide, customize, pattern, rule, sequence, distribution, manoeuvre, engineering"),
  "technique": split("technique, certificate, adjust, specified, mandatory, fix, correct, develop, deal, trade, systematic, reliable, detailed, approach, tactic, mode-of-operation, standard-operating-procedure, ability, capability, skill, execution, proficiency"),
  "scientific": split("scientific, advance, claim, report, information, variable, prove, measure, demographic, probable, classify, reclassify, test, observe, variance, interest, learn, predict, compute, controlled, fact, versed, thorough, laws, informed, calculate, reality, precise, mathematic, know, specialization, empirical, technology, philosophy, research, verifiable, experiment, quantitative, trial-and-error, investigation, expert, application, objective, rigour, theorist, sophistication, analyse, evaluate, data, technical, educate, scholarly, well-schooled, academic, accurate"),
 },
 "pathos": {
  "emotion": split("emotion, electrify, energetic, enthusiastic, excite, fiery, gung-ho, passion, impassion, provocative, lively, rouse, spirited, stirring, vehement, vigour, invigorate, reinvigorate, vivid, intense, eager, psyched, exuberance, feel, volatile, avid, sentiment, zest, obsess, sensation, inspire, suffer, affect, rave, vulnerable, emotive, frantic, sensitive, overwrought, vitalize, ecstatic, feverish, carried-away, fanatic, love, theatrics, fierce, laugh, impatience, severe, urgency, hysterical, impulsive, strike-a-chord, ecstasy, hasty, heartstrings, thrill, turbulent, poignant, tumultuous, pathetic, disturb, heartfelt, compulsion, excruciate, emphatic, adore, soul-stirring, evoke, ambitious, expressive, eloquent, aspire, demonstrative, fervent, touchy, dramatic, fervid, zeal, overzealous, emote, earnest, determination, tense, fervour, relish, crazy, craze"),
  "happiness": split("happiness, glee, pleasure, delight, jolly, enjoy, enchant, paradise, heartily, heart-and-soul, elated, serenity, gratification, light-heartedly, glad, pleased, cheerful, satisfy, well-pleased, joy, bliss, exhilaration"),
  "sadness": split("sadness, solemn, downtrodden, heartbreak, grief, unhappy, despair, despondent, oppress, misery, painful, woe, downcast, pleasureless, agony, downhearted, joyless, heartache, dispirit, cheerless, bummed, sorry, broken-heart, heartbroken, melancholy, pity, mourn, dismal, dreary, sombre, deject, depress, discourage, lament, dishearten, deplorable, sorrow, grieve, uncheerful, regret, gloom, bleak"),
  "fear": split("fear, dread, nightmare, hideous, fright, phobia, ghastly, terror, afraid, eerie, horror, scare, grisly, panic, suspect, gruesome, alarm, forebode, unspeakable, trepidation, misgiving, shy, terrify, cower, concern, mistrust, apprehensive, distrust, worry, qualm, uneasy, nervous, angst, tremble, appal, anxious, overanxious, anguish, terrible, timid, anxiety, grim, dire, faint-hearted, coward, cautious, distress, intimidate, hesitate, harrow, reluctant, awful, unsure, horrible, horrendous"),
  "surprise": split("surprise, unforeseen, astonish, unanticipated, amaze, sudden, stun, jolting, ambush, jarring, blitz, bombshell, eye-opener, revelation, reveal, astound, wonder, awe, marvel, miracle, shock, sneak-attack, out-of-the-ordinary, incredible, unusual, uncommon, unfamiliar"),
  "anger": split("anger, enrage, ire, infuriate, wroth, fight, irate, contentious, hostile, provoke, belligerent, wrath, arouse, furious, spite, livid, rage, distraught, savage, fury, agitate, upset, violent, threaten, rant, seethe, resent, rabid, irritate, frenzy, gall, irk, mad, rile, aggravate, indignant, ill-will, miff, stirred-up, bad-blood, exasperate, petulant, exacerbate, discontent, affront, uptight, insult, humiliate, mortify"),
  "disgust": split("disgust, despicable, disappoint, revolt, sicken, objectionable, off-putting, offend, dissatisfaction, obnoxious, disapproval, nasty, repulse, displeasure, unpleasant, displease, sick-and-tired, sick-of, insufferable, scandal, fed-up, outrageous, aversion, annoy, reprehensible, distaste, unsavoury, vile, foul, vulgar, odious, stink, abhorrent, abomination, loath, detestable, hatred, hate, dislike, unlikable, repugnant, animosity, repel"),
 },
 "ethos": {
  "moral": split("moral, righteous, noble, straightforward, principle, innocent, precept, proverb, manners, fidelity, seemliness, conscience, corrupt"),
  "character": split("character, reputation, repute, status, good-standing, glory, prestige, esteem, courage, strength, fortitude, sincere, resolute, brave, heroic, self-reliant, strive, tenacious, valiant"),
  "wisdom": split("wisdom, insight, foresight, prudence, wise, perceptive, shrewd, enlighten, diplomatic, careful, tactful, guru, statesman, elder, luminary"),
  "intelligence": split("intelligence, cognition, ingenious, ingenuity, intellect, smart, aptitude, wit, brainpower, mastermind, cerebral, genius, literate, well-read, acumen, brilliance, gifted, savvy"),
  "discern": split("discern, perceive, clever, decipher, figure-out, good-eye, ascertain, distinguish, intuition, pick-out, recognize, clairvoyance, differ, farsighted, discriminate, judge, scrutinize, delineate, detection, keen, comprehension, aware, discreet, watch, mindful, alert, tell, apart, understand"),
  "virtue": split("virtue, care, forgive, un-corrupt, incorrupt, honour, decency, upstanding, justice, modest, grace, worthy, rely, charity, impeccable, scrupulous, loyal, truth, creditable, commendable, praiseworthy, right-minded"),
  "excellence": split("excellence, the-best, matchless, pre-eminence, peerless, mastery, unparalleled, perfect, quality, sterling, supremacy, first-class, merit, impressive, admirable, first-rate, tip-top, extraordinary, remarkable, splendid, great, super, exceptional, superior, standout, outstanding, supreme, transcendent, surpass, excel"),
  "goodness": split("goodness, good, nobility, wholesome, big-hearted, soft-hearted, good-hearted, warm-hearted, generous, quintessence, help, harmony, grateful, courteous, mercy, thoughtful, tolerant"),
  "goodwill": split("goodwill, beneficence, gentle, kindness, humane, lenient, fatherly, motherly, sympathy, empathy, paternal, maternal, gracious, compassion, broadminded, gift, accommodate, donate, oblige, benevolent, well-meaning, aid, altruistic, unselfish, considerate, benign, bounteous, open-handed, philanthropy, humanitarian, munificent"),
  "ethical": split("ethical, upright, honest, pure, proper, fair, lofty, integrity, golden-rule, authentic, believable, credible, decent, devoted, equitable, even-handed, faithful, forthright, genuine, respectable, law-abiding, lawful, trust"),
  "social": split("social, good-natured, companion, polite, sociable, cooperation, community, communal, society, civic, civil, congenial, neighbourly, socially-responsible, hospitable, fraternity, brotherhood, sisterhood, cordial, hearty, humanity, agreeable, human-race, humankind, mankind, welfare, volunteer, general-public, outreach, camaraderie, mediator, fellowship, family, citizen, collaboration, accessibility, openness, easy-going, support, receptive, mutual, sharing, unite, team, friend"),
 },
}

# ---------- stem variants (assumption: inflectional only) ----------
def variants(w):
    w = w.lower()
    v = {w}
    if w.endswith("e"):
        v |= {w + "s", w + "d", w[:-1] + "ing", w + "r", w + "rs"}
    elif w.endswith("y") and len(w) > 3 and w[-2] not in "aeiou":
        v |= {w[:-1] + "ies", w[:-1] + "ied", w + "ing"}
    else:
        v |= {w + "s", w + "es", w + "ed", w + "ing", w + "er", w + "ers"}
    return v

def build_matchers():
    single, multi = {}, []          # single-token lookup ; multiword regexes
    for dim, cats in TABLE_II.items():
        for cat, words in cats.items():
            for w in words:
                parts = re.split(r"[-\s]+", w.lower())
                if len(parts) == 1:
                    for form in variants(parts[0]):
                        single.setdefault(form, (dim, cat, w))
                else:
                    pat = r"\b" + r"[-\s]+".join(map(re.escape, parts)) + r"s?\b"
                    multi.append((re.compile(pat), dim, cat, w))
    return single, multi

SINGLE, MULTI = build_matchers()

def score(text):
    t = text.lower().replace("’", "'")
    tokens = re.findall(r"[a-z]+", t)               # ΣPr: alphabetic words
    numerals = re.findall(r"\$?\d[\d,.]*%?", t)       # 'numbers' that are NOT words
    hits = []
    for m in MULTI:                                   # multiword first
        for _ in m[0].finditer(t):
            hits.append((m[3], m[1], m[2]))
    for tok in tokens:
        if tok in SINGLE:
            dim, cat, base = SINGLE[tok]
            hits.append((tok if tok == base.lower() else f"{tok}→{base}", dim, cat))
    c = Counter(h[1] for h in hits)
    n = len(tokens)
    L, P, E = (c[d] / n for d in ("logos", "pathos", "ethos"))
    pe = (P + E) / L if L else float("nan")
    return dict(n_words=n, n_numerals=len(numerals), hits=hits,
                logos=c["logos"], pathos=c["pathos"], ethos=c["ethos"],
                L=L, P=P, E=E, PE_Rhetoric=pe)

# ---------- inductive step demo: words used >= k times ----------
STOP = set("""a an the and or of to in for on by with as at from that this these those we our us
is are was were be been being have has had it its which who whom their they them than then
there here not no but if also such other more most each every all any some into over under
about after before between through during including include includes""".split())

def inductive_candidates(text, k=3):
    toks = [w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP and len(w) > 2]
    freq = Counter(toks)
    out = []
    for w, f in freq.most_common():
        if f < k: break
        out.append((w, f, "IN DICT" if w in SINGLE else "→ rater review"))
    return out

# ---------- SEC filing excerpts (quoted in McLeod et al. 2022, Table I) ----------
DOCS = {
 "Dunkin' Brands – Strategic Challenge 1": """Focus on store-level economics. In recent years, we have undertaken significant initiatives to further enhance store-level economics for our franchisees that we believe have further increased franchisee profitability. For example, we reduced the upfront capital expenditure costs to open an end-cap restaurant with a drive-thru by approximately 23% between fiscal 2008 and fiscal 2010. Additionally, between fiscal 2008 and the first quarter of fiscal 2011, we believe we have facilitated approximately $220 million in franchisee cost reductions primarily through strategic sourcing, as well as through other initiatives, such as rationalizing the number of product offerings to reduce waste and reducing costs on branded packaging by reducing the colour mix in graphics. We believe that the majority of these cost savings represent sustainable improvements to our franchisees supply costs, with the remainder dependent upon the outcome of future supply contract re-negotiations, which typically occur every two to four years.""",
 "Dunkin' Brands – Strategic Challenge 2": """In the US, Baskin-Robbins core strengths are its national brand recognition, 65 years of heritage and #1 position in the QSR industry for servings of hard serve ice cream. While the Baskin-Robbins US segment has experienced decreasing comparable store sales in each of the last three years due primarily to increased competition and decreased consumer spending in each year, and the number of Baskin-Robbins US stores has decreased since 2008, we believe that we can capitalize on the brands strengths and generate renewed excitement for the brand, including through our recently introduced More Flavors, More Fun marketing campaign.""",
 "Vera Bradley – Employee Discussion 1": """We were founded in 1982 by two friends, Barbara Bradley Baekgaard and Patricia R. Miller, who built our company around their passion for design and commitment to customer service. We believe our founders created a unique company culture that attracts passionate and motivated employees who are excited about our products and our brand. Our employees share our founders' commitment to Vera Bradley customers. We believe that a fun, friendly and welcoming work environment fosters creativity and collaboration and that, by empowering our employees to become personally involved in product design, testing and marketing, they become passionate and devoted brand advocates.""",
 "Vera Bradley – Employee Discussion 2": """Historically, we worked with independent sales consultants who were not our employees, but most of whom worked exclusively for us. In October 2007, we began transitioning our sales force in-house. We believe that having an in-house sales force results in more consistent brand presentation and messaging, enhanced support for our Indirect retailers and a more predictable, scalable and cost efficient model. As of 31 July 2010, our sales team consisted of 87 in-house, full-time sales consultants. The compensation structure for our sales consultants consists of a combination of fixed pay and sales based incentives.""",
}

if __name__ == "__main__":
    total = sum(len(w) for cats in TABLE_II.values() for w in cats.values())
    print(f"Table II base words transcribed: {total} (paper reports 891)")
    allw = [w.lower() for cats in TABLE_II.values() for ws in cats.values() for w in ws]
    dup = [w for w, n in Counter(allw).items() if n > 1]
    print("duplicates across dimensions:", dup or "none")
    print()
    for name, txt in DOCS.items():
        r = score(txt)
        print("=" * 78); print(name)
        print(f"ΣPr={r['n_words']} words | numerals (not counted as words)={r['n_numerals']}")
        print(f"ΣL={r['logos']}  ΣP={r['pathos']}  ΣE={r['ethos']}")
        print(f"L={r['L']:.4f}  P={r['P']:.4f}  E={r['E']:.4f}  PE Rhetoric=(P+E)/L={r['PE_Rhetoric']:.3f}")
        for dim in ("logos", "pathos", "ethos"):
            ws = [f"{h[0]}({h[2]})" for h in r["hits"] if h[1] == dim]
            print(f"  {dim:6}: {', '.join(ws) if ws else '-'}")
    print("=" * 78)
    allt = " ".join(DOCS.values())
    print("Inductive step demo (words used >= 3 times across the excerpts):")
    for w, f, s in inductive_candidates(allt, 3):
        print(f"  {w:15} {f:3}  {s}")
