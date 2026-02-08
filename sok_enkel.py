#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Søkeverktøy - Forenklet versjon
"""

import fitz  # PyMuPDF
import os
import re
from datetime import datetime

print("=" * 70)
print("                  PDF SOKEVERKTOY v2.1")
print("=" * 70)
print()

# === INNSTILLINGER ===
NOKKELORD_FIL = "nokkelord.txt"
RAPPORT_FIL = "soke_rapport.html"
FILTER_TEKST = "Romerike og Glåmdal tingrett"  # Sett til None for å deaktivere

# === FUNKSJON: Last nøkkelord ===
def last_nokkelord():
    """Leser nøkkelord fra fil"""
    if not os.path.exists(NOKKELORD_FIL):
        print(f"Oppretter {NOKKELORD_FIL}...")
        with open(NOKKELORD_FIL, "w", encoding="utf-8") as f:
            f.write("# Skriv ett sokeord per linje\n")
            f.write("kontrakt\n")
            f.write("avtale\n")
        print(f"  OK! Rediger filen og kjor programmet igjen.\n")
        return ["kontrakt", "avtale"]
    
    with open(NOKKELORD_FIL, "r", encoding="utf-8") as f:
        ord = [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]
    
    return ord if ord else ["kontrakt"]

# === FUNKSJON: Finn setninger med ord ===
def finn_setninger(tekst, ord, filter_ut=None):
    """Finner setninger som inneholder et ord"""
    if not tekst or (filter_ut and filter_ut.lower() in tekst.lower()):
        return []
    
    # Søk med word boundaries
    pattern = re.compile(r'\b' + re.escape(ord) + r'\b', re.IGNORECASE)
    
    # Del tekst i setninger
    setninger = re.split(r'(?<=[.!?])\s+', tekst)
    
    funn = []
    for setning in setninger:
        if pattern.search(setning):
            setning = ' '.join(setning.split())  # Fjern ekstra mellomrom
            if len(setning) > 20:  # Ignorer veldig korte setninger
                funn.append(setning)
    
    return funn

# === FUNKSJON: Søk i én PDF ===
def sok_i_pdf(filnavn, nokkelord_liste, filter_ut):
    """Søker gjennom én PDF-fil"""
    resultat = {
        'fil': filnavn,
        'funn': {},
        'totalt': 0
    }
    
    try:
        doc = fitz.open(filnavn)
        
        for side_nr in range(len(doc)):
            tekst = doc[side_nr].get_text()
            
            for ord in nokkelord_liste:
                setninger = finn_setninger(tekst, ord, filter_ut)
                if setninger:
                    if ord not in resultat['funn']:
                        resultat['funn'][ord] = []
                    resultat['funn'][ord].extend(setninger)
                    resultat['totalt'] += len(setninger)
        
        doc.close()
    except Exception as e:
        print(f"  FEIL i {filnavn}: {e}")
    
    return resultat

# === FUNKSJON: Generer HTML-rapport ===
def lag_rapport(alle_resultater, nokkelord_liste):
    """Lager HTML-rapport"""
    totalt_filer = len([r for r in alle_resultater if r['totalt'] > 0])
    totalt_treff = sum(r['totalt'] for r in alle_resultater)
    
    html = f"""<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <title>Sokerapport - PDF</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .file-box {{
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .file-name {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .keyword-header {{
            background: #3498db;
            color: white;
            padding: 8px 15px;
            margin: 10px 0;
            border-radius: 5px;
            font-weight: bold;
        }}
        .sentence {{
            background: #ecf0f1;
            padding: 10px;
            margin: 5px 0;
            border-left: 4px solid #3498db;
            border-radius: 3px;
        }}
        .highlight {{
            background: yellow;
            padding: 2px 4px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PDF Sokerapport</h1>
        <p>Generert: {datetime.now().strftime('%d.%m.%Y kl. %H:%M')}</p>
    </div>
    
    <div class="stats">
        <h2>Oppsummering</h2>
        <p><strong>Filer med treff:</strong> {totalt_filer}</p>
        <p><strong>Totalt antall treff:</strong> {totalt_treff}</p>
        <p><strong>Sokte etter:</strong> {', '.join(nokkelord_liste)}</p>
    </div>
"""
    
    # Sorter etter antall treff
    alle_resultater.sort(key=lambda x: x['totalt'], reverse=True)
    
    for res in alle_resultater:
        if res['totalt'] == 0:
            continue
        
        html += f"""
    <div class="file-box">
        <div class="file-name">{res['fil']} ({res['totalt']} treff)</div>
"""
        
        for ord, setninger in res['funn'].items():
            html += f"""
        <div class="keyword-header">{ord} ({len(setninger)} treff)</div>
"""
            for setning in setninger:
                # Fremhev søkeordet
                pattern = re.compile(r'\b' + re.escape(ord) + r'\b', re.IGNORECASE)
                setning_med_highlight = pattern.sub(
                    lambda m: f'<span class="highlight">{m.group()}</span>',
                    setning
                )
                html += f'        <div class="sentence">{setning_med_highlight}</div>\n'
        
        html += "    </div>\n"
    
    html += """
</body>
</html>
"""
    return html

# === HOVEDPROGRAM ===
def main():
    # 1. Last nøkkelord
    print("Laster nokkelord...")
    nokkelord = last_nokkelord()
    print(f"  Soker etter: {', '.join(nokkelord)}")
    print()
    
    # 2. Finn PDF-filer
    print("Soker etter PDF-filer...")
    mappe = os.getcwd()
    pdf_filer = [f for f in os.listdir(mappe) if f.lower().endswith('.pdf')]
    
    if not pdf_filer:
        print("  INGEN PDF-FILER FUNNET!")
        print(f"  Legg PDF-filer i: {mappe}")
        print()
        input("Trykk Enter for aa avslutte...")
        return
    
    print(f"  Fant {len(pdf_filer)} PDF-filer")
    print()
    
    # 3. Søk gjennom PDF-filer
    print("Starter sok...")
    print("-" * 70)
    
    alle_resultater = []
    for i, pdf in enumerate(pdf_filer, 1):
        print(f"[{i}/{len(pdf_filer)}] {pdf}...", end=" ")
        resultat = sok_i_pdf(pdf, nokkelord, FILTER_TEKST)
        alle_resultater.append(resultat)
        
        if resultat['totalt'] > 0:
            print(f"OK ({resultat['totalt']} treff)")
        else:
            print("Ingen treff")
    
    print("-" * 70)
    print()
    
    # 4. Lag rapport
    print("Genererer rapport...")
    html = lag_rapport(alle_resultater, nokkelord)
    
    with open(RAPPORT_FIL, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"  Rapport lagret: {RAPPORT_FIL}")
    print()
    
    # 5. Vis oppsummering
    totalt_treff = sum(r['totalt'] for r in alle_resultater)
    filer_med_treff = len([r for r in alle_resultater if r['totalt'] > 0])
    
    print("=" * 70)
    print("FERDIG!")
    print("=" * 70)
    print(f"Filer med treff: {filer_med_treff}")
    print(f"Totalt treff: {totalt_treff}")
    print("=" * 70)
    print()
    
    return 0

# === KJØR PROGRAMMET ===
if __name__ == "__main__":
    try:
        exit_code = main()
        
        # Prøv å åpne rapporten
        if os.path.exists(RAPPORT_FIL):
            print("Apner rapporten...")
            import webbrowser
            webbrowser.open(RAPPORT_FIL)
        
        print()
        input("Trykk Enter for aa avslutte...")
        
    except Exception as e:
        print()
        print("=" * 70)
        print("FEIL OPPSTOD!")
        print("=" * 70)
        print(f"{e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        input("Trykk Enter for aa avslutte...")
