import json
import os
import re
import urllib.request


HTML_PATH = os.path.join(os.path.dirname(__file__), "index.html")


def fetch_json(url: str, timeout: int = 8):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def safe_get_json(url: str):
    try:
        return fetch_json(url)
    except Exception:
        return None


def read_html() -> str:
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()


def write_html(html: str) -> None:
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)


def get_meta_content(html: str, attr: str, name: str) -> str | None:
    pattern = rf'<meta\s+[^>]*{attr}="{re.escape(name)}"[^>]*content="([^"]*)"'
    m = re.search(pattern, html, flags=re.IGNORECASE)
    return m.group(1) if m else None


def replace_meta(html: str, attr: str, name: str, content: str) -> str:
    pattern = rf'(<meta\s+[^>]*{attr}="{re.escape(name)}"[^>]*content=")([^"]*)(")'
    if re.search(pattern, html, flags=re.IGNORECASE):
        return re.sub(pattern, rf'\g<1>{content}\3', html, flags=re.IGNORECASE)
    insert = f'    <meta {attr}="{name}" content="{content}">\n'
    return html.replace("</head>", insert + "</head>")


def replace_title(html: str, title: str) -> str:
    pattern = r"(<title>)(.*?)(</title>)"
    if re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL):
        return re.sub(pattern, rf"\1{title}\3", html, flags=re.IGNORECASE | re.DOTALL)
    return html


def upsert_jsonld(html: str, jsonld: dict) -> str:
    json_text = json.dumps(jsonld, ensure_ascii=True)
    pattern = r'(<script\s+[^>]*id="meapi-jsonld"[^>]*>)(.*?)(</script>)'
    if re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL):
        return re.sub(pattern, rf'\1{json_text}\3', html, flags=re.IGNORECASE | re.DOTALL)
    insert = f'    <script type="application/ld+json" id="meapi-jsonld">{json_text}</script>\n'
    return html.replace("</head>", insert + "</head>")


def truncate(text: str, max_len: int = 220) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def main() -> None:
    html = read_html()

    api_base = os.getenv("API_BASE") or get_meta_content(html, "name", "api-base")
    site_url = os.getenv("SITE_URL") or get_meta_content(html, "property", "og:url")
    if not api_base:
        print("Missing API base URL.")
        return

    profile = safe_get_json(f"{api_base}/profile") or {}
    skills = safe_get_json(f"{api_base}/skills") or []
    projects = safe_get_json(f"{api_base}/projects") or []

    name = profile.get("name") or "Me-API Playground"
    email = profile.get("email")
    github = profile.get("github")
    linkedin = profile.get("linkedin")
    education = profile.get("education")

    skill_names = [s.get("name") for s in skills if s.get("name")]
    project_items = [
        {
            "title": p.get("title"),
            "description": p.get("description"),
            "url": (p.get("links") or {}).get("link"),
        }
        for p in projects
        if p.get("title")
    ]

    skills_preview = ", ".join(skill_names[:8]) if skill_names else "Profile, skills, projects"
    projects_preview = ", ".join([p["title"] for p in project_items[:3]])

    description = f"{name} — {education or 'Portfolio'}."
    if skills_preview:
        description += f" Skills: {skills_preview}."
    if projects_preview:
        description += f" Projects: {projects_preview}."
    description = truncate(description, 220)

    title = f"{name} | Me-API Playground"

    html = replace_title(html, title)
    html = replace_meta(html, "name", "description", description)
    html = replace_meta(html, "name", "author", name)
    html = replace_meta(html, "name", "keywords", ", ".join(skill_names[:12]))

    html = replace_meta(html, "property", "og:title", title)
    html = replace_meta(html, "property", "og:description", description)
    if site_url:
        html = replace_meta(html, "property", "og:url", site_url)

    html = replace_meta(html, "name", "twitter:title", title)
    html = replace_meta(html, "name", "twitter:description", description)

    jsonld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "email": email,
        "url": site_url,
        "sameAs": [v for v in [github, linkedin] if v],
        "knowsAbout": skill_names[:20],
        "subjectOf": [
            {
                "@type": "CreativeWork",
                "name": p["title"],
                "description": p.get("description"),
                "url": p.get("url"),
            }
            for p in project_items[:10]
        ],
    }

    html = upsert_jsonld(html, jsonld)
    write_html(html)
    print("Metadata updated.")


if __name__ == "__main__":
    main()
