import sys
import json
from collections import Counter

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open("data/processed/shlokas.json", encoding="utf-8") as f:
    shlokas = json.load(f)

print(f"=== SHLOKAS AUDIT: Total Records in shlokas.json = {len(shlokas)} ===")
for s in shlokas:
    print(f"ID: {s['id']}")
    print(f"  Shloka Display Number : {s['shloka_number_display']}")
    print(f"  Associated PDF Pages  : {s['associated_pages']}")
    print(f"  Topic                 : {s.get('english_title')}")
    print(f"  First Line Devanagari : {s['text'].splitlines()[0]}")
    print()

with open("data/processed/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"=== CHUNKS AUDIT: Total Chunks in chunks.json = {len(chunks)} ===")
type_counts = Counter(c['metadata'].get('content_type') for c in chunks)
category_counts = Counter(c['metadata'].get('category') for c in chunks)
print(f"Content Type Breakdown : {dict(type_counts)}")
print(f"Category Breakdown     : {dict(category_counts)}")

print("\nDetailed Chunk to Source Mapping:")
for i, c in enumerate(chunks, 1):
    m = c['metadata']
    src = m.get('source')
    shloka_num = m.get('shloka_number')
    ctype = m.get('content_type')
    cat = m.get('category')
    page = m.get('page_number')
    print(f"[{i:02d}] ID: {c['id']:<40} | Type: {ctype:<11} | Cat: {cat:<12} | Shloka: {str(shloka_num):<4} | Page: {str(page):<3} | Source: {src}")
