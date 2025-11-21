import json
import ollama
from src.utils import load_text, save_json

OUTPUT = "output/summary.json"

PROMPT_TEMPLATE = """
Summarize the following ACT into 5–10 bullet points focusing on:
- Purpose
- Key definitions
- Eligibility
- Obligations
- Enforcement elements

TEXT:
{TEXT}
"""

def main(text_path, out_path=OUTPUT):
    text = load_text(text_path)

    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "user", "content": PROMPT_TEMPLATE.format(TEXT=text)}
        ]
    )

    summary = response["message"]["content"]

    save_json(out_path, {"summary": summary})
    print(f"[+] Summary saved → {out_path}")


if __name__ == "__main__":
    main("output/extracted_text.txt")
