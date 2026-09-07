import re


def _get_heading_level(
    line: str,
) -> int | None:
    """
    Geef het Markdown-headingniveau terug.
    """

    match = re.match(
        r"^\s*(#{1,6})\s+",
        line,
    )

    if not match:
        return None

    return len(
        match.group(1)
    )


def _get_section_class(
    line: str,
) -> str | None:
    """
    Zoek een .section-* class in de attributen van een heading.
    """

    match = re.match(
        r"^\s*#{1,6}\s+.*\{([^}]*)\}\s*$",
        line,
    )

    if not match:
        return None

    attributes = match.group(1).split()

    for attribute in attributes:
        if attribute.startswith(".section-"):
            return attribute[1:]

    return None


def _remove_section_marker(
    line: str,
) -> str:
    """
    Verwijder .section-* uit de heading-attributen.

    Andere attributen, zoals .page-toc, blijven staan.
    """

    def replace_attributes(match):
        attributes = [
            attribute
            for attribute in match.group(1).split()
            if not attribute.startswith(".section-")
        ]

        if not attributes:
            return ""

        return "{" + " ".join(attributes) + "}"

    return re.sub(
        r"\{([^}]*)\}\s*$",
        replace_attributes,
        line,
    )


def wrap_sections(
    markdown: str,
) -> str:
    """
    Zet headings met een .section-* class om naar HTML-secties.

    De heading bepaalt het niveau van de section.
    Een section sluit bij een volgende heading op hetzelfde
    of een hoger niveau.

    Sections kunnen daardoor ook genest worden.
    """

    lines = markdown.splitlines()
    output = []

    open_sections = []

    in_fence = False
    fence_marker = None

    for line in lines:

        stripped = line.lstrip()

        if stripped.startswith("```") or stripped.startswith("~~~"):

            marker = stripped[:3]

            if not in_fence:
                in_fence = True
                fence_marker = marker

            elif marker == fence_marker:
                in_fence = False
                fence_marker = None

            output.append(line)
            continue

        if in_fence:
            output.append(line)
            continue

        heading_level = _get_heading_level(
            line
        )

        section_class = _get_section_class(
            line
        )

        if heading_level is not None:

            while (
                open_sections
                and heading_level <= open_sections[-1]
            ):
                output.extend([
                    "",
                    "</section>",
                    "",
                ])

                open_sections.pop()

        if section_class is not None:

            output.extend([
                f'<section class="{section_class}" markdown="1">',
                "",
            ])

            line = _remove_section_marker(
                line
            )

            open_sections.append(
                heading_level
            )

        output.append(line)

    while open_sections:

        output.extend([
            "",
            "</section>",
        ])

        open_sections.pop()

    result = "\n".join(
        output
    )

    if markdown.endswith("\n"):
        result += "\n"

    return result