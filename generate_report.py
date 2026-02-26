import requests
import time
from datetime import datetime

WIKI_API = "https://sv.wikipedia.org/w/api.php"
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

S = requests.Session()
S.headers.update({
    "User-Agent": "Wikipedia_cat_monitor/1.0 (https://github.com/salgo60/ifkdb)"
})


import json
import os

HISTORY_FILE = "data/history.json"

def update_history(total_clubs, total_players, total_with_p54):

    os.makedirs("data", exist_ok=True)

    total_missing = total_players - total_with_p54
    percent_missing = round((total_missing / total_players) * 100, 2) if total_players else 0

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "clubs": total_clubs,
        "players": total_players,
        "with_p54": total_with_p54,
        "missing": total_missing,
        "percent_missing": percent_missing
    }

    history = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

    history.append(snapshot)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    return history
    
# ---------------------------------------------------
# Helpers
# ---------------------------------------------------

def get_subcategories(category_title):
    members = []
    cmcontinue = None

    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category_title,
            "cmtype": "subcat",
            "cmlimit": "500",
            "format": "json",
            "formatversion": "2"
        }

        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        r = S.get(WIKI_API, params=params)
        r.raise_for_status()
        data = r.json()

        members.extend(data["query"]["categorymembers"])

        if "continue" in data:
            cmcontinue = data["continue"]["cmcontinue"]
            time.sleep(0.2)
        else:
            break

    return [m["title"] for m in members]


def get_category_players(category_title):
    members = []
    gcmcontinue = None

    while True:
        params = {
            "action": "query",
            "generator": "categorymembers",
            "gcmtitle": category_title,
            "gcmlimit": "max",
            "gcmnamespace": 0,
            "prop": "pageprops",
            "format": "json",
            "formatversion": "2"
        }

        if gcmcontinue:
            params["gcmcontinue"] = gcmcontinue

        r = S.get(WIKI_API, params=params)
        r.raise_for_status()
        data = r.json()

        if "query" in data:
            for page in data["query"]["pages"]:
                qid = page.get("pageprops", {}).get("wikibase_item")
                if qid:
                    members.append(qid)

        if "continue" in data:
            gcmcontinue = data["continue"]["gcmcontinue"]
            time.sleep(0.2)
        else:
            break

    return members


def get_team_qid_from_category(category_title):

    params = {
        "action": "query",
        "titles": category_title,
        "prop": "pageprops",
        "format": "json",
        "formatversion": "2"
    }

    r = S.get(WIKI_API, params=params)
    r.raise_for_status()
    data = r.json()

    pages = data.get("query", {}).get("pages", [])
    if not pages or "pageprops" not in pages[0]:
        return None

    category_qid = pages[0]["pageprops"].get("wikibase_item")
    if not category_qid:
        return None

    query = f"""
    SELECT ?club WHERE {{
      wd:{category_qid} wdt:P971 ?club .
      ?club wdt:P31/wdt:P279* wd:Q476028 .
    }}
    """

    headers = {
        "User-Agent": S.headers["User-Agent"],
        "Accept": "application/sparql-results+json"
    }

    r = requests.get(SPARQL_ENDPOINT, params={"query": query}, headers=headers)
    r.raise_for_status()
    data = r.json()

    results = data["results"]["bindings"]
    if results:
        return results[0]["club"]["value"].split("/")[-1]

    return None


def get_players_via_p54(team_qid):

    query = f"""
    SELECT (COUNT(?player) as ?count) WHERE {{
      ?player wdt:P54 wd:{team_qid}.
    }}
    """

    headers = {
        "User-Agent": S.headers["User-Agent"],
        "Accept": "application/sparql-results+json"
    }

    r = requests.get(SPARQL_ENDPOINT, params={"query": query}, headers=headers)
    r.raise_for_status()
    data = r.json()

    return int(data["results"]["bindings"][0]["count"]["value"])


# ---------------------------------------------------
# Monitor Report
# ---------------------------------------------------

def generate_report(main_category):

    clubs = get_subcategories(main_category)

    total_players = 0
    total_with_p54 = 0

    club_stats = []

    for club_cat in sorted(clubs):

        print("Analyserar:", club_cat)

        team_qid = get_team_qid_from_category(club_cat)
        if not team_qid:
            continue

        wiki_players = get_category_players(club_cat)
        wiki_count = len(wiki_players)

        wd_count = get_players_via_p54(team_qid)

        total_players += wiki_count
        total_with_p54 += min(wiki_count, wd_count)

        missing = max(0, wiki_count - wd_count)

        percent_missing = round((missing / wiki_count) * 100, 1) if wiki_count else 0

        club_stats.append({
            "club": club_cat.replace("Kategori:", ""),
            "wiki_count": wiki_count,
            "wd_count": wd_count,
            "missing": missing,
            "percent_missing": percent_missing
        })

        time.sleep(0.2)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    today_str = datetime.now().strftime("%Y%m%d")

    report_filename = f"monitor_report_{today_str}.html"

    html = f"""
    <h1>Monitor – P54 Coverage</h1>
    <p><strong>Generated:</strong> {timestamp}</p>
    <p><strong>Category:</strong> {main_category}</p>

    <ul>
        <li>Total clubs: {len(club_stats)}</li>
        <li>Total players (Wikipedia): {total_players}</li>
        <li>Total with P54 (approx): {total_with_p54}</li>
        <li>Total missing (approx): {total_players - total_with_p54}</li>
    </ul>

    <table border="1" cellpadding="6">
        <tr>
            <th>Club</th>
            <th>Wikipedia players</th>
            <th>P54 count</th>
            <th>Missing</th>
            <th>% Missing</th>
        </tr>
    """

    for club in sorted(club_stats, key=lambda x: x["percent_missing"], reverse=True):

        row_color = ' style="background-color:#ffdddd;"' if club["percent_missing"] > 30 else ""

        html += f"""
        <tr{row_color}>
            <td>{club["club"]}</td>
            <td>{club["wiki_count"]}</td>
            <td>{club["wd_count"]}</td>
            <td>{club["missing"]}</td>
            <td>{club["percent_missing"]}%</td>
        </tr>
        """

    html += "</table>"

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(html)

    print("\nMonitor report created:", report_filename)


# ---------------------------------------------------
# RUN
# ---------------------------------------------------

if __name__ == "__main__":
    category = "Kategori:Fotbollsspelare_i_klubblag_i_Sverige"
    generate_report(category)