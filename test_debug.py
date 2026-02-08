#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Søkeverktøy - Enkel og robust versjon
"""

import sys
import os

print("=" * 60)
print("PDF SØKEVERKTØY - DEBUG VERSJON")
print("=" * 60)
print()

# Test 1: Python versjon
print("TEST 1: Sjekker Python-versjon...")
print(f"  Python versjon: {sys.version}")
print(f"  ✅ OK")
print()

# Test 2: Sjekk om PyMuPDF kan importeres
print("TEST 2: Sjekker PyMuPDF...")
try:
    import fitz
    print(f"  PyMuPDF versjon: {fitz.version}")
    print(f"  ✅ OK")
except ImportError as e:
    print(f"  ❌ FEIL: Kunne ikke importere PyMuPDF")
    print(f"  Feilmelding: {e}")
    print()
    print("  LØSNING: Kjør denne kommandoen:")
    print("  pip install PyMuPDF")
    print()
    input("Trykk Enter for å avslutte...")
    sys.exit(1)
print()

# Test 3: Sjekk nåværende mappe
print("TEST 3: Sjekker nåværende mappe...")
current_dir = os.getcwd()
print(f"  Mappe: {current_dir}")
print(f"  ✅ OK")
print()

# Test 4: Sjekk om nokkelord.txt finnes
print("TEST 4: Sjekker nokkelord.txt...")
if os.path.exists("nokkelord.txt"):
    print(f"  ✅ Funnet!")
    with open("nokkelord.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        print(f"  Nøkkelord: {', '.join(lines)}")
else:
    print(f"  ⚠️ Ikke funnet - oppretter eksempelfil...")
    with open("nokkelord.txt", "w", encoding="utf-8") as f:
        f.write("kontrakt\navtale\n")
    print(f"  ✅ Opprettet nokkelord.txt")
print()

# Test 5: Finn PDF-filer
print("TEST 5: Søker etter PDF-filer...")
pdf_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.pdf')]
print(f"  Antall PDF-filer funnet: {len(pdf_files)}")
if pdf_files:
    print(f"  Første 5 filer:")
    for i, f in enumerate(pdf_files[:5], 1):
        print(f"    {i}. {f}")
    print(f"  ✅ OK")
else:
    print(f"  ⚠️ INGEN PDF-FILER FUNNET!")
    print(f"  Legg PDF-filer i denne mappen: {current_dir}")
print()

print("=" * 60)
print("ALLE TESTER FULLFØRT!")
print("=" * 60)
print()
print("Hvis alle tester viser OK, kan du kjøre det fulle programmet.")
print()
input("Trykk Enter for å avslutte...")
