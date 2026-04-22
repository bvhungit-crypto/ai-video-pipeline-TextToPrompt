import requests
import json
import base64
import time
import os
import subprocess
from pathlib import Path
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from main import run_pipeline_from_text


# ========= CONFIG =========
CREDENTIALS_FILE = "credentials.json"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "bvhungit-crypto/youtube-scripts"


# ========= GOOGLE AUTH =========
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)


# ========= LOAD CONFIG =========
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


# ========= LOAD SRT =========
def load_srt_from_url(url):
    url = url.replace("/edit", "/export?format=txt")
    res = requests.get(url)
    res.raise_for_status()
    return res.text


# ========= UPLOAD GITHUB =========
def upload_to_github(filename, content):
    url = f"https://api.github.com/repos/{REPO}/contents/{filename}"

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    data = {
        "message": f"add {filename}",
        "content": encoded
    }

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    res = requests.put(url, headers=headers, json=data)
    res.raise_for_status()

    return f"https://raw.githubusercontent.com/{REPO}/main/{filename}"


def publish_rendered_file(session_id, content):
    rendered_path = Path("data") / "rendered" / f"{session_id}.json"
    rendered_path.parent.mkdir(parents=True, exist_ok=True)
    rendered_path.write_text(content, encoding="utf-8")

    subprocess.run(["git", "add", "."], check=True)

    commit_cmd = ["git", "commit", "-m", f"auto upload {session_id}"]
    commit_run = subprocess.run(commit_cmd, capture_output=True, text=True)
    if commit_run.returncode != 0:
        combined = f"{commit_run.stdout}\n{commit_run.stderr}".lower()
        if "nothing to commit" not in combined:
            raise RuntimeError(commit_run.stderr.strip() or "git commit failed")

    subprocess.run(["git", "push"], check=True)

    return f"https://raw.githubusercontent.com/{REPO}/main/data/rendered/{session_id}.json"


# ========= MAIN LOOP =========
def run():
    for sheet_config in config["sheets"]:
        print(f"\n=== Processing {sheet_config['name']} ===")

        try:
            print("Using ID:", sheet_config["spreadsheet_id"])
            spreadsheet = client.open_by_key(sheet_config["spreadsheet_id"])
            sheet = spreadsheet.worksheet(sheet_config["worksheet"])
        except Exception as e:
            print(f"❌ Cannot open sheet: {e}")
            continue

        header = sheet.row_values(1)
        col_map = {name.strip(): idx + 1 for idx, name in enumerate(header)}
        rows = sheet.get_all_records()

        for i, row in enumerate(rows, start=2):
            normalized_row = {k.lower(): v for k, v in row.items()}
            status = str(row.get("Status", "")).lower()
            script_link = row.get("Str Link") or row.get("str link") or ""
            style = str(normalized_row.get("style", "")).strip().lower()
            if not style:
                style = "cinematic_dark"
            mode = str(normalized_row.get("mode", "character")).strip().lower()
            if not mode:
                mode = "character"
            print("Processing row:", i)
            print("Str Link:", script_link)
            print("STYLE:", style)
            print("MODE:", mode)
            print("FINAL STYLE:", style)
            print("FINAL MODE:", mode)

            if status == "done" or not script_link:
                continue

            print(f"➡️ Processing row {i}...")

            try:
                # 1. Load SRT
                if "github.com" in script_link and "/blob/" in script_link:
                    script_link = script_link.replace("github.com/", "raw.githubusercontent.com/")
                    script_link = script_link.replace("/blob/", "/")
                srt_text = load_srt_from_url(script_link)

                # 2. Run pipeline
                output = run_pipeline_from_text(srt_text, style=style, mode=mode)

                # 3. Convert JSON
                prompt_text = json.dumps(output, ensure_ascii=False, indent=2)

                # 4. Save rendered file + git upload
                session_id = f"{sheet_config['name']}_row_{i}_{int(time.time())}"
                github_link = publish_rendered_file(session_id, prompt_text)

                # 5. Update sheet
                sheet.update_cell(i, col_map["Prompt"], github_link)
                sheet.update_cell(i, col_map["Status"], "done")

                print(f"✅ Done row {i}")

            except Exception as e:
                print(f"❌ Error row {i}: {e}")


# ========= RUN =========
if __name__ == "__main__":
    run()