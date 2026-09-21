<div align="center">

# 📄 Resume Studio

**A modern, ATS-optimized single-page resume studio with real-time live preview, in-browser editor, and instant export to Print-Ready HTML & Overleaf LaTeX.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)]()
[![ATS Friendly](https://img.shields.io/badge/ATS-Optimized-success.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange.svg)]()

[Live Studio](#-quick-start) • [Features](#-features) • [How to Edit](#-how-to-customize) • [PDF Export](#-exporting-to-pdf-1-page-fit) • [Overleaf / LaTeX](#-using-with-overleaf-latex)

</div>

---

## 🌟 Why Resume Studio?

Traditional resume builders lock your data in proprietary formats, while LaTeX templates often take hours of debugging and package management. 

**Resume Studio** gives you the best of both worlds:
- **Separation of Content & Styling:** Keep your resume data in clean, structured `resume_data.json` or edit `resume.html` directly.
- **Dual Engine Output:** One click compiles your resume into both a pixel-perfect **A4 1-Page HTML Resume** and an **Overleaf-Ready LaTeX (`.tex`) document**.
- **Interactive Local Studio:** Includes a zero-dependency local web studio with live hot-reloading, zoom controls, 1-page fit measurement, and an in-browser code drawer.
- **100% Zero External Dependencies:** Built purely using Python's standard library. No `pip install` required.

---

## 🚀 Quick Start

### 1. Launch the Interactive Web Studio (Recommended)
Launch the studio server with real-time live sync, zoom controls, and instant PDF printing:
```bash
python generate.py --ui
```
*or run directly:*
```bash
python app.py
```
Open **[http://localhost:5050](http://localhost:5050)** in your browser. Any edits made to `resume_data.json` or `resume.html` will instantly hot-reload the preview in real-time.

### 2. Generate HTML & LaTeX via CLI
Compile both `resume.html` and `resume.tex` directly from your terminal:
```bash
python generate.py
```

### 3. Generate & Open HTML in Default Browser
```bash
python generate.py --open
```

---

## ✨ Features

- ⚡ **Sub-Second Live Reload:** Built-in MD5 content watcher automatically detects file changes on disk and reloads the preview in under 500ms.
- 📐 **1-Page A4 Fit Inspector:** Real-time height measurement dynamically validates whether your resume perfectly fits a single A4 page.
- 🖨️ **Print & PDF Perfection:** Pre-configured `@media print` CSS rules ensure crisp typography, exact margins, and no awkward page breaks.
- 📜 **Overleaf-Ready LaTeX:** Automatically converts HTML formatting (bold, italics, special characters) into clean, standard LaTeX syntax (`.tex`).
- 🎨 **In-Browser Side Drawer:** Edit your structured JSON data or raw HTML directly inside the web studio.
- 🔒 **Privacy-First:** 100% offline and local. Your personal information never leaves your machine.

---

## 📁 Repository Structure

```text
resume-studio/
│
├── app.py             # 🚀 Live Web Studio server (zero-dependency, live reload, PDF export)
├── generate.py        # ⚙️ Python compiler (compiles JSON into HTML & LaTeX)
├── resume_data.json   # ✏️ Structured resume content (profile, skills, experience, etc.)
├── resume.html        # 🌐 1-Page print-ready HTML file (browser preview)
├── resume.tex         # 📜 Overleaf-compatible LaTeX template file
├── README.md          # 📖 Documentation
└── .gitignore         # 🚫 Git rules for clean version control
```

---

## ✏️ How to Customize

You can customize your resume in **three easy ways**:

### Option A: Using the Live Web Studio (Easiest)
1. Run `python generate.py --ui` and open `http://localhost:5050`.
2. Click **"Edit & Code"** in the top bar to open the side drawer.
3. Edit your data under `resume.html` or `resume_data.json` and click **Save**.
4. The canvas will immediately reflect your updates.

### Option B: Editing `resume_data.json` (Structured Data)
Open **`resume_data.json`** in your favorite text editor:
1. **Personal Information:** Update `name`, `phone`, `email`, `location`, `linkedin`, and `github`.
2. **Profile Summary:** Write a 2–3 sentence high-impact summary.
3. **Skills:** Add or rename skill categories dynamically (`languages`, `frameworks`, `cloud_devops`, etc.).
4. **Work Experience & Projects:** Add achievements using action verbs and measurable metrics (e.g., *“Reduced latency by 40%”*).
5. Run `python generate.py` to compile both HTML and LaTeX.

### Option C: Directly Editing `resume.html`
You can also directly edit `resume.html` if you want full control over HTML and CSS styling. The Web Studio will monitor your changes and hot-reload automatically whenever you save.

---

## 🖨️ Exporting to PDF (1-Page Fit)

1. In the Web Studio, click **"Print / Save PDF"** (or open `resume.html` in Chrome/Edge and press `Ctrl + P` / `Cmd + P`).
2. Set **Destination** to **`Save as PDF`**.
3. In **More Settings**:
   - **Paper size:** `A4`
   - **Margins:** `Default` *(all margins are mathematically calibrated in CSS)*
   - **Options:** **UNCHECK** `Headers and footers` *(hides URL, page numbers, and dates)*
   - **Background graphics:** **Checked** (optional)
4. Click **Save**.

---

## 🌐 Using with Overleaf (LaTeX)

If you prefer submitting a LaTeX-generated PDF or need an Overleaf project:
1. Open `resume.tex` and copy all code.
2. Go to [Overleaf.com](https://www.overleaf.com) $\rightarrow$ **New Project** $\rightarrow$ **Blank Project**.
3. Paste the contents into `main.tex` and click **Recompile**.
4. Download your compiled PDF directly from Overleaf.

---

## 💡 ATS Optimization Best Practices

- **Keep it to 1 Page:** Recruiters and hiring managers spend an average of 6 seconds reviewing a resume.
- **Quantify Impact:** Use metrics (`%`, `$`, time saved, users served) in bullet points:
  - *Weak:* "Helped build backend APIs."
  - *Strong:* "Architected scalable backend microservices, reducing API latency by **45%** across 1M+ daily requests."
- **Standard Section Headers:** Resume Studio uses universal section headers (`Professional Experience`, `Technical Skills`, `Education`) recognized by all major Applicant Tracking Systems (Workday, Greenhouse, Lever).

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">

⭐ **If you find Resume Studio useful, please consider giving it a star on GitHub!** ⭐

</div>
