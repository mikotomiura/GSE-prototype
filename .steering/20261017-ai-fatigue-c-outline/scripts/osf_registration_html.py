"""Save an OSF registration as the full text of a record (decision 36).

Some candidates are OSF registrations (a review protocol or a preregistration) with no article file: the
registration form is the document. The form is laid out as HTML from the OSF API: the schema's page and section
headings and question labels, and the registrant's answers verbatim (file answers by file name). The form's own
instructions (paragraph blocks) and the unchosen options are left out. The page says it was built from the API.

Usage: python3 osf_registration_html.py <guid> <out.html>
"""

import html
import json
import sys
import urllib.request

API = "https://api.osf.io/v2"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=60) as r:
        return json.load(r)


def answer(v):
    if isinstance(v, list):
        return "<ul>" + "".join(f"<li>{html.escape(x.get('file_name', str(x)) if isinstance(x, dict) else str(x))}</li>"
                                for x in v) + "</ul>" if v else "<p>(no answer)</p>"
    text = str(v or "").strip()
    return "".join(f"<p>{html.escape(p)}</p>" for p in text.split("\n") if p.strip()) or "<p>(no answer)</p>"


def main():
    guid, out = sys.argv[1], sys.argv[2]
    d = get(f"{API}/registrations/{guid}/")["data"]
    a = d["attributes"]
    schema = d["relationships"]["registration_schema"]["links"]["related"]["href"]
    blocks = get(schema + "schema_blocks/?page%5Bsize%5D=500")["data"]
    resp = a.get("registration_responses") or {}
    body = []
    for b in sorted(blocks, key=lambda b: b["attributes"]["index"]):
        t, at = b["attributes"]["block_type"], b["attributes"]
        if t == "page-heading":
            body.append(f"<h2>{html.escape(at['display_text'])}</h2>")
        elif t == "subsection-heading":
            body.append(f"<h3>{html.escape(at['display_text'])}</h3>")
        elif t == "question-label":
            body.append(f"<h4>{html.escape(at['display_text'])}</h4>")
        elif at.get("registration_response_key") and t != "select-input-option":
            body.append(answer(resp.get(at["registration_response_key"])))
    head = (f"<h1>{html.escape(a['title'])}</h1><p>OSF registration {guid} ({html.escape(a.get('registration_supplement') or '')}),"
            f" registered {str(a.get('date_registered'))[:10]}. https://osf.io/{guid}/</p>"
            f"<p>{html.escape(a.get('description') or '')}</p>"
            "<p>[This page was built from the OSF API (registration form: headings, questions and the registrant's answers"
            " verbatim). It is not a page saved from the OSF site.]</p>")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(a['title'])}</title></head>"
                f"<body>{head}{''.join(body)}</body></html>\n")
    print(f"wrote {out}: {len(resp)} answers")


if __name__ == "__main__":
    main()
