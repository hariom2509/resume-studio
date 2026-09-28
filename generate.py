#!/usr/bin/env python3
"""
Resume Creator & Generator
Author: Hari Om
Description: Reads `resume_data.json` and renders both `resume.html` and `resume.tex`.
Usage:
    python generate.py          # Builds resume.html and resume.tex
    python generate.py --open   # Builds and opens resume.html in default browser
"""

import json
import os
import re
import sys
import webbrowser
import argparse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(CURRENT_DIR, "resume_data.json")
HTML_OUT = os.path.join(CURRENT_DIR, "resume.html")
TEX_OUT = os.path.join(CURRENT_DIR, "resume.tex")


def load_data():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found!")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def strip_html_tags(text):
    return re.sub(r"<[^>]+>", "", text)


def html_to_latex(text):
    """Converts common HTML formatting like <strong> to LaTeX equivalent."""
    text = re.sub(r"<strong>(.*?)</strong>", r"\\textbf{\1}", text)
    text = re.sub(r"<b>(.*?)</b>", r"\\textbf{\1}", text)
    text = re.sub(r"<em>(.*?)</em>", r"\\textit{\1}", text)
    text = re.sub(r"<i>(.*?)</i>", r"\\textit{\1}", text)
    text = text.replace("\\&", "&").replace("&amp;", "&").replace("&", "\\&")
    text = text.replace("\\%", "%").replace("%", "\\%")
    text = text.replace("\\$", "$").replace("$", "\\$")
    text = text.replace("\\_", "_").replace("_", "\\_")
    text = text.replace("–", "--")
    text = text.replace("—", "---")
    return text


def build_html(data):
    p = data.get("personal", {})
    skills = data.get("skills", {})
    
    # Render Contact Info
    contact_parts = []
    if p.get("phone"):
        contact_parts.append(f'<a href="tel:{p["phone"]}">{p["phone"]}</a>')
    if p.get("location"):
        contact_parts.append(f'<span>{p["location"]}</span>')
    if p.get("email"):
        contact_parts.append(f'<a href="mailto:{p["email"]}">{p["email"]}</a>')
    if p.get("linkedin"):
        l_url = p["linkedin"] if p["linkedin"].startswith("http") else f"https://{p['linkedin']}"
        contact_parts.append(f'<a href="{l_url}" target="_blank">LinkedIn</a>')
    if p.get("github"):
        g_url = p["github"] if p["github"].startswith("http") else f"https://{p['github']}"
        contact_parts.append(f'<a href="{g_url}" target="_blank">GitHub</a>')
    contact_html = ' <span class="sep">|</span> '.join(contact_parts)

    # Render Experience
    exp_html = ""
    for exp in data.get("experience", []):
        exp_html += f"""
    <div class="row-between">
      <span class="company-name">{exp.get('company', '')}</span>
      <span class="date-range">{exp.get('date', '')}</span>
    </div>
    <div class="role-title">{exp.get('role', '')}</div>
"""
        if exp.get("bullets"):
            exp_html += "    <ul>\n"
            for bullet in exp.get("bullets", []):
                exp_html += f"      <li>{bullet}</li>\n"
            exp_html += "    </ul>\n"
        for proj in exp.get("projects", []):
            if proj.get("name"):
                exp_html += f"""    <div class="project-heading">{proj['name']}</div>\n"""
            exp_html += "    <ul>\n"
            for bullet in proj.get("bullets", []):
                exp_html += f"      <li>{bullet}</li>\n"
            exp_html += "    </ul>\n"

    # Render Standalone Projects
    proj_html = ""
    for proj in data.get("projects", []):
        proj_html += f"""
    <div class="project-heading" style="margin-top: 1px;">{proj.get('name', '')}</div>
    <ul>
"""
        for bullet in proj.get("bullets", []):
            proj_html += f"      <li>{bullet}</li>\n"
        proj_html += "    </ul>\n"

    proj_section_html = ""
    if data.get("projects"):
        proj_section_html = f"""
  <!-- Projects -->
  <div class="section">
    <div class="section-title">PROJECTS</div>
{proj_html}  </div>
"""

    # Render Education
    edu_html = ""
    for edu in data.get("education", []):
        edu_html += f"""
    <div class="edu-row">
      <span class="edu-school">{edu.get('institution', '')}</span>
      <span class="edu-location">{edu.get('location', '')}</span>
    </div>
    <div class="edu-row">
      <span class="edu-degree">{edu.get('degree', '')}</span>
      <span class="edu-years">{edu.get('period', '')}</span>
    </div>
"""

    # Render Certifications
    cert_html = "    <ul>\n"
    for cert in data.get("certifications", []):
        cert_html += f"      <li>{cert}</li>\n"
    cert_html += "    </ul>\n"

    # Render Skills
    skills_html = ""
    for cat, items in skills.items():
        cat_display = cat
        if not any(c.isupper() for c in cat_display):
            cat_display = cat_display.replace("_", " ").title()
        elif "_" in cat_display and " " not in cat_display:
            cat_display = cat_display.replace("_", " ").title()
        cat_escaped = cat_display.replace("&", "&amp;")
        if isinstance(items, list):
            items_str = ", ".join(str(x) for x in items)
        else:
            items_str = str(items)
        items_escaped = items_str.replace("&", "&amp;")
        skills_html += f"""    <div class="skill-group">
      <span class="skill-label">{cat_escaped}:</span> {items_escaped}
    </div>\n"""

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{p.get('name', 'Resume')} - Resume</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
  @page {{
    size: A4;
    margin: 10mm 14mm 8mm 14mm;
  }}

  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  body {{
    font-family: 'Lora', 'Times New Roman', 'Latin Modern Roman', Times, serif;
    font-size: 8.8pt;
    line-height: 1.25;
    color: #000;
    background: #fff;
    -webkit-font-smoothing: antialiased;
  }}

  .resume-container {{
    max-width: 210mm;
    margin: 0 auto;
    padding: 8mm 14mm 6mm 14mm;
  }}

  /* Header */
  .header {{
    text-align: center;
    margin-bottom: 5px;
  }}

  .name {{
    font-size: 22pt;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #000;
    margin-bottom: 2px;
  }}

  .contact-info {{
    font-size: 8.5pt;
    color: #004f9e;
  }}

  .contact-info a {{
    color: #004f9e;
    text-decoration: underline;
  }}

  .contact-info a:hover {{
    color: #002b5c;
  }}

  .contact-info span.sep {{
    color: #004f9e;
    margin: 0 1px;
    text-decoration: none;
    display: inline-block;
  }}

  /* Section Styles */
  .section {{
    margin-top: 4px;
    margin-bottom: 2px;
  }}

  .section-title {{
    font-size: 10.5pt;
    font-weight: 700;
    color: #000;
    border-bottom: 0.8pt solid #000;
    padding-bottom: 1px;
    margin-bottom: 3px;
    text-transform: none;
  }}

  .section-title.uppercase {{
    text-transform: uppercase;
  }}

  /* Content */
  p, .text-block {{
    font-size: 8.6pt;
    text-align: justify;
    line-height: 1.25;
    margin-bottom: 2px;
  }}

  /* Skills */
  .skill-group {{
    font-size: 8.5pt;
    line-height: 1.24;
    margin-bottom: 1.5px;
    text-align: justify;
  }}

  .skill-label {{
    font-weight: 700;
  }}

  /* Split Row */
  .row-between {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 8.8pt;
  }}

  .company-name {{
    font-weight: 700;
    color: #000;
  }}

  .date-range {{
    font-weight: 700;
    color: #000;
    white-space: nowrap;
  }}

  .role-title {{
    font-style: italic;
    font-weight: 600;
    font-size: 8.6pt;
    margin-bottom: 1px;
  }}

  .project-heading {{
    font-weight: 700;
    font-size: 8.6pt;
    margin-top: 2.5px;
    margin-bottom: 1px;
  }}

  /* Bullet Lists */
  ul {{
    margin: 0;
    padding-left: 14px;
    list-style-type: disc;
  }}

  li {{
    font-size: 8.4pt;
    line-height: 1.23;
    margin-bottom: 1.5px;
    text-align: justify;
  }}

  li strong {{
    font-weight: 700;
  }}

  /* Education */
  .edu-row {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 8.8pt;
  }}

  .edu-school {{
    font-weight: 700;
  }}

  .edu-location {{
    font-weight: 700;
    white-space: nowrap;
  }}

  .edu-degree {{
    font-style: italic;
    font-size: 8.6pt;
  }}

  .edu-years {{
    font-style: italic;
    white-space: nowrap;
    font-size: 8.6pt;
  }}

  @media print {{
    body {{
      background: #fff;
    }}
    .resume-container {{
      padding: 0;
      width: 100%;
    }}
    .contact-info a {{
      color: #004f9e !important;
      text-decoration: underline !important;
    }}
  }}
</style>
</head>
<body>

<div class="resume-container">

  <!-- Header -->
  <div class="header">
    <div class="name">{p.get('name', 'Resume')}</div>
    <div class="contact-info">
      {contact_html}
    </div>
  </div>

  <!-- Profile Summary -->
  <div class="section">
    <div class="section-title">PROFILE SUMMARY</div>
    <p>
      {data.get('summary', '')}
    </p>
  </div>

  <!-- Technical Skills -->
  <div class="section">
    <div class="section-title">TECHNICAL SKILLS</div>
{skills_html}  </div>

  <!-- Professional Experience -->
  <div class="section">
    <div class="section-title">PROFESSIONAL EXPERIENCE</div>
{exp_html}  </div>
{proj_section_html}

  <!-- Education -->
  <div class="section">
    <div class="section-title">EDUCATION</div>
{edu_html}
  </div>

  <!-- Certifications & Awards -->
  <div class="section">
    <div class="section-title">CERTIFICATIONS &amp; AWARDS</div>
{cert_html}
  </div>

</div>

</body>
</html>
"""
    return html_template


def build_tex(data):
    p = data.get("personal", {})
    skills = data.get("skills", {})

    contact_tex_parts = []
    if p.get("phone"):
        contact_tex_parts.append(html_to_latex(p["phone"]))
    if p.get("location"):
        contact_tex_parts.append(html_to_latex(p["location"]))
    if p.get("email"):
        contact_tex_parts.append(f'\\href{{mailto:{p["email"]}}}{{\\color{{NavyBlue}}{html_to_latex(p["email"])}}}')
    if p.get("linkedin"):
        l_url = p["linkedin"] if p["linkedin"].startswith("http") else f"https://{p['linkedin']}"
        contact_tex_parts.append(f'\\href{{{l_url}}}{{\\color{{NavyBlue}}LinkedIn}}')
    if p.get("github"):
        g_url = p["github"] if p["github"].startswith("http") else f"https://{p['github']}"
        contact_tex_parts.append(f'\\href{{{g_url}}}{{\\color{{NavyBlue}}GitHub}}')
    contact_tex = ' \\ $|$ \\ '.join(contact_tex_parts)

    # Render Experience
    exp_tex = ""
    for exp in data.get("experience", []):
        exp_tex += f"""
    \\resumeSubheading
      {{{html_to_latex(exp.get('company', ''))}}}{{{html_to_latex(exp.get('date', ''))}}}
      {{{html_to_latex(exp.get('role', ''))}}}{{}}
"""
        if exp.get("bullets"):
            exp_tex += "    \\resumeItemListStart\n"
            for bullet in exp.get("bullets", []):
                exp_tex += f"      \\resumeItem{{{html_to_latex(bullet)}}}\n"
            exp_tex += "    \\resumeItemListEnd\n"
        for proj in exp.get("projects", []):
            if proj.get("name"):
                exp_tex += f"""
    \\vspace{{2pt}}
    \\textbf{{\\small {html_to_latex(proj['name'])}}}
"""
            exp_tex += "    \\resumeItemListStart\n"
            for bullet in proj.get("bullets", []):
                exp_tex += f"      \\resumeItem{{{html_to_latex(bullet)}}}\n"
            exp_tex += "    \\resumeItemListEnd\n"

    # Render Standalone Projects
    proj_tex = ""
    for proj in data.get("projects", []):
        proj_tex += f"""
    \\vspace{{1pt}}
    \\textbf{{\\small {html_to_latex(proj.get('name', ''))}}}
    \\resumeItemListStart
"""
        for bullet in proj.get("bullets", []):
            proj_tex += f"      \\resumeItem{{{html_to_latex(bullet)}}}\n"
        proj_tex += "    \\resumeItemListEnd\n"

    proj_section_tex = ""
    if data.get("projects"):
        proj_section_tex = f"""
%-----------PROJECTS-----------
\\section{{PROJECTS}}
  \\resumeSubHeadingListStart
{proj_tex}  \\resumeSubHeadingListEnd
  \\vspace{{-12pt}}
"""

    # Render Education
    edu_tex = ""
    for edu in data.get("education", []):
        edu_tex += f"""
    \\resumeSubheading
      {{{html_to_latex(edu.get('institution', ''))}}}{{{html_to_latex(edu.get('location', ''))}}}
      {{{html_to_latex(edu.get('degree', ''))}}}{{{html_to_latex(edu.get('period', ''))}}}
"""

    # Render Certifications
    cert_tex = ""
    for cert in data.get("certifications", []):
        cert_tex += f"    \\resumeItem{{{html_to_latex(cert)}}}\n"

    # Render Skills
    skills_tex = ""
    for cat, items in skills.items():
        cat_display = cat
        if not any(c.isupper() for c in cat_display):
            cat_display = cat_display.replace("_", " ").title()
        elif "_" in cat_display and " " not in cat_display:
            cat_display = cat_display.replace("_", " ").title()
        if isinstance(items, list):
            items_str = ", ".join(str(x) for x in items)
        else:
            items_str = str(items)
        skills_tex += f"     \\textbf{{{html_to_latex(cat_display)}:}} {html_to_latex(items_str)} \\\\ \\vspace{{1pt}}\n"

    summary_tex = html_to_latex(data.get('summary', ''))

    tex_template = f"""%-------------------------
% Resume in LaTeX
% Author : {p.get('name', 'Resume')}
% Generated via Resume Creator
%------------------------

\\documentclass[letterpaper,10.5pt]{{article}}

\\usepackage{{latexsym}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{titlesec}}
\\usepackage{{marvosym}}
\\usepackage[usenames,dvipsnames]{{color}}
\\usepackage{{verbatim}}
\\usepackage{{enumitem}}
\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage[english]{{babel}}
\\usepackage{{tabularx}}
\\usepackage{{times}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyfoot{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}

% Adjust margins
\\addtolength{{\\oddsidemargin}}{{-0.55in}}
\\addtolength{{\\evensidemargin}}{{-0.55in}}
\\addtolength{{\\textwidth}}{{1.1in}}
\\addtolength{{\\topmargin}}{{-.6in}}
\\addtolength{{\\textheight}}{{1.2in}}

\\urlstyle{{same}}

\\raggedbottom
\\raggedright
\\setlength{{\\tabcolsep}}{{0in}}

% Sections formatting
\\titleformat{{\\section}}{{
  \\vspace{{-5pt}}\\scshape\\raggedright\\large
}}{{}}{{0em}}{{}}[\\color{{black}}\\titlerule \\vspace{{-4pt}}]

% Custom commands
\\newcommand{{\\resumeItem}}[1]{{
  \\item\\small{{
    {{#1 \\vspace{{-2pt}}}}
  }}
}}

\\newcommand{{\\resumeSubheading}}[4]{{
  \\vspace{{-1pt}}\\item
    \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
      \\textbf{{#1}} & #2 \\\\
      \\textit{{\\small#3}} & \\textit{{\\small #4}} \\\\
    \\end{{tabular*}}\\vspace{{-6pt}}
}}

\\newcommand{{\\resumeProjectHeading}}[2]{{
    \\vspace{{-2pt}}\\item
    \\begin{{tabular*}}{{0.97\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
      \\small#1 & #2 \\\\
    \\end{{tabular*}}\\vspace{{-6pt}}
}}

\\newcommand{{\\resumeSubItem}}[1]{{\\resumeItem{{#1}}\\vspace{{-4pt}}}}

\\renewcommand\\labelitemii{{$\\vcenter{{\\hbox{{\\tiny$\\bullet$}}}}$}}

\\newcommand{{\\resumeSubHeadingListStart}}{{\\begin{{itemize}}[leftmargin=0.15in, label={{}}]}}
\\newcommand{{\\resumeSubHeadingListEnd}}{{\\end{{itemize}}}}
\\newcommand{{\\resumeItemListStart}}{{\\begin{{itemize}}[leftmargin=0.15in]}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\vspace{{-4pt}}}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\begin{{document}}

%----------HEADING----------
\\begin{{center}}
    \\textbf{{\\Huge \\scshape {p['name']}}} \\\\ \\vspace{{2pt}}
    \\small \\color{{NavyBlue}} {p['phone']} \\ $|$ \\ {p['location']} \\ $|$ \\ \\href{{mailto:{p['email']}}}{{\\color{{NavyBlue}}{p['email']}}} \\ $|$ \\ \\href{{{p['linkedin']}}}{{\\color{{NavyBlue}}LinkedIn}} \\ $|$ \\ \\href{{{p['github']}}}{{\\color{{NavyBlue}}GitHub}}
\\end{{center}}

%-----------PROFILE SUMMARY-----------
\\section{{PROFILE SUMMARY}}
  \\vspace{{1pt}}
  \\small{{
    {summary_tex}
  }}
  \\vspace{{-2pt}}

%-----------TECHNICAL SKILLS-----------
\\section{{TECHNICAL SKILLS}}
 \\begin{{itemize}}[leftmargin=0.15in, label={{}}]
    \\small{{\\item{{
{skills_tex}    }}}}
 \\end{{itemize}}
 \\vspace{{-14pt}}

%-----------EXPERIENCE-----------
\\section{{PROFESSIONAL EXPERIENCE}}
  \\resumeSubHeadingListStart
{exp_tex}
  \\resumeSubHeadingListEnd
  \\vspace{{-12pt}}

{proj_section_tex}%-----------EDUCATION-----------
\\section{{EDUCATION}}
  \\resumeSubHeadingListStart
{edu_tex}
  \\resumeSubHeadingListEnd
  \\vspace{{-12pt}}

%-----------CERTIFICATIONS & AWARDS-----------
\\section{{CERTIFICATIONS \\& AWARDS}}
 \\begin{{itemize}}[leftmargin=0.15in, label=\\tiny$\\bullet$]
{cert_tex}
 \\end{{itemize}}

%-------------------------------------------
\\end{{document}}
"""
    return tex_template


def main():
    parser = argparse.ArgumentParser(description="Resume Creator & Generator")
    parser.add_argument("--open", action="store_true", help="Open generated HTML in browser")
    parser.add_argument("--ui", "--serve", dest="ui", action="store_true", help="Launch Resume Studio interactive web UI with live reload")
    parser.add_argument("--port", type=int, default=5050, help="Port for the web UI server (default: 5050)")
    args = parser.parse_args()

    print("[*] Loading resume_data.json...")
    data = load_data()

    print("[*] Generating resume.html...")
    if os.path.exists(HTML_OUT):
        import shutil
        shutil.copyfile(HTML_OUT, os.path.join(CURRENT_DIR, "resume.backup.html"))
    html_content = build_html(data)
    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("[*] Generating resume.tex...")
    tex_content = build_tex(data)
    with open(TEX_OUT, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print("[+] Build complete!")
    print(f"    - HTML: {HTML_OUT}")
    print(f"    - LaTeX: {TEX_OUT}")

    if args.ui:
        import app
        app.run_server(port=args.port, open_browser=True)
    elif args.open:
        print("[+] Opening in default browser...")
        webbrowser.open(f"file:///{HTML_OUT.replace(os.sep, '/')}")


if __name__ == "__main__":
    main()
