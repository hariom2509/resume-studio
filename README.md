# 📄 Resume Creator

A clean, modular, ATS-optimized Resume Management System & Template for Software Engineers and Tech Professionals.

Easily update your resume data in JSON format and automatically compile it into both a **1-Page Print-Ready HTML Resume** and **Overleaf-Ready LaTeX Source Code (`.tex`)**.

---

## 🚀 Quick Start

### 1. Launch Interactive Web Studio (Recommended)
Run the web studio with live preview, zoom controls, 1-page fit inspector, and PDF export:
```bash
python generate.py --ui
# or
python app.py
```

### 2. Generate Resume (HTML & LaTeX)
Run the generator script in your terminal:
```bash
python generate.py
```

### 3. Generate and Open HTML Directly
```bash
python generate.py --open
```

---

## 📁 Repository Structure

```text
resume-creator/
│
├── app.py             # 🚀 Live Web Studio server (live reload, A4 inspection, PDF export)
├── resume_data.json   # ✏️ Edit your profile, skills, jobs, bullets, and projects here
├── generate.py        # ⚙️ Script that compiles JSON into HTML & LaTeX
├── resume.html        # 🌐 1-Page print-ready HTML file (browser preview)
├── resume.tex         # 📜 Overleaf / LaTeX template file
├── README.md          # 📖 Instructions & documentation
└── .gitignore         # 🚫 Standard git ignore rules
```

---

## ✏️ How to Edit Your Resume

You don't have to touch messy HTML or LaTeX code! Simply open **`resume_data.json`** in VS Code or any text editor:

1. **Update Profile & Summary:**
   Edit the `"personal"` or `"summary"` fields.
2. **Add or Modify Skills:**
   Edit the `"skills"` object (`generative_ai`, `backend_apis`, `cloud_devops`, etc.).
3. **Update Work Experience / Projects:**
   Add new projects, update metrics, or modify bullet points in `"experience"` or `"projects"`.
4. **Re-generate:**
   Run `python generate.py` to update both `resume.html` and `resume.tex` instantly.

---

## 🖨️ How to Export to PDF (1-Page Fit)

1. Open `resume.html` in **Google Chrome** or **Microsoft Edge** (or run `python generate.py --open`).
2. Press **`Ctrl + P`** (or `Cmd + P` on Mac).
3. Set **Destination** to **`Save as PDF`**.
4. In **More Settings**:
   - **Paper size:** `A4` or `Letter`
   - **Margins:** `Default` or `None`
   - **Headers and footers:** **UNCHECK** (to hide date and page title)
5. Click **Save**.

---

## 🌐 Using with Overleaf (LaTeX)
If you prefer LaTeX:
1. Copy the contents of `resume.tex`.
2. Open [Overleaf.com](https://www.overleaf.com) $\rightarrow$ New Project $\rightarrow$ Blank Project.
3. Paste the code into `main.tex` and click **Recompile**.
