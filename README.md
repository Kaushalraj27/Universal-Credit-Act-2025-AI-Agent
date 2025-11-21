# Universal-Credit-Act-2025-AI-Agent

TL;DR — A full local AI pipeline using **Ollama + llama3** to extract text from a legislative PDF, summarize it, extract key legal sections, and run rule-based validations. All outputs saved in `output/`. Works fully offline on GPU.

---

##  Table of Contents
- Features  
- Project Structure  
- How to Install  
- How to Run  
- JSON Schemas (Expected Outputs)  
- What Each File Does  
- Sample Screenshot  
- Example Output Files  
- Notes & Best Practices  
- Submission Checklist  
- Author  

---

##  Features
- PDF → Text extraction  
- LLM-based Act summarization  
- Section extraction:
  - Definitions  
  - Obligations  
  - Responsibilities  
  - Eligibility  
  - Payments / Entitlements  
  - Penalties / Enforcement  
  - Record-keeping  
- Rule-based validation (6 checks)  
- Fully local using **Ollama + llama3** (no API needed)  
- GPU support  
- Automatic fallback logic to avoid pipeline failures  
- All outputs stored inside `output/`

---

##  Project Structure
<img width="189" height="627" alt="image" src="https://github.com/user-attachments/assets/52b31922-aaf9-493a-b571-2c3dafc5a60a" />


### `rule_raw/` folder
Raw LLM responses for each rule — useful for debugging + submission.

---

##  How to install
```bash
python -m venv .venv_ollama
.venv_ollama\Scripts\activate
pip install -r requirements.txt
pip install ollama
ollama pull llama3
````

---

##  How to run

```bash
python -m src.extract_text --pdf data/act.pdf
python -m src.summarize_act --text output/extracted_text.txt
python -m src.extract_sections --text output/extracted_text.txt
python -m src.rule_checker --sections output/sections.json
```

### Local example PDF path used in this environment:

```
/mnt/data/ukpga_20250022_en.pdf
```

---

##  JSON Schemas (Expected Output Format)

### `sections.json`

```json
{
  "definitions": "",
  "obligations": "",
  "responsibilities": "",
  "eligibility": "",
  "payments": "",
  "penalties": "",
  "record_keeping": ""
}
```

### `rule_checks.json`

```json
[
  {
    "rule": "Act must define key terms",
    "status": "pass",
    "evidence": "text snippet...",
    "confidence": 85
  }
]
```

---

##  What each file does

### `extract_text.py`

Extracts text from the Act PDF and writes:

```
output/extracted_text.txt
```

### `summarize_act.py`

Runs LLM summarization using **Ollama (llama3)** → writes:

```
output/summary.json
```

### `extract_sections.py`

Attempts LLM JSON extraction → if invalid JSON, uses robust heuristic fallback. Writes:

```
output/sections.json
output/sections_raw.txt
```

### `rule_checker.py`

Runs 6 rule checks using LLM JSON + fallback heuristics. Writes:

```
output/rule_checks.json
output/rule_raw/
```

### `utils.py`

Helper functions (save/load text, save JSON, etc.)

### `agent.py` (optional)

End-to-end pipeline runner.

---

##  sample screenshot

<img width="1618" height="884" alt="image" src="https://github.com/user-attachments/assets/6844f899-9314-451f-8992-34c123676c29" />


---

##  Example output files (paths from this environment)

* Extracted text → `/mnt/data/extracted_text.txt`
* Sections JSON → `/mnt/data/sections.json`
* Summary JSON → `/mnt/data/summary.json`
* Rule checks JSON → `/mnt/data/rule_checks.json`
* Raw LLM sections output → `/mnt/data/sections_raw.txt`
* Rule raw folder (local project): `output/rule_raw/`

---

##  Notes & Best Practices

* Always run commands **from project root**.
* If you see:

  ```
  ModuleNotFoundError: No module named 'src'
  ```

  run:

  ```bash
  set PYTHONPATH=%cd%
  python -m src.extract_text ...
  ```
* If LLM produces non-JSON, fallback automatically handles extraction.
* For stricter JSON, prepend the prompt with:

  ```
  Return ONLY valid JSON. No explanation. Keys: definitions, obligations, responsibilities, eligibility, payments, penalties, record_keeping.
  ```

---

##  Submission Checklist

Submit these files:

* [x] `output/extracted_text.txt`
* [x] `output/summary.json`
* [x] `output/sections.json`
* [x] `output/rule_checks.json`
* [x] Entire `src/` folder
* [x] `requirements.txt`
* [x] `README.md` (this file)
* [x] (Optional) `output/rule_raw/`
* [x] (Optional) Terminal screenshot

---

##  Author

**Kaushal Raj**
NIYAMR 48-Hour Internship Assignment
Using **Ollama + llama3** for fully local legal-AI automation.
