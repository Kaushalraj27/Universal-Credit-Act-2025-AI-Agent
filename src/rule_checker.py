# src/rule_checker.py
import argparse
import json
import os
import re
from src.utils import load_json, save_json, ensure_dirs

# try to import ollama client; if missing, we'll use pure-python heuristics
try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False

BASE = os.path.dirname(os.path.dirname(__file__))
OUTPUT_RULES = os.path.join(BASE, "output", "rule_checks.json")
RAW_DIR = os.path.join(BASE, "output", "rule_raw")
ensure_dirs = ensure_dirs  # rebind for clarity
ensure_dirs(os.path.dirname(OUTPUT_RULES))
ensure_dirs(RAW_DIR)

RULES = [
    ("Act must define key terms", "definitions"),
    ("Act must specify eligibility criteria", "eligibility"),
    ("Act must specify responsibilities of the administering authority", "responsibilities"),
    ("Act must include enforcement or penalties", "penalties"),
    ("Act must include payment calculation or entitlement structure", "payments"),
    ("Act must include record-keeping or reporting requirements", "record_keeping"),
]

RULE_PROMPT = """
You are a precise legal assistant.

Check whether the following SECTION TEXT satisfies the RULE:
RULE: "{RULE}"

SECTION TEXT:
{SECTION}

Answer with a JSON object exactly in this format (nothing else):
{{
  "rule": "{RULE}",
  "status": "pass" or "fail",
  "evidence": "<one-line snippet as evidence or empty string>",
  "confidence": 0-100
}}

If unsure, set status to "fail" and confidence low.
"""

# Simple keyword heuristics (used as fallback)
KEYWORDS_BY_RULE = {
    "Act must define key terms": ["definition", "interpretation", "meaning of", "in this Act"],
    "Act must specify eligibility criteria": ["eligible", "entitled", "eligibility", "claimant", "entitlement"],
    "Act must specify responsibilities of the administering authority": ["Secretary of State", "responsible", "duty", "must exercise", "shall"],
    "Act must include enforcement or penalties": ["penalt", "offence", "sanction", "enforce", "fine"],
    "Act must include payment calculation or entitlement structure": ["allowance", "payment", "amount", "calculate", "entitlement", "standard allowance"],
    "Act must include record-keeping or reporting requirements": ["record", "report", "reporting", "records", "record-keeping"],
}

def try_parse_json(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None

def run_model_check(rule, section_text, idx):
    # idx used to save raw file per-rule
    raw_path = os.path.join(RAW_DIR, f"rule_{idx+1}_raw.txt")
    if not OLLAMA_AVAILABLE:
        with open(raw_path, "w", encoding="utf8") as f:
            f.write("OLLAMA client not available. Skipping LLM check.\n")
        return None, raw_path

    prompt = RULE_PROMPT.format(RULE=rule, SECTION=section_text or "")
    try:
        resp = ollama.chat(model="llama3", messages=[{"role":"user","content":prompt}])
        content = resp.get("message", {}).get("content", "")
        # save raw LLM output for debugging
        with open(raw_path, "w", encoding="utf8") as f:
            f.write(content or "")
        return content, raw_path
    except Exception as e:
        # record the exception for inspection
        with open(raw_path, "w", encoding="utf8") as f:
            f.write("Exception when calling ollama:\n")
            f.write(repr(e))
        return None, raw_path

def heuristic_check(rule, section_text):
    # returns dict in the expected format
    kws = KEYWORDS_BY_RULE.get(rule, [])
    text = (section_text or "").lower()
    evidence = ""
    found = False
    for kw in kws:
        if kw in text:
            # pick first matching sentence as evidence
            m = re.search(r'([^.\\n]*' + re.escape(kw) + r'[^.\\n]*)', text)
            evidence = m.group(0).strip() if m else kw
            found = True
            break
    status = "pass" if found else "fail"
    confidence = 70 if found else 25
    return {"rule": rule, "status": status, "evidence": evidence, "confidence": confidence}

def main(sections_path, out_path=OUTPUT_RULES):
    # load sections
    sections = {}
    try:
        sections = load_json(sections_path)
    except Exception:
        print(f"[!] Could not load sections from {sections_path}. Using empty sections.")
    results = []
    for idx, (rule_text, section_key) in enumerate(RULES):
        sec_text = sections.get(section_key, "")
        # 1) Try LLM if available and parse JSON
        llm_content, raw_path = run_model_check(rule_text, sec_text, idx)
        parsed = try_parse_json(llm_content or "")
        if parsed and isinstance(parsed, dict) and {"rule","status","evidence","confidence"} <= set(parsed.keys()):
            # normalize confidence as int and ensure keys present
            parsed["confidence"] = int(parsed.get("confidence", 0))
            results.append(parsed)
            print(f"[+] Rule {idx+1} -> used LLM JSON. Raw saved to {raw_path}")
            continue

        # 2) If no valid JSON, run heuristic fallback
        fallback = heuristic_check(rule_text, sec_text)
        # annotate where fallback came from
        fallback["_fallback_from"] = "heuristic"
        fallback["_raw_llm_file"] = raw_path
        results.append(fallback)
        print(f"[!] Rule {idx+1} -> fallback heuristic used. Raw LLM output at {raw_path}")

    save_json(out_path, results)
    print(f"[+] Rule checks saved to: {out_path}")
    print(f"[+] Raw LLM outputs (per-rule) saved to: {RAW_DIR}")
    return out_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sections", dest="sections", default=os.path.join(BASE,"output","sections.json"))
    parser.add_argument("--out", dest="out", default=OUTPUT_RULES)
    args = parser.parse_args()
    main(args.sections, args.out)
