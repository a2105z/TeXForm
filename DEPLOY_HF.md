# Deploy TeXForm to Hugging Face Spaces (Free)

This guide walks you through deploying TeXForm to Hugging Face Spaces on the **free tier**.

---

## Prerequisites

- A [Hugging Face account](https://huggingface.co/join)
- Git installed
- Your TeXForm code (this repo)

---

## Step 1: Create a new Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in:
   - **Space name:** `texform` (or any name you like)
   - **License:** MIT (or your preference)
   - **SDK:** Select **Docker**
   - **Visibility:** Public (required for free tier)
3. Click **Create Space**

---

## Step 2: Push your code to the Space

From your TeXForm project folder, run:

```powershell
# Add Hugging Face as a remote (replace YOUR_USERNAME with your HF username)
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/texform

# Push to the Space (use 'main' or 'master' depending on your branch)
git push hf main
```

**If you don't have a GitHub repo yet**, you can push directly:

```powershell
cd "c:\Users\aarav\OneDrive\Desktop\Personal Projects\Software Products\TeXform"

git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/texform
git push hf main
```

**First-time push:** Hugging Face may ask for your credentials. Use a [HF Access Token](https://huggingface.co/settings/tokens) as the password if needed.

---

## Step 3: Wait for the build

- Hugging Face will build your Docker image (first build can take **10–20 minutes**)
- Watch the build logs in your Space's **Logs** tab
- When it says "Your Space is running", you're done

---

## Step 4: Use your Space

Your app will be live at:

```
https://huggingface.co/spaces/YOUR_USERNAME/texform
```

Upload a PDF or image, click **Convert to LaTeX**, and download the result.

---

## Optional: Add MathPix (paid math recognition)

If you have a MathPix API subscription:

1. Open your Space on Hugging Face
2. Click **Settings** (gear icon)
3. Go to **Variables and secrets**
4. Add:
   - `MATHPIX_APP_ID` = your app ID
   - `MATHPIX_APP_KEY` = your app key
5. The Space will restart with MathPix enabled

Without MathPix, TeXForm uses **Pix2Text** (free, offline) for math recognition.

---

## What to expect on the free tier

| Aspect | Details |
|--------|---------|
| **Speed** | CPU-only; processing may take 30–90 seconds per page |
| **Sleep** | Space sleeps after 48 hours of inactivity; first visit after that may take ~1 minute to wake |
| **File size** | Keep uploads under 50 MB |
| **Cost** | Free |

---

## Troubleshooting

- **Build fails:** Check the Logs tab for errors. Common issues: out-of-memory during build, or missing files.
- **"Backend not reachable":** The Space may still be starting. Wait 1–2 minutes and refresh.
- **Slow processing:** Normal on CPU. Try smaller images or fewer pages.
