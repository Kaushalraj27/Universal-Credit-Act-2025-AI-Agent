# src/extract_sections.py
import argparse
import re
import json
import os
from src.utils import load_text, save_json, clean_text, ensure_dirs

try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False

OUTPUT_SECTIONS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "sections.json")
RAW_OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "sections_raw.txt")

SECTION_KEYWORDS = {
    "definitions": ["definition", "interpretation", "meaning of", "in this section"],
    "obligations": ["must", "is to", "shall", "exercise the power", "require"],
    "responsibilities": ["responsible", "responsibility", "Secretary of State", "Department"],
    "eligibility": ["entitled", "eligible", "entitlement", "eligibility", "claimant", "pre-2026 claimant"],
    "payments": ["allowance", "amount", "payments", "standard allowance", "LCWRA", "ESA"],
    "penalties": ["penalt", "offence", "sanction", "enforce"],
    "record_keeping": ["record", "report", "reporting", "record-keeping"],
}

PROMPT = """
Extract the following sections from this ACT:

- Definitions
- Obligations
- Responsibilities
- Eligibility
- Payments / Entitlements
- Penalties / Enforcement
- Record-Keeping / Reporting

Return JSON ONLY with keys:
definitions, obligations, responsibilities, eligibility, payments, penalties, record_keeping

TEXT:
{TEXT}
"""

def find_paragraphs(text):
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return paras

def heuristic_extract(text):
    text_clean = clean_text(text)
    paras = find_paragraphs(text_clean)
    lowered = [p.lower() for p in paras]
    result = {}
    for section, kws in SECTION_KEYWORDS.items():
        hits = []
        for i, p in enumerate(paras):
            low = lowered[i]
            for kw in kws:
                if kw in low:
                    hits.append(p)
                    break
        # fallback: find headings or nearby lines
        if not hits:
            for i, p in enumerate(paras):
                if re.search(r'\b' + re.escape(section.replace("_"," ")) + r'\b', p, re.I):
                    hits.append(paras[i])
        result[section] = "\n\n".join(hits) if hits else ""
    return result

def try_parse_json(content):
    try:
        return json.loads(content)
    except Exception:
        return None

def run_ollama(text):
    if not OLLAMA_AVAILABLE:
        return None, "ollama client not installed"
    try:
        resp = ollama.chat(model="llama3", messages=[{"role":"user","content":PROMPT.format(TEXT=text)}])
        content = resp.get("message", {}).get("content", "")
        return content, None
    except Exception as e:
        return None, str(e)

def main(text_path, out_path=OUTPUT_SECTIONS):
    ensure_dirs(os.path.dirname(out_path))
    text = load_text(text_path)
    text = clean_text(text)

    # 1) Try with Ollama and attempt to parse JSON
    content = None
    error = None
    if OLLAMA_AVAILABLE:
        content, error = run_ollama(text)

    if content:
        # save raw output for inspection
        with open(RAW_OUT, "w", encoding="utf8") as f:
            f.write(content)
    else:
        # if no model output, save a message
        with open(RAW_OUT, "w", encoding="utf8") as f:
            f.write(f"No model output. Error: {error}\n\nRunning heuristic extractor.\n")

    parsed = try_parse_json(content or "")
    if parsed and isinstance(parsed, dict):
        # ensure all keys exist
        final = {k: parsed.get(k, "") for k in SECTION_KEYWORDS.keys()}
        save_json(out_path, final)
        print(f"[+] Sections (from model JSON) saved to {out_path}")
        return out_path

    # 2) fallback heuristic extraction
    print("[!] Model output not valid JSON — falling back to heuristic extraction.")
    heuristic = heuristic_extract(text)
    # save heuristic result too
    save_json(out_path, heuristic)
    print(f"[+] Sections (heuristic) saved to {out_path}")
    return out_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "extracted_text.txt"))
    parser.add_argument("--out", type=str, default=OUTPUT_SECTIONS)
    args = parser.parse_args()
    main(args.text, args.out)
