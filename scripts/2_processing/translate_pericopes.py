#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translate Bible pericope titles from English to Romanian
for Orthodox Bible pericope files
"""

import json
import sys
import os

# Comprehensive translation dictionary for Bible pericope titles
# Using Orthodox Romanian Bible terminology
TRANSLATIONS = {
    # General terms and phrases
    "The": "Învățătura despre",  # context-dependent, will be handled specially
    "of": "lui",
    "the": "",

    # Key theological terms
    "Proclamation": "Propovăduirea",
    "Baptism": "Botezul",
    "Temptation": "Ispitirea",
    "Testimony": "Mărturia",
    "Dedication": "Dedicația",
    "Birth": "Nașterea",
    "Foretold": "Vestită",
    "Promise": "Făgăduința",
    "Ascension": "Înălțarea",
    "Chosen": "Ales",
    "Replace": "a-l înlocui pe",
    "Word": "Cuvântul",
    "Became": "S-a făcut",
    "Flesh": "Trup",
    "Lamb": "Mielul",
    "God": "Dumnezeu",

    # People
    "John the Baptist": "Ioan Botezătorul",
    "Jesus": "Isus",
    "Theophilus": "Teofil",
    "Judas": "Iuda",
    "Matthias": "Matia",
    "Holy Spirit": "Duhul Sfânt",

    # Specific title translations - complete phrases
    "The Proclamation of John the Baptist": "Propovăduirea lui Ioan Botezătorul",
    "The Baptism of Jesus": "Botezul lui Isus",
    "The Temptation of Jesus": "Ispitirea lui Isus",
    "The Testimony of John the Baptist": "Mărturia lui Ioan Botezătorul",
    "Dedication to Theophilus": "Dedicația către Teofil",
    "The Birth of John the Baptist Foretold": "Vestirea nașterii lui Ioan Botezătorul",
    "The Birth of Jesus Foretold": "Vestirea nașterii lui Isus",
    "The Word Became Flesh": "Cuvântul S-a făcut Trup",
    "The Lamb of God": "Mielul lui Dumnezeu",
    "The Promise of the Holy Spirit": "Făgăduința Duhului Sfânt",
    "The Ascension of Jesus": "Înălțarea lui Isus",
    "Matthias Chosen to Replace Judas": "Alegerea lui Matia în locul lui Iuda",

    # Additional common Bible terms
    "Calling": "Chemarea",
    "First": "Primii",
    "Disciples": "Ucenici",
    "Man": "Om",
    "Unclean": "Necurat",
    "Spirit": "Duh",
    "Healing": "Vindecarea",
    "Leper": "Lepros",
    "Paralytic": "Slăbănog",
    "Calling of": "Chemarea lui",
    "Mother-in-Law": "Soacră",
    "Peter": "Petru",
    "Fever": "Friguri",
    "Many": "Mulți",
    "Sick": "Bolnavi",
    "Preach": "Propovăduire",
    "Throughout": "În toată",
    "Galilee": "Galileea",
    "Cleansing": "Curățirea",
    "Forgiveness": "Iertarea",
    "Sins": "Păcate",
    "Tax Collector": "Vameș",
    "Matthew": "Matei",
    "Levi": "Levi",
    "Question": "Întrebarea",
    "Fasting": "Postul",
    "About": "Despre",
    "Lord": "Domnul",
    "Sabbath": "Sabat",
    "Withered": "Uscată",
    "Hand": "Mână",
    "Choosing": "Alegerea",
    "Twelve": "Celor doisprezece",
    "Apostles": "Apostoli",
    "Sermon": "Predica",
    "Mount": "de pe Munte",
    "Plain": "de la Câmpie",
    "Crowds": "Mulțimi",
    "Follow": "Urmează",
    "Teaching": "Învățătura",
    "Authority": "Autoritate",
    "Centurion": "Sutaș",
    "Servant": "Slujitor",
    "Slave": "Rob",
    "Widow": "Văduvă",
    "Son": "Fiu",
    "Nain": "Nain",
    "Ministry": "Slujirea",
    "Pharisee": "Fariseu",
    "House": "Casa",
    "Simon": "Simon",
    "Sinful": "Păcătoasă",
    "Woman": "Femeie",
    "Women": "Femei",
    "Parable": "Pilda",
    "Sower": "Semănătorului",
    "Purpose": "Scopul",
    "Parables": "Pildelor",
    "Explained": "Tâlcuită",
    "Lamp": "Lumină",
    "Stand": "Sfeșnic",
    "Calming": "Liniștirea",
    "Storm": "Furtunii",
    "Demon-Possessed": "Îndrăcit",
    "Gerasene": "Gadarenilor",
    "Dead": "Moartă",
    "Girl": "Fată",
    "Jairus": "Iair",
    "Daughter": "Fiica",
    "Subject": "Supusă",
    "Bleeding": "Scurgere de sânge",
    "Sending": "Trimiterea",
    "Out": "în lume",
    "Two": "a doi",
    "by": "câte",
    "Death": "Moartea",
    "Beheading": "Tăierea capului",
    "Feeding": "Înmulțirea",
    "Five Thousand": "celor cinci mii",
    "Four Thousand": "celor patru mii",
    "Walking": "Mersul",
    "Water": "pe apă",
    "Sea": "Mare",
    "Clean": "Curat",
    "Unclean": "Necurat",
    "Faith": "Credința",
    "Canaanite": "Canaaneancă",
    "Syrophoenician": "Sirofeniciana",
    "Deaf": "Surd",
    "Mute": "Mut",
    "Yeast": "Dospeala",
    "Leaven": "Aluatul",
    "Pharisees": "Fariseilor",
    "Sadducees": "Saducheilor",
    "Confession": "Mărturisirea",
    "Christ": "Hristos",
    "Messiah": "Mesia",
    "Predicts": "Vestește",
    "Foretells": "Vestește",
    "Resurrection": "Învierea",
    "Transfiguration": "Schimbarea la Față",
    "Boy": "Băiat",
    "Epileptic": "Lunatic",
    "Greatest": "Cel mai mare",
    "Kingdom": "Împărăția",
    "Heaven": "Cerurilor",
    "Temple": "Templu",
    "Tax": "Bir",
    "Lost": "Pierdută",
    "Sheep": "Oaie",
    "Brother": "Frate",
    "Against": "Împotriva",
    "You": "ta",
    "Parable of": "Pilda",
    "Unmerciful": "Nemilostiv",
    "Servant": "Slujitor",
    "Divorce": "Divorț",
    "Little": "Copii",
    "Children": "Copii",
    "Rich": "Bogat",
    "Young": "Tânăr",
    "Man": "Om",
    "Ruler": "Dregător",
    "Eternal": "Veșnică",
    "Life": "Viață",
    "Workers": "Lucrători",
    "Vineyard": "Vie",
    "Request": "Cererea",
    "James": "Iacov",
    "John": "Ioan",
    "Mother": "Mama",
    "Sons": "Fiii",
    "Zebedee": "lui Zebedei",
    "Blind": "Orb",
    "Bartimaeus": "Bartimeu",
    "Beggars": "Cerșetori",
    "Jericho": "Ierihon",
    "Triumphal": "Triumfală",
    "Entry": "Intrare",
    "Jerusalem": "Ierusalim",
    "Cleansing of": "Curățirea",
    "Fig": "Smochin",
    "Tree": "Pom",
    "Cursed": "Blestemat",
    "Withered": "Uscat",
    "Chief": "Marii",
    "Priests": "Preoți",
    "Elders": "Bătrâni",
    "Tenants": "Viticultori",
    "Marriage": "Nunta",
    "Banquet": "Ospăț",
    "Wedding": "Nuntă",
    "Paying": "Plata",
    "Imperial": "Împărătesc",
    "Taxes": "Biruri",
    "Caesar": "Cezarului",
    "Sadducees": "Saducheii",
    "Ask": "Întreabă",
    "Seven": "Șapte",
    "Brothers": "Frați",
    "Greatest Commandment": "Cea mai mare poruncă",
    "David": "David",
    "Call": "numește",
    "Denouncing": "Mustrarea",
    "Teachers": "Cărturari",
    "Law": "Lege",
    "Widow's": "Văduvei",
    "Offering": "Darul",
    "Mite": "Lepton",
    "Signs": "Semnele",
    "End": "Sfârșitului",
    "Times": "Timpurilor",
    "Age": "Veacului",
    "Coming": "Venirea",
    "Day": "Ziua",
    "Hour": "Ceasul",
    "Unknown": "Necunoscută",
    "Virgins": "Fecioare",
    "Talents": "Talanți",
    "Anointing": "Ungerea",
    "Bethany": "Betania",
    "Plot": "Uneltirea",
    "Kill": "a-L ucide pe",
    "Last": "Cina",
    "Supper": "cea de Taină",
    "Instituting": "Instituirea",
    "Lord's": "Cinei",
    "Gethsemane": "Ghetsimani",
    "Arrest": "Arestarea",
    "Before": "Înaintea",
    "Sanhedrin": "Sinedriului",
    "High": "Mare",
    "Priest": "Preot",
    "Caiaphas": "Caiafa",
    "Annas": "Ana",
    "Denial": "Tăgăduirea",
    "Pilate": "Pilat",
    "Judas": "Iuda",
    "Hangs": "Se spânzură",
    "Himself": "",
    "Soldiers": "Ostașii",
    "Mock": "Batjocoresc",
    "Crucifixion": "Răstignirea",
    "Crucified": "Răstignit",
    "Two": "Doi",
    "Rebels": "Tâlhari",
    "Robbers": "Tâlhari",
    "Thieves": "Tâlhari",
    "Burial": "Îngroparea",
    "Guard": "Paza",
    "Tomb": "Mormânt",
    "Empty": "Gol",
    "Risen": "Înviat",
    "Great": "Marea",
    "Commission": "Trimitere",
    "Appearing": "Arătarea",
    "Mary": "Maria",
    "Magdalene": "Magdalena",
    "Road": "Drumul",
    "Emmaus": "Emaus",
    "Appears": "Se arată",
    "Appearance": "Arătarea",
    "Thomas": "Toma",
    "Miraculous": "Minunată",
    "Catch": "Pescuire",
    "Fish": "Pești",
    "Restore": "Restabilirea",
    "Peter": "Petru",
    "Outpouring": "Revărsarea",
    "Pentecost": "Rusalii",
    "Preaches": "Propovăduiește",
    "Believers": "Credincioși",
    "Fellowship": "Împărtășire",
    "Breaking": "Frângerea",
    "Bread": "Pâinii",
    "Gate": "Poartă",
    "Called": "numită",
    "Beautiful": "Frumoasă",
    "Lame": "Olog",
    "Beggar": "Cerșetor",
    "Healed": "Vindecat",
    "Addresses": "Se adresează",
    "Crowd": "Mulțimii",
    "Arrested": "Arestați",
    "Speak": "Vorbesc",
    "Prayer": "Rugăciunea",
    "Boldness": "Îndrăzneală",
    "Ananias": "Anania",
    "Sapphira": "Safira",
    "Miraculous Signs": "Semne și minuni",
    "Wonders": "Minuni",
    "Opposition": "Împotrivire",
    "Angel": "Îngerul",
    "Opens": "Deschide",
    "Doors": "Ușile",
    "Prison": "Temniță",
    "Gamaliel": "Gamaliel",
    "Advice": "Sfatul",
    "Choosing of": "Alegerea",
    "Deacons": "Diaconi",
    "Stephen": "Ștefan",
    "Seized": "Prins",
    "Speech": "Cuvântarea",
    "Stoning": "Uciderea cu pietre",
    "Martyrdom": "Martiriul",
    "Persecution": "Prigonirea",
    "Church": "Biserică",
    "Scattered": "Împrăștiată",
    "Philip": "Filip",
    "Samaria": "Samaria",
    "Ethiopian": "Etiopian",
    "Eunuch": "Famen",
    "Conversion": "Convertirea",
    "Saul": "Saul",
    "Paul": "Pavel",
    "Damascus": "Damasc",
    "Escapes": "Scapă",
    "Aeneas": "Enea",
    "Tabitha": "Tabita",
    "Dorcas": "Dorca",
    "Raised": "Înviată",
    "Cornelius": "Corneliu",
    "Calls": "Cheamă",
    "Vision": "Vedenia",
    "Gentiles": "Neamuri",
    "Receive": "Primesc",
    "Explains": "Explică",
    "Actions": "Faptele",
    "Antioch": "Antiohia",
    "Barnabas": "Barnaba",
    "Sent": "Trimis",
    "Agabus": "Agab",
    "Predicts": "Prezice",
    "Famine": "Foamete",
    "Miraculous Escape": "Scăparea minunată",
    "Herod": "Irod",
    "Struck": "Lovit",
    "Down": "",
    "Mission": "Misiunea",
    "Cyprus": "Cipru",
    "Sergius": "Sergiu",
    "Paulus": "Paul",
    "Elymas": "Elima",
    "Sorcerer": "Vrăjitor",
    "Pisidian": "Pisidiei",
    "Synagogue": "Sinagogă",
    "Iconium": "Iconia",
    "Lystra": "Listra",
    "Derbe": "Derbe",
    "Return": "Întoarcerea",
    "Council": "Sinodul",
    "Disagreement": "Neînțelegerea",
    "Between": "dintre",
    "Sharp": "Ascuțită",
    "Contention": "Dispută",
    "Mark": "Marcu",
    "Timothy": "Timotei",
    "Joins": "Se alătură",
    "Macedonian": "Macedoneanului",
    "Troas": "Troa",
    "Lydia": "Lidia",
    "Philippi": "Filipi",
    "Fortune-Teller": "Ghicitoare",
    "Slave Girl": "Roabă",
    "Beaten": "Bătut",
    "Imprisoned": "Închis",
    "Earthquake": "Cutremur",
    "Jailer": "Temnicer",
    "Converted": "Convertit",
    "Berea": "Bereea",
    "Athens": "Atena",
    "Areopagus": "Areopag",
    "Corinth": "Corint",
    "Aquila": "Acuila",
    "Priscilla": "Priscila",
    "Ephesus": "Efes",
    "Apollos": "Apolo",
    "Riot": "Răscoala",
    "Demetrius": "Dimitrie",
    "Silversmiths": "Argintari",
    "Eutychus": "Eutih",
    "Falls": "Cade",
    "Window": "Fereastră",
    "Farewell": "Rămas bun",
    "Elders": "Prezbiteri",
    "Way": "Drum",
    "Warnings": "Avertismente",
    "Caesarea": "Cezareea",
    "Arrival": "Sosirea",
    "Seized": "Prins",
    "Arrested": "Arestat",
    "Speaks": "Vorbește",
    "Defense": "Apărare",
    "Felix": "Felix",
    "Festus": "Fest",
    "Agrippa": "Agripa",
    "Appeals": "Face apel",
    "Rome": "Roma",
    "Voyage": "Călătoria",
    "Storm": "Furtună",
    "Shipwreck": "Naufragiu",
    "Shipwrecked": "Naufragiat",
    "Malta": "Malta",
    "Arrival in": "Sosirea la",
    "House": "Casă",
    "Arrest": "Arest",
    "Boldly": "Cu îndrăzneală",
    "Proclaims": "Propovăduiește",
}

def translate_title(title_en):
    """
    Translate an English pericope title to Romanian
    Uses direct lookup first, then falls back to word-by-word translation
    """
    # Direct lookup for exact matches
    if title_en in TRANSLATIONS:
        return TRANSLATIONS[title_en]

    # If no direct match, return the original (will be manually reviewed)
    # This is safer than attempting automatic word-by-word translation
    # which could produce incorrect results
    return title_en

def translate_pericope_file(filepath):
    """
    Translate pericope titles in a JSON file
    Only updates titles that are currently in English (not already translated)
    """
    print(f"\nProcessing: {filepath}")

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Count translations
    total = len(data['pericopes'])
    updated = 0
    already_translated = 0

    # Update pericopes
    for pericope in data['pericopes']:
        title_en = pericope['title_en']
        title_ro = pericope.get('title_ro', '')

        # Check if already translated (not just copy of English)
        if title_ro and title_ro != title_en:
            already_translated += 1
            continue

        # Translate
        new_title_ro = translate_title(title_en)

        if new_title_ro != title_en:
            pericope['title_ro'] = new_title_ro
            updated += 1
            print(f"  ✓ {pericope['pericope_id']}")
            print(f"    EN: {title_en}")
            print(f"    RO: {new_title_ro}")

    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSummary for {data['name_ro']}:")
    print(f"  Total pericopes: {total}")
    print(f"  Already translated: {already_translated}")
    print(f"  Newly translated: {updated}")
    print(f"  Remaining untranslated: {total - already_translated - updated}")

    return {
        'book': data['name_ro'],
        'total': total,
        'already_translated': already_translated,
        'updated': updated,
        'remaining': total - already_translated - updated
    }

def main():
    base_path = 'C:/Users/User/Documents/GitHub/orthodox_bible/bible_books_pericopes'

    files = [
        f'{base_path}/52_Matei_pericopes.json',
        f'{base_path}/53_Marcu_pericopes.json',
        f'{base_path}/54_Luca_pericopes.json',
        f'{base_path}/55_Ioan_pericopes.json',
        f'{base_path}/56_Faptele Apostolilor_pericopes.json'
    ]

    print("=" * 70)
    print("Bible Pericope Title Translation - English to Romanian")
    print("=" * 70)

    results = []
    for filepath in files:
        if os.path.exists(filepath):
            result = translate_pericope_file(filepath)
            results.append(result)
        else:
            print(f"\nERROR: File not found: {filepath}")

    # Overall summary
    print("\n" + "=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)
    for r in results:
        print(f"{r['book']:20} | Total: {r['total']:3} | Already: {r['already_translated']:3} | New: {r['updated']:3} | Remaining: {r['remaining']:3}")

    print("\nTranslation complete!")

if __name__ == '__main__':
    main()
