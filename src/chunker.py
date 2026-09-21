"""
Chunker Module for Sanskrit Shloka Analysis RAG System.
Performs intelligent shloka-boundary-aware chunking preserving grammatical
and commentary relationships instead of arbitrary character-count splitting.
Produces data/processed/shlokas.json and data/processed/chunks.json.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from src.config import PROCESSED_DATA_DIR
from src.schemas import ShlokaData, ChunkData, ChunkMetadata
from src.data_loader import get_curated_chapter1_shlokas, get_curated_methodology_chunks

def create_chunks_from_shloka(shloka: Dict[str, Any]) -> List[ChunkData]:
    """
    Generate multiple specialized, semantically coherent chunks for a single shloka:
    1. Primary Sanskrit verse chunk
    2. Grammatical analysis chunk (Padavibhaga, Anvaya, Sandhi, Samasa)
    3. Lexical/Morphological chunk (Dhatu, Kridanta, Shabdaroopa)
    4. Interpretive/Commentary chunk (Shlokartha, Bhavartha)
    """
    chunks = []
    shloka_id = shloka["id"]
    shloka_num = shloka["shloka_number"]
    source = shloka.get("source", "Sushruta Samhita")
    sthana = shloka.get("sthana", "Nidana Sthana")
    chapter = shloka.get("chapter", "Vatavyadhi Nidana")
    pages = shloka.get("associated_pages", [])
    primary_page = pages[0] if pages else 1

    # 1. Primary Shloka Text Chunk
    primary_text = (
        f"Source: {source}, {sthana}, Chapter 1: {chapter} (श्लोक {shloka['shloka_number_display']})\n"
        f"Sanskrit Verse:\n{shloka['text']}\n"
        f"Transliteration: {shloka.get('transliteration', '')}\n"
        f"Subject: {shloka.get('english_title', '')}"
    )
    chunks.append(ChunkData(
        id=f"{shloka_id}_verse",
        text=primary_text,
        metadata={
            "source": source,
            "sthana": sthana,
            "chapter": chapter,
            "shloka_number": shloka_num,
            "shloka_id": shloka_id,
            "content_type": "shloka",
            "category": "verse",
            "language": "Sanskrit",
            "page_number": primary_page
        }
    ))

    # 2. Syntactic & Padavibhaga Chunk
    syntax_text = (
        f"Sushruta Samhita, Vatavyadhi Nidana (श्लोक {shloka['shloka_number_display']}) - पदविभागः एवं अन्वयः:\n"
        f"Padavibhaga: {shloka.get('padavibhaga', '')}\n"
        f"Anvaya (अन्वयवाक्यम्): {shloka.get('anvaya', '')}"
    )
    chunks.append(ChunkData(
        id=f"{shloka_id}_syntax",
        text=syntax_text,
        metadata={
            "source": source,
            "sthana": sthana,
            "chapter": chapter,
            "shloka_number": shloka_num,
            "shloka_id": shloka_id,
            "content_type": "grammar",
            "category": "syntax",
            "language": "Sanskrit",
            "page_number": primary_page
        }
    ))

    # 3. Morphology & Word Formation Chunk (Sandhi, Samasa, Dhatu)
    grammar = shloka.get("grammar_details", {})
    grammar_lines = [f"Grammar and Word Formations for Shloka {shloka['shloka_number_display']}:"]
    
    if "sandhi" in grammar and grammar["sandhi"]:
        grammar_lines.append("सन्धि-विच्छेदः:")
        for s in grammar["sandhi"]:
            grammar_lines.append(f"- {s.get('pada')}: {s.get('split')} ({s.get('type')}) - {s.get('rule')}")

    if "samasa" in grammar and grammar["samasa"]:
        grammar_lines.append("समास-विग्रहः:")
        for sm in grammar["samasa"]:
            grammar_lines.append(f"- {sm.get('pada')}: विग्रह: {sm.get('vigraha')} | प्रकार: {sm.get('type')} | अर्थ: {sm.get('meaning')}")

    if "dhaturoopa" in grammar and grammar["dhaturoopa"]:
        grammar_lines.append("धातुरूपाणि (Verbal Roots):")
        for d in grammar["dhaturoopa"]:
            grammar_lines.append(f"- क्रियापद: {d.get('kriyapada')} | धातु: {d.get('dhatu')} ({d.get('gana')}) | अर्थ: {d.get('meaning')} | {d.get('lakara')}, {d.get('purusha')}, {d.get('vachana')}")

    if "kridanta" in grammar and grammar["kridanta"]:
        grammar_lines.append("कृदन्ताः / तद्धिताः:")
        for k in grammar["kridanta"]:
            grammar_lines.append(f"- {k.get('pada')}: प्रकृति: {k.get('prakriti')} + प्रत्यय: {k.get('pratyaya')} ({k.get('type')}) - {k.get('meaning')}")

    if len(grammar_lines) > 1:
        chunks.append(ChunkData(
            id=f"{shloka_id}_morphology",
            text="\n".join(grammar_lines),
            metadata={
                "source": source,
                "sthana": sthana,
                "chapter": chapter,
                "shloka_number": shloka_num,
                "shloka_id": shloka_id,
                "content_type": "grammar",
                "category": "morphology",
                "language": "Sanskrit+English",
                "page_number": pages[1] if len(pages) > 1 else primary_page
            }
        ))

    # 4. Commentary & Bhavartha Chunk
    commentary_text = (
        f"Sushruta Samhita, Vatavyadhi Nidana (श्लोक {shloka['shloka_number_display']}) - अर्थः एवं भावार्थः:\n"
        f"Shlokartha (Literal meaning): {shloka.get('shlokartha', '')}\n"
        f"Bhavartha (Intended Purport): {shloka.get('bhavartha', '')}"
    )
    chunks.append(ChunkData(
        id=f"{shloka_id}_commentary",
        text=commentary_text,
        metadata={
            "source": source,
            "sthana": sthana,
            "chapter": chapter,
            "shloka_number": shloka_num,
            "shloka_id": shloka_id,
            "content_type": "commentary",
            "category": "bhavartha",
            "language": "Sanskrit+Hindi+English",
            "page_number": primary_page
        }
    ))

    return chunks


def build_and_save_processed_data() -> Tuple[List[ShlokaData], List[ChunkData]]:
    """
    Main data preparation pipeline:
    1. Loads raw source material
    2. Generates ShlokaData and ChunkData
    3. Saves data/processed/shlokas.json and data/processed/chunks.json
    """
    raw_shlokas = get_curated_chapter1_shlokas()
    methodology_chunks = get_curated_methodology_chunks()

    shlokas_models: List[ShlokaData] = []
    all_chunks: List[ChunkData] = []

    for s in raw_shlokas:
        shloka_obj = ShlokaData(
            id=s["id"],
            source=s.get("source", "Sushruta Samhita"),
            sthana=s.get("sthana", "Nidana Sthana"),
            chapter=s.get("chapter", "Vatavyadhi Nidana"),
            chapter_number=s.get("chapter_number", 1),
            shloka_number=s["shloka_number"],
            shloka_number_display=s.get("shloka_number_display", str(s["shloka_number"])),
            text=s["text"],
            transliteration=s.get("transliteration"),
            english_title=s.get("english_title"),
            associated_pages=s.get("associated_pages", [])
        )
        shlokas_models.append(shloka_obj)

        # Generate contextual chunks
        shloka_chunks = create_chunks_from_shloka(s)
        all_chunks.extend(shloka_chunks)

    # Add methodology chunks from Ayurvidya
    for m in methodology_chunks:
        all_chunks.append(ChunkData(
            id=m["id"],
            text=f"Ayurvidya Methodology: {m['title']}\n{m['text']}",
            metadata={
                "source": m.get("metadata", {}).get("source", "steps of Ayurvidya.pdf"),
                "sthana": "Methodology",
                "chapter": "Prabhashanam",
                "shloka_number": 0,
                "shloka_id": "methodology",
                "content_type": m["content_type"],
                "category": m["category"],
                "language": "Sanskrit+English",
                "page_number": 1
            }
        ))

    # Save shlokas.json
    shlokas_path = PROCESSED_DATA_DIR / "shlokas.json"
    with open(shlokas_path, "w", encoding="utf-8") as f:
        json.dump([s.model_dump() for s in shlokas_models], f, ensure_ascii=False, indent=2)

    # Save chunks.json
    chunks_path = PROCESSED_DATA_DIR / "chunks.json"
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump([c.model_dump() for c in all_chunks], f, ensure_ascii=False, indent=2)

    return shlokas_models, all_chunks

if __name__ == "__main__":
    shlokas, chunks = build_and_save_processed_data()
    print(f"Processed {len(shlokas)} shlokas into {len(chunks)} chunks.")
