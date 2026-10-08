"""Rebuild the "All repositories" table in README.md from the GitHub API.

Runs in GitHub Actions on a schedule, so a new public repository shows up on the
profile without editing the README by hand.
"""
import json
import os
import re
import urllib.request
from datetime import datetime

USER = "YoussefSaeed1"
README = "README.md"
START, END = "<!-- REPOS:START -->", "<!-- REPOS:END -->"

# Used only when a repository has no "About" description on GitHub.
FALLBACK = {
    "portfolio": "Personal portfolio website: Power BI projects, skills, experience and speaking",
    "powerbi-projects": "Power BI dashboards built around business questions, with findings and full report pages",
    "Heart_Disease_Project": "Heart disease risk prediction: ML pipeline and a Streamlit app",
    "ERD-Kiwilytics-Project": "Entity Relationship Diagram for a sales and order-management database",
    "courtfit": "CourtFit: Push/Pull/Legs + tennis training app (installable PWA, works offline)",
}
SKIP = {USER, "YoussefSaeed1.github.io"}
LANG_ICON = {"Python": "🐍", "Jupyter Notebook": "📓", "HTML": "🌐", "JavaScript": "🟨",
             "TypeScript": "🔷", "R": "📈", "SQL": "🗄", "TSQL": "🗄"}


def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed&type=owner",
        headers={"Accept": "application/vnd.github+json", "User-Agent": USER})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def build_table(repos):
    rows = ["| Repository | What it is | Language | Updated |", "|---|---|---|---|"]
    for repo in repos:
        name = repo["name"]
        if repo.get("fork") or repo.get("archived") or repo.get("private") or name in SKIP:
            continue
        desc = (repo.get("description") or FALLBACK.get(name) or "—").replace("|", "/")
        lang = repo.get("language") or "—"
        icon = LANG_ICON.get(lang, "")
        updated = datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %Y")
        link = f"[**{name}**]({repo['html_url']})"
        if repo.get("homepage"):
            link += f" · [live]({repo['homepage']})"
        lang_cell = f"{icon} {lang}".strip()
        rows.append(f"| {link} | {desc} | {lang_cell} | {updated} |")
    return "\n".join(rows)


def main():
    table = build_table(fetch_repos())
    text = open(README, encoding="utf-8").read()
    new = re.sub(re.escape(START) + r".*?" + re.escape(END),
                 f"{START}\n{table}\n{END}", text, flags=re.S)
    if new != text:
        open(README, "w", encoding="utf-8").write(new)
        print("README updated")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
