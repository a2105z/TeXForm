# Push TeXform to Software-Engineering-Projects

Follow these steps to add TeXform to your repo:  
**https://github.com/a2105z/Software-Engineering-Projects**

---

## 1. Clone your Software-Engineering-Projects repo (if you don’t have it yet)

Open PowerShell and run:

```powershell
cd "c:\Users\aarav\OneDrive\Desktop\Personal Projects"
git clone https://github.com/a2105z/Software-Engineering-Projects.git
cd Software-Engineering-Projects
```

If you already have it cloned somewhere, just `cd` into that folder instead.

---

## 2. Copy TeXform in as a folder (without its own `.git`)

From inside **Software-Engineering-Projects**, run:

```powershell
# Create TeXform folder and copy contents, excluding .git
robocopy "..\TeXform" ".\TeXform" /E /XD .git /NFL /NDL /NJH /NJS
```

If `robocopy` prompts about “Destination Directory”, type **D** (directory) and press Enter.

**Alternative (manual):**  
- Create a folder named `TeXform` inside `Software-Engineering-Projects`.  
- Copy everything from your current TeXform project into it **except** the `.git` folder (if present).

---

## 3. Commit and push

Still inside **Software-Engineering-Projects**:

```powershell
git add TeXform
git status
git commit -m "Add TeXform: handwritten notes to LaTeX (React + FastAPI, TrOCR)"
git push origin main
```

Use `master` instead of `main` if that’s your default branch.

---

## 4. Optional: hide secrets

If `config/secrets.yaml` has real API keys, don’t push it. Either:

- Remove it from the copied folder before `git add`, or  
- Add `config/secrets.yaml` to `.gitignore` in the TeXform folder and run:

  ```powershell
  git rm --cached TeXform/config/secrets.yaml
  git commit -m "Stop tracking TeXform secrets"
  git push origin main
  ```

---

After this, TeXform will appear at:  
**https://github.com/a2105z/Software-Engineering-Projects/tree/main/TeXform**
