# agent.py
import os
import subprocess
import sys
from src.utils import load_json, save_json

BASE = os.path.dirname(os.path.dirname(__file__))

def run(script):
    print(f"[ RUN ] {script}")
    subprocess.check_call([sys.executable, os.path.join(BASE, "src", script)])

def main():
    run("extract_text.py")
    run("summarize_act.py")
    run("extract_sections.py")
    run("rule_checker.py")

    final = {
        "summary": load_json("output/summary.json"),
        "sections": load_json("output/sections.json"),
        "rule_checks": load_json("output/rule_checks.json")
    }

    save_json("output/final_output.json", final)

    print("\n[+] FINAL OUTPUT READY → output/final_output.json")

if __name__ == "__main__":
    main()
