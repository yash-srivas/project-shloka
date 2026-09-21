import sys
import pypdf
import re

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

reader = pypdf.PdfReader("data/raw/CHAPTER 1- VATAVYADHI NIDANA.pdf")
print(f"Total pages in 'CHAPTER 1- VATAVYADHI NIDANA.pdf': {len(reader.pages)}")

# Track pages where shlokas and sections appear
shloka_mentions = []

for i, page in enumerate(reader.pages):
    page_num = i + 1
    text = page.extract_text() or ""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    # Search for shloka numbers like ||१|| or ||1|| or |१| or similar
    shloka_markers = re.findall(r'[\|।॥]{1,2}\s*[०१२३४५६७८९0-9\s]+\s*[\|।॥]{1,2}', text)
    
    # Check for header/section markers
    has_padavibhaga = "Padavibhaga" in text or "पदविभाग" in text
    has_anvaya = "Anvaya" in text or "अन्वय" in text
    has_shlokartha = "Shlokartha" in text or "श्लोकार्थ" in text
    has_bhavartha = "Bhavartha" in text or "भावार्थ" in text
    
    print(f"--- PAGE {page_num} ---")
    if lines:
        print(f"Top lines: {lines[:2]}")
    if shloka_markers:
        print(f"Markers found: {shloka_markers}")
    print(f"Sections present: Padavibhaga={has_padavibhaga}, Anvaya={has_anvaya}, Shlokartha={has_shlokartha}, Bhavartha={has_bhavartha}")
