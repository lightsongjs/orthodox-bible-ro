#coding: utf-8
import json
import os

# Complete translations dictionary
# Using Unicode escape for right single quotation mark: \u2019
TRANS = {
    # JOB (Iov)
    "Job and His Family": "Iov și familia sa",
    "Attack on Job\u2019s Character": "Atacul asupra caracterului lui Iov",
    "Job Loses Property and Children": "Iov pierde averea și copiii",
    "Attack on Job\u2019s Health": "Atacul asupra sănătății lui Iov",
    "Job\u2019s Three Friends": "Cei trei prieteni ai lui Iov",
    "Job Curses the Day He Was Born": "Iov blestemă ziua nașterii sale",
    "Eliphaz Speaks Job Has Sinned": "Elifaz vorbește: Iov a păcătuit",
    "Job Is Corrected by God": "Iov este mustrat de Dumnezeu",
    "Job Replies My Complaint Is Just": "Iov răspunde: Plângerea mea este dreaptă",
    "Job My Suffering Is without End": "Iov: Suferința mea este fără sfârșit",
    "Bildad Speaks Job Should Repent": "Bildad vorbește: Iov trebuie să se pocăiască",
    "Job Replies There Is No Mediator": "Iov răspunde: Nu există mijlocitor",
    "Job I Loathe My Life": "Iov: Urăsc viața mea",
    "Zophar Speaks Job\u2019s Guilt Deserves Punishment": "Țofar vorbește: Vina lui Iov merită pedeapsă",
    "Job Replies I Am a Laughingstock": "Iov răspunde: Sunt de batjocură",
    "Job\u2019s Despondent Prayer": "Rugăciunea descurajată a lui Iov",
    "Job Chapter 14": "Capitolul 14",
    "Eliphaz Speaks Job Undermines Religion": "Elifaz vorbește: Iov subminează religia",
    "Job Reaffirms His Innocence": "Iov își reafirmă nevinovăția",
    "Job Prays for Relief": "Iov se roagă pentru alinare",
    "Bildad Speaks God Punishes the Wicked": "Bildad vorbește: Dumnezeu pedepsește pe cei răi",
    "Job Replies I Know That My Redeemer Lives": "Iov răspunde: Știu că Răscumpărătorul meu trăiește",
    "Zophar Speaks Wickedness Receives Just Retribution": "Țofar vorbește: Răutatea primește pedeapsa cuvenită",
    "Job Replies The Wicked Often Go Unpunished": "Iov răspunde: Cei răi rămân adesea nepedepsiți",
    "Eliphaz Speaks Job\u2019s Wickedness Is Great": "Elifaz vorbește: Răutatea lui Iov este mare",
    "Job Replies My Complaint Is Bitter": "Iov răspunde: Plângerea mea este amară",
    "Job Complains of Violence on the Earth": "Iov se plânge de violența de pe pământ",
    "Bildad Speaks How Can a Mortal Be Righteous Before God": "Bildad vorbește: Cum poate fi drept omul înaintea lui Dumnezeu",
    "Job Replies God\u2019s Majesty Is Unsearchable": "Iov răspunde: Maiestatea lui Dumnezeu este de nepătruns",
    "Job Maintains His Integrity": "Iov își păstrează integritatea",
    "Interlude Where Wisdom Is Found": "Interludiu: Unde se găsește înțelepciunea",
    "Job Finishes His Defense": "Iov își încheie apărarea",
    "Job Chapter 30": "Capitolul 30",
    "Job Chapter 31": "Capitolul 31",
    "Elihu Rebukes Job\u2019s Friends": "Elihu mustră prietenii lui Iov",
    "Elihu Rebukes Job": "Elihu îl mustră pe Iov",
    "Elihu Proclaims God\u2019s Justice": "Elihu proclamă dreptatea lui Dumnezeu",
    "Elihu Condemns Self-Righteousness": "Elihu condamnă încrederea în propria dreptate",
    "Elihu Exalts God\u2019s Goodness": "Elihu preamărește bunătatea lui Dumnezeu",
    "Elihu Proclaims God\u2019s Majesty": "Elihu proclamă maiestatea lui Dumnezeu",
    "Job Chapter 37": "Capitolul 37",
    "TheLordAnswers Job": "Domnul îi răspunde lui Iov",
    "Job Chapter 39": "Capitolul 39",
    "Job\u2019s Response to God": "Răspunsul lui Iov către Dumnezeu",
    "God\u2019s Challenge to Job": "Provocarea lui Dumnezeu către Iov",
    "Job Chapter 41": "Capitolul 41",
    "Job Is Humbled and Satisfied": "Iov este umilit și mulțumit",
    "Job\u2019s Friends Are Humiliated": "Prietenii lui Iov sunt umiliți",
    "Job\u2019s Fortunes Are Restored Twofold": "Bogățiile lui Iov sunt întoarse îndoit",
}

def translate_file(filepath, book_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = 0
    for p in data['pericopes']:
        en = p['title_en']
        if en in TRANS:
            p['title_ro'] = TRANS[en]
            count += 1
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    total = len(data['pericopes'])
    print(f"{book_name}: {count}/{total}")
    return count == total

# Apply translations
base = 'bible_books_pericopes'
results = []
results.append(translate_file(f'{base}/18_Iov_pericopes.json', 'Iov'))

print("Done!" if all(results) else "Incomplete")
