#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix pericope title translations by reading actual JSON content
"""

import json
import os
import sys
import codecs

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

base_path = r"bible_books_pericopes"
files = [
    "01_Facerea_pericopes.json",
    "02_Ieșirea_pericopes.json",
    "03_Leviticul_pericopes.json",
    "04_Numerii_pericopes.json",
    "05_Deuteronomul_pericopes.json"
]

# Mapping from straight apostrophe versions to Romanian
TRANSLATIONS_BASE = {
    "Adam's Descendants to Noah and His Sons": "Urmașii lui Adam până la Noe și fiii săi",
    "God's Promise to Noah": "Făgăduința lui Dumnezeu către Noe",
    "Lot's Captivity and Rescue": "Captivitatea și eliberarea lui Lot",
    "God's Covenant with Abram": "Legământul lui Dumnezeu cu Avram",
    "Sarah's Death and Burial": "Moartea și înmormântarea Sarei",
    "Ishmael's Descendants": "Urmașii lui Ismael",
    "Esau's Hittite Wives": "Soțiile hetite ale lui Esau",
    "Esau's Lost Blessing": "Binecuvântarea pierdută a lui Esau",
    "Esau Marries Ishmael's Daughter": "Esau se căsătorește cu fiica lui Ismael",
    "Jacob's Dream at Bethel": "Visul lui Iacov la Betel",
    "Jacob Marries Laban's Daughters": "Iacov se căsătorește cu fiicele lui Laban",
    "Jacob Prospers at Laban's Expense": "Iacov prosperă pe seama lui Laban",
    "Jacob Escapes Esau's Fury": "Iacov scapă de furia lui Esau",
    "Dinah's Brothers Avenge Their Sister": "Frații Dinei își răzbună sora",
    "Esau's Descendants": "Urmașii lui Esau",
    "Joseph and Potiphar's Wife": "Iosif și soția lui Potifar",
    "Joseph Interprets Pharaoh's Dream": "Iosif tâlcuiește visul Faraonului",
    "Joseph's Rise to Power": "Înălțarea lui Iosif la putere",
    "Joseph's Brothers Go to Egypt": "Frații lui Iosif merg în Egipt",
    "Joseph's Brothers Return to Canaan": "Frații lui Iosif se întorc în Canaan",
    "Judah Pleads for Benjamin's Release": "Iuda pledează pentru eliberarea lui Beniamin",
    "Jacob Blesses Joseph's Sons": "Iacov îi binecuvântează pe fiii lui Iosif",
    "Jacob's Last Words to His Sons": "Ultimele cuvinte ale lui Iacov către fiii săi",
    "Jacob's Death and Burial": "Moartea și înmormântarea lui Iacov",
    "Joseph's Last Days and Death": "Ultimele zile și moartea lui Iosif",
    "Moses' Miraculous Power": "Puterea minunată a lui Moise",
    "Israel's Deliverance Assured": "Izbăvirea lui Israel asigurată",
    "Moses and Aaron Obey God's Commands": "Moise și Aaron ascultă poruncile lui Dumnezeu",
    "Aaron's Miraculous Rod": "Toiagul minunat al lui Aaron",
    "Jethro's Advice": "Sfatul lui Ietro",
    "Moses' Intercession": "Mijlocirea lui Moise",
    "Aaron's Priesthood Inaugurated": "Preoția lui Aaron inaugurată",
    "Census of the Levites": "Recensământarea leviților",
    "The Budding of Aaron's Rod": "Înflorirea toiagului lui Aaron",
    "The Priests' Portion": "Partea preoților",
    "Balaam's First Oracle": "Primul oracle al lui Balaam",
    "Balaam's Second Oracle": "Al doilea oracle al lui Balaam",
    "Balaam's Third Oracle": "Al treilea oracle al lui Balaam",
    "Balaam's Fourth Oracle": "Al patrulea oracle al lui Balaam",
    "Joshua Appointed Moses' Successor": "Iosua numit urmașul lui Moise",
    "The Stages of Israel's Journey from Egypt": "Etapele călătoriei lui Israel din Egipt",
    "Israel's Refusal to Enter the Land": "Refuzul lui Israel de a intra în țară",
    "The Penalty for Israel's Rebellion": "Pedeapsa pentru răzvrătirea lui Israel",
    "Moses the Mediator of God's Will": "Moise mijlocitorul voii lui Dumnezeu",
    "God's Fidelity Assured": "Credincioșia lui Dumnezeu asigurată",
    "Joshua Becomes Moses' Successor": "Iosua devine urmașul lui Moise",
    "Moses and Joshua Receive God's Charge": "Moise și Iosua primesc însărcinarea lui Dumnezeu",
    "Moses' Death Foretold": "Moartea lui Moise prevestită",
    "Moses' Final Blessing on Israel": "Binecuvântarea finală a lui Moise pentru Israel",
}

def main():
    total_fixed = 0

    for filename in files:
        file_path = os.path.join(base_path, filename)
        print(f"\nProcessing: {filename}")

        # Read JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        fixed_count = 0
        for pericope in data['pericopes']:
            title_en = pericope['title_en']

            # If not yet translated (title_ro == title_en)
            if title_en == pericope['title_ro']:
                # Try to find translation by normalizing apostrophes
                normalized = title_en.replace('\u2019', "'")  # Replace curly with straight

                if normalized in TRANSLATIONS_BASE:
                    pericope['title_ro'] = TRANSLATIONS_BASE[normalized]
                    fixed_count += 1

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"  Fixed: {fixed_count} titles")
        total_fixed += fixed_count

    print(f"\n{'='*60}")
    print(f"Total fixed: {total_fixed}")

if __name__ == "__main__":
    main()
