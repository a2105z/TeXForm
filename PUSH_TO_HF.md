# Push TeXForm to Hugging Face Spaces

Your code is committed and the `hf` remote is configured. You just need to authenticate and push.

---

## Step 1: Create a Hugging Face Access Token

1. Go to **[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)**
2. Click **"Create new token"**
3. Name it (e.g. `texform-push`)
4. Set permission to **Write**
5. Click **Create**
6. **Copy the token** (it starts with `hf_`) — you won't see it again

---

## Step 2: Push to Hugging Face

Open PowerShell in this folder and run:

```powershell
cd "c:\Users\aarav\OneDrive\Desktop\Personal Projects\Software Products\TeXform"
git push hf main
```

When prompted:
- **Username:** `amittal417`
- **Password:** paste your **access token** (not your account password)

---

## Step 3: Wait for the build

- Go to [huggingface.co/spaces/amittal417/texform](https://huggingface.co/spaces/amittal417/texform)
- The first build takes 10–20 minutes
- When it says "Your Space is running", your app is live

---

## Security note

**Never share your access token or account password.** If you shared a password in chat, consider changing it at [huggingface.co/settings/account](https://huggingface.co/settings/account).
