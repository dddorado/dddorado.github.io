from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIKI_PATH = ROOT / "wiki.md"
INDEX_PATH = ROOT / "index.html"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def join_human(items: list[str]) -> str:
    items = [item.strip() for item in items if item.strip()]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def natural_phrase(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    if value.startswith("AI"):
        return value
    return value[0].lower() + value[1:]


def first_sentence(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)
    return parts[0].strip()


def section_body(text: str, title: str) -> str:
    pattern = rf"^## {re.escape(title)}\n\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"Missing section: {title}")
    return match.group(1).strip()


def subsection_bodies(text: str) -> list[tuple[str, str]]:
    matches = re.finditer(
        r"^### (.+?)\n\n(.*?)(?=^### |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return [(match.group(1).strip(), match.group(2).strip()) for match in matches]


def bullet_lines(text: str) -> list[str]:
    return [line[2:].strip() for line in text.splitlines() if line.startswith("- ")]


def nonempty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def parse_key_value_bullets(text: str) -> list[tuple[str, str]]:
    items = []
    for line in bullet_lines(text):
        key, value = line.split(":", 1)
        items.append((key.strip(), value.strip()))
    return items


def parse_education(lines: list[str]) -> list[dict[str, str]]:
    items = []
    for line in lines:
        dates, rest = line.split(":", 1)
        degree, institution = rest.strip().rsplit(", ", 1)
        items.append(
            {
                "dates": dates.strip(),
                "degree": degree.strip(),
                "institution": institution.strip(),
            }
        )
    return items


def parse_skills(text: str) -> list[dict[str, object]]:
    groups = []
    for title, body in subsection_bodies(text):
        groups.append({"title": title, "items": bullet_lines(body)})
    return groups


def parse_appointments(lines: list[str]) -> list[dict[str, str]]:
    items = []
    for line in lines:
        if ": " in line:
            dates, rest = line.split(": ", 1)
            main, note = (rest.rsplit(". ", 1) + [""])[:2] if ". " in rest else (rest, "")
            title, organization = main.split(", ", 1)
        else:
            parts = line.rstrip(".").split(". ", 2)
            if len(parts) < 3:
                raise ValueError(f"Could not parse appointment line: {line}")
            dates, title, organization = parts
            note = ""
        items.append(
            {
                "dates": dates.strip(),
                "title": title.strip(),
                "organization": organization.strip().rstrip("."),
                "note": note.strip().rstrip(".") + ("." if note.strip() else ""),
            }
        )
    return items


def parse_teaching(text: str) -> list[dict[str, object]]:
    groups = []
    for theme, body in subsection_bodies(text):
        courses = []
        for line in bullet_lines(body):
            heading, description = (line.split(". ", 1) + [""])[:2]
            code, title = heading.split(", ", 1)
            courses.append(
                {
                    "code": code.strip(),
                    "title": title.strip(),
                    "description": description.strip().rstrip(".") + ("." if description.strip() else ""),
                }
            )
        groups.append({"theme": theme, "courses": courses})
    return groups


def parse_publication_line(line: str) -> dict[str, str]:
    match = re.match(
        r"(?P<year>\d{4})\.\s+(?P<title>.+?)\.\s+\*(?P<venue>.+?)\*\.(?:\s+(?P<label>DOI|Link):\s+(?P<link>.+))?$",
        line,
    )
    if not match:
        raise ValueError(f"Could not parse publication line: {line}")
    data = {
        "year": match.group("year").strip(),
        "title": match.group("title").strip(),
        "venue": match.group("venue").strip(),
    }
    if match.group("link"):
        data["link"] = match.group("link").strip()
    return data


def parse_publications(text: str) -> list[dict[str, object]]:
    featured_section = section_body(text, "Publications")
    featured_subsections = dict(subsection_bodies(featured_section))
    featured_titles = {
        parse_publication_line(line)["title"]
        for line in bullet_lines(featured_subsections.get("Featured publications", ""))
    }
    publications = []
    for line in bullet_lines(featured_subsections.get("Full publication list", "")):
        item = parse_publication_line(line)
        item["featured"] = item["title"] in featured_titles
        publications.append(item)
    return publications


def parse_projects(lines: list[str]) -> list[dict[str, str]]:
    items = []
    for line in lines:
        match = re.match(
            r"(?P<dates>.+?)\.\s+(?P<title>.+?)\.\s+Funding body:\s+(?P<funder>.+?)\.\s+Role:\s+(?P<role>.+?)\.?$",
            line,
        )
        if not match:
            raise ValueError(f"Could not parse project line: {line}")
        items.append(
            {
                "dates": match.group("dates").strip(),
                "title": match.group("title").strip(),
                "funder": match.group("funder").strip(),
                "role": match.group("role").strip(),
            }
        )
    return items


def parse_advising(lines: list[str]) -> list[dict[str, str]]:
    items = []
    for line in lines:
        match = re.match(
            r"(?P<year>\d{4})\.\s+(?P<name>.+?)\.\s+\*(?P<title>.+?)\*\s*(?P<rest>.*)$",
            line,
        )
        if not match:
            raise ValueError(f"Could not parse advising line: {line}")
        rest = match.group("rest").lstrip(". ").strip()
        role = ""
        if "Role:" in rest:
            level, role_part = rest.split("Role:", 1)
            role = role_part.strip().rstrip(".")
        else:
            level = rest
        items.append(
            {
                "year": match.group("year").strip(),
                "title": match.group("title").strip(),
                "name": match.group("name").strip(),
                "level": level.strip().rstrip("."),
                **({"role": role} if role else {}),
            }
        )
    return items


def parse_talks(lines: list[str]) -> list[dict[str, object]]:
    items = []
    for index, line in enumerate(lines):
        match = re.match(r"(?P<date>\d{4}/\d{2})\.\s+\*(?P<title>.+?)\*\.\s+(?P<rest>.+)$", line)
        if not match:
            raise ValueError(f"Could not parse talk line: {line}")
        rest = match.group("rest").strip().rstrip(".")
        if ". " in rest:
            event, place = rest.split(". ", 1)
        elif " · " in rest:
            event, place = rest.split(" · ", 1)
        else:
            event, place = rest, ""
        items.append(
            {
                "featured": index < 6,
                "date": match.group("date").strip(),
                "year": match.group("date").split("/")[0],
                "title": match.group("title").strip(),
                "event": event.strip(),
                "place": place.strip(),
            }
        )
    return items


def parse_service(text: str) -> list[dict[str, object]]:
    groups = []
    for title, body in subsection_bodies(text):
        items = []
        for line in bullet_lines(body):
            parts = line.rstrip(".").split(". ", 2)
            if len(parts) != 3:
                raise ValueError(f"Could not parse service line: {line}")
            dates, role, organization = parts
            items.append(
                {
                    "dates": dates.strip(),
                    "role": role.strip(),
                    "organization": organization.strip(),
                }
            )
        groups.append({"title": title, "items": items})
    return groups


def parse_wiki(text: str) -> dict[str, object]:
    name = section_body(text, "Name")
    current_role = section_body(text, "Current academic role")
    professional_summary = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", section_body(text, "Professional summary"))
        if paragraph.strip()
    ]
    contact_links = parse_key_value_bullets(section_body(text, "Contact and links"))
    institutional_profile = dict(parse_key_value_bullets(section_body(text, "Institutional profile")))
    education = parse_education(bullet_lines(section_body(text, "Education")))
    research_interests = bullet_lines(section_body(text, "Research interests"))
    skills = parse_skills(section_body(text, "Skills"))
    appointments = parse_appointments(bullet_lines(section_body(text, "Professional appointments")))
    teaching = parse_teaching(section_body(text, "Teaching"))
    publications = parse_publications(text)
    projects = parse_projects(bullet_lines(section_body(text, "Projects and grants")))
    advising = parse_advising(bullet_lines(section_body(text, "Advising and mentorship")))
    talks = parse_talks(bullet_lines(section_body(text, "Talks, presentations, and engagements")))
    service = parse_service(section_body(text, "Service and leadership"))

    highlight_research_items = [natural_phrase(item) for item in research_interests[:6]]
    highlight_research = (
        f"Research interests include {join_human(highlight_research_items)}."
        if research_interests
        else "Research interests are documented in the resume."
    )
    teaching_themes = [natural_phrase(group["theme"]) for group in teaching]
    highlight_teaching = (
        f"Teaching spans {join_human(teaching_themes[:5])}."
        if teaching_themes
        else "Teaching activity is documented in the resume."
    )
    highlight_talks = (
        "Talks and presentations address AI, libraries, education, tourism analytics, digital humanities, and research methods."
    )

    return {
        "name": name.strip(),
        "current_role": current_role.strip(),
        "professional_summary": professional_summary,
        "contact_links": contact_links,
        "institutional_profile": institutional_profile,
        "portfolio_data": {
            "highlights": [
                {
                    "title": "Research across LIS, data, and critical methods",
                    "text": highlight_research,
                },
                {
                    "title": "Teaching from information systems to digital scholarship",
                    "text": highlight_teaching,
                },
                {
                    "title": "Public engagement through talks, workshops, and conference work",
                    "text": highlight_talks,
                },
            ],
            "education": education,
            "researchInterests": research_interests,
            "skills": skills,
            "appointments": appointments,
            "credentials": [],
            "teachingGroups": teaching,
            "publications": publications,
            "projects": projects,
            "advising": advising,
            "talks": talks,
            "service": service,
        },
    }


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def contact_href(label: str, value: str) -> str:
    return f"mailto:{value}" if label.lower() == "email" else value


def render_links(items: list[tuple[str, str]], class_name: str, indent: str) -> str:
    lines = [f'{indent}<ul class="{class_name}" aria-label="Professional links">' if class_name == "quick-links" else f'{indent}<ul class="{class_name}">']
    for label, value in items:
        lines.append(
            f'{indent}  <li><a href="{escape(contact_href(label, value))}">{escape(label)}</a></li>'
        )
    lines.append(f"{indent}</ul>")
    return "\n".join(lines)


def role_parts(current_role: str, institutional_base: str) -> tuple[str, str, str]:
    parts = [part.strip() for part in current_role.split(",")]
    title = parts[0] if parts else current_role
    unit = parts[1] if len(parts) > 1 else institutional_base
    institution = ", ".join(parts[2:]).strip() if len(parts) > 2 else institutional_base
    return title, unit, institution


def render_panel(name: str, current_role: str, profile: dict[str, str]) -> str:
    blocks = [
        ("Current role", current_role),
        ("Academic trajectory", profile.get("Academic trajectory", "")),
        ("Institutional base", profile.get("Institutional base", "")),
        ("Research communities", profile.get("Research communities", "")),
        ("Location", profile.get("Location", "")),
    ]
    lines = ['          <aside class="hero-panel" aria-label="Current profile">', f"            <h3>{escape(name)}</h3>"]
    for label, value in blocks:
        if not value:
            continue
        lines.extend(
            [
                '            <div class="panel-block">',
                f'              <p class="panel-label">{escape(label)}</p>',
                f'              <p class="panel-value">{escape(value)}</p>',
                "            </div>",
            ]
        )
    lines.append("          </aside>")
    return "\n".join(lines)


def render_biography(paragraphs: list[str]) -> str:
    lines = ['              <article class="card prose-card">', "                <h3>Biography</h3>"]
    for paragraph in paragraphs:
        lines.append("                <p>")
        lines.append(f"                  {escape(paragraph)}")
        lines.append("                </p>")
    lines.append("              </article>")
    return "\n".join(lines)


def render_contact_card(current_role: str, profile: dict[str, str], links: list[tuple[str, str]]) -> str:
    title, unit, institution = role_parts(current_role, profile.get("Institutional base", ""))
    email_value = next((value for label, value in links if label.lower() == "email"), "")
    external_links = [(label, value) for label, value in links if label.lower() != "email"]

    lines = [
        '          <div class="contact-card">',
        "            <div>",
        "              <h3>Professional contact</h3>",
        f'              <p><a href="mailto:{escape(email_value)}">{escape(email_value)}</a></p>',
    ]
    if unit:
        lines.append(f"              <p>{escape(unit)}</p>")
    if institution:
        lines.append(f"              <p>{escape(institution)}</p>")
    if profile.get("Location"):
        lines.append(f'              <p>{escape(profile["Location"])}</p>')
    lines.extend(
        [
            "            </div>",
            "",
            "            <div>",
            "              <h3>External profiles</h3>",
            render_links(external_links, "contact-links", "              "),
            "            </div>",
            "          </div>",
        ]
    )
    return "\n".join(lines)


def replace_pattern(content: str, pattern: str, replacement: str, flags: int = re.DOTALL) -> str:
    updated, count = re.subn(pattern, replacement, content, count=1, flags=flags)
    if count != 1:
        raise ValueError(f"Pattern not found or not unique: {pattern}")
    return updated


def update_index(index_text: str, wiki: dict[str, object]) -> str:
    current_role = wiki["current_role"]
    profile = wiki["institutional_profile"]
    summary = wiki["professional_summary"]
    links = wiki["contact_links"]
    title, unit, _ = role_parts(current_role, profile.get("Institutional base", ""))
    research_interests = wiki["portfolio_data"]["researchInterests"]

    lead = (
        f"{title} at {unit}, working across {join_human([natural_phrase(item) for item in research_interests[:7]])}."
        if unit and research_interests
        else current_role
    )
    about_intro = first_sentence(summary[0]) if summary else ""
    contact_intro = (
        "For research collaboration, speaking invitations, teaching engagements, and "
        "professional inquiries, the institutional email below is the best first contact."
    )

    data_json = json.dumps(wiki["portfolio_data"], ensure_ascii=False, indent=2)
    content = index_text
    content = replace_pattern(
        content,
        r"window\.portfolioData = \{.*?^\};",
        f"window.portfolioData = {data_json};",
        flags=re.MULTILINE | re.DOTALL,
    )
    content = replace_pattern(
        content,
        r'(?s)\n\s*<p class="lead">\s*.*?\s*</p>',
        "\n".join(
            [
                "",
                '            <p class="lead">',
                f"              {escape(lead)}",
                "            </p>",
            ]
        ),
    )
    content = replace_pattern(
        content,
        r'(?s)\n\s*<ul class="quick-links" aria-label="Professional links">.*?</ul>',
        "\n" + render_links(links, "quick-links", "            "),
    )
    content = replace_pattern(
        content,
        r'(?s)\n\s*<aside class="hero-panel" aria-label="Current profile">.*?</aside>',
        "\n" + render_panel(wiki["name"], current_role, profile),
    )
    content = replace_pattern(
        content,
        r'(<h2 id="about-title">Academic profile</h2>\s*<p>\s*).*?(\s*</p>)',
        rf"\1{escape(about_intro)}\2",
        flags=re.DOTALL,
    )
    content = replace_pattern(
        content,
        r'(?s)\n\s*<article class="card prose-card">.*?</article>',
        "\n" + render_biography(summary),
    )
    content = replace_pattern(
        content,
        r'(<h2 id="contact-title">Get in touch</h2>\s*<p>\s*).*?(\s*</p>)',
        rf"\1{escape(contact_intro)}\2",
        flags=re.DOTALL,
    )
    content = replace_pattern(
        content,
        r'(?s)\n\s*<div class="contact-card">.*?</div>\s*</div>\s*</section>',
        "\n" + f"{render_contact_card(current_role, profile, links)}\n        </div>\n      </section>",
    )
    return content


def main() -> None:
    wiki_text = read_text(WIKI_PATH)
    index_text = read_text(INDEX_PATH)
    parsed = parse_wiki(wiki_text)
    updated_index = update_index(index_text, parsed)
    write_text(INDEX_PATH, updated_index)


if __name__ == "__main__":
    main()
