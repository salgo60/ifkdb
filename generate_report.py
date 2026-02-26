import requests
import time
from datetime import datetime

from datetime import datetime

def log(message):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}", flush=True) 

WIKI_API = "https://sv.wikipedia.org/w/api.php"
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

S = requests.Session()
S.headers.update({
    "User-Agent": "Wikipedia_cat/1.0 (https://github.com/salgo60/ifkdb; contact: salgo60@msn.com)"
})

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
                    members.append({
                        "name": page["title"],
                        "qid": qid
                    })

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
    data = sparql_query(query)

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
    SELECT ?player WHERE {{
      ?player wdt:P54 wd:{team_qid}.
    }}
    """

    headers = {
        "User-Agent": S.headers["User-Agent"],
        "Accept": "application/sparql-results+json"
    }

    r = requests.get(SPARQL_ENDPOINT, params={"query": query}, headers=headers)
    r.raise_for_status()
    data = sparql_query(query)

    return {
        row["player"]["value"].split("/")[-1]
        for row in data["results"]["bindings"]
    }
def sparql_query(query):

    headers = {
        "User-Agent": S.headers["User-Agent"],
        "Accept": "application/sparql-results+json"
    }

    for attempt in range(5):
        r = requests.get(
            SPARQL_ENDPOINT,
            params={"query": query},
            headers=headers
        )

        if r.status_code == 429:
            wait = 5 * (attempt + 1)
            log(f"429 Too Many Requests — sleeping {wait}s")
            time.sleep(wait)
            continue

        if r.status_code >= 500:
            wait = 3 * (attempt + 1)
            log(f"Server error {r.status_code} — retrying in {wait}s")
            time.sleep(wait)
            continue

        r.raise_for_status()
        return r.json()

    raise Exception("SPARQL failed after retries")

# ---------------------------------------------------
# MAIN REPORT
# ---------------------------------------------------

def generate_report(main_category):

    log("=== START MONITOR ===")
    log(f"Category: {main_category}")

    #clubs = get_subcategories(main_category)
    clubs = get_subcategories(main_category)[:20]
    #log(f"Found {len(clubs)} clubs")
    log(f"Processing first {len(clubs)} clubs (CI limit)")

    total_players = 0
    total_correct = 0
    total_missing = 0

    today_str = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    report_filename = f"rapport_{today_str}.html"
    qs_filename = f"quickstatements_P54_missing_{today_str}.txt"

    quickstatements = []
    html_blocks = ""

    for club_cat in sorted(clubs):

        start_time = time.time()
        log(f"Processing club: {club_cat}")

        team_qid = get_team_qid_from_category(club_cat)
        if not team_qid:
            continue

        wiki_players = get_category_players(club_cat)
        wd_players = get_players_via_p54(team_qid)

        club_total = 0
        club_missing = 0
        rows = ""

        for player in sorted(wiki_players, key=lambda x: x["name"]):

            club_total += 1
            total_players += 1

            has_p54 = player["qid"] in wd_players

            if has_p54:
                total_correct += 1
            else:
                total_missing += 1
                club_missing += 1
                quickstatements.append(f'{player["qid"]}|P54|{team_qid}')

            lag_url = f"https://sv.wikipedia.org/wiki/{club_cat.replace(' ', '_')}"
            player_url = f"https://sv.wikipedia.org/wiki/{player['name'].replace(' ', '_')}"
            wikidata_url = f"https://www.wikidata.org/wiki/{player['qid']}"
            p54_url = f"{wikidata_url}#P54"

            row_color = "" if has_p54 else ' style="background-color:#ffdddd;"'
            symbol = "✅" if has_p54 else "❌"
            status_text = "Har P54" if has_p54 else "Saknar P54"

            rows += f"""
            <tr{row_color}>
                <td><a href="{lag_url}" target="_blank">{club_cat.replace("Kategori:", "")}</a></td>
                <td><a href="{player_url}" target="_blank">{player["name"]}</a></td>
                <td><a href="{wikidata_url}" target="_blank">{player["qid"]}</a></td>
                <td>{symbol} <a href="{p54_url}" target="_blank">{status_text}</a></td>
            </tr>
            """

        if club_total == 0:
            continue

        percent_missing = round((club_missing / club_total) * 100, 1)

        html_blocks += f"""
        <details>
            <summary>
                <strong>{club_cat.replace("Kategori:", "")}</strong>
                – Spelare: {club_total}
                – Saknar P54: {club_missing}
                ({percent_missing}%)
            </summary>
            <table border="1" cellpadding="6" cellspacing="0">
                <tr>
                    <th>Lag</th>
                    <th>Spelare</th>
                    <th>Wikidata</th>
                    <th>P54 status</th>
                </tr>
                {rows}
            </table>
            <br>
        </details>
        """

        time.sleep(0.2)
        elapsed = round(time.time() - start_time, 2)
    
    header = f"""
    <h1>Revisionsrapport – Fotbollsspelare i klubblag i Sverige</h1>

    <p>
    <strong>Rapport skapad:</strong> {timestamp}<br>
    <strong>GitHub Issue:</strong>
    <a href="https://github.com/salgo60/ifkdb/issues/17" target="_blank">
    https://github.com/salgo60/ifkdb/issues/17
    </a>
    </p>

    <ul>
        <li><strong>Antal lag:</strong> {len(clubs)}</li>
        <li><strong>Antal spelare:</strong> {total_players}</li>
        <li><strong>Med korrekt wdt:P54:</strong> {total_correct}</li>
        <li><strong>Saknar wdt:P54:</strong> {total_missing}</li>
    </ul>
    <hr>
    """

    full_html = header + html_blocks

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(full_html)

    quickstatements = sorted(set(quickstatements))
    with open(qs_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(quickstatements))

    print("\nKLART ✅")
    print("Rapport:", report_filename)
    print("QuickStatements:", qs_filename)
    print("Antal QS:", len(quickstatements))

    log("=== MONITOR COMPLETE ===")
    log(f"Total players: {total_players}")
    log(f"Total missing: {total_players - total_with_p54}")
    log(f"Report file: {report_filename}")
    return report_filename, qs_filename


# ---------------------------------------------------
# RUN
# ---------------------------------------------------

category = "Kategori:Fotbollsspelare_i_klubblag_i_Sverige"
generate_report(category)

