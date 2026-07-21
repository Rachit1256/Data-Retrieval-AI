# Deploying AskAI Analytics (free tier, no domain needed)

Stack: **GitHub** (source control) → **Render** (backend, free) →
**Vercel** (frontend, free). Total cost: $0/month for personal/demo use.

## 0. Files in this zip

Unzip this over your repo root -- it adds/overwrites exactly 4 files:

```
.gitignore                         (repo root)
render.yaml                        (repo root -- tells Render how to build/run the backend)
frontend/.env.example              (documents the one env var the frontend needs)
frontend/src/services/api.js       (now reads the backend URL from an env var instead of
                                     hardcoding http://127.0.0.1:8000)
```

If your repo doesn't already have `backend/` and `frontend/` as
top-level folders, adjust `rootDir: backend` in `render.yaml` and the
"Root Directory" field in the Vercel step below to match your layout.

## 1. Push to GitHub

If you haven't already:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

**Do this with the `.gitignore` from this zip already in place** (before
your first commit, or run `git rm -r --cached .` after adding it if
you've already committed `venv/`, `node_modules/`, or `.env`). You do
not want your Gemini API key or a 500MB virtualenv in your repo history.

## 2. Deploy the backend on Render

1. Go to [render.com](https://render.com), sign up/log in with GitHub.
2. Click **New +** → **Blueprint**, pick your repo. Render will read
   `render.yaml` automatically and configure the service for you
   (root dir `backend`, build command `pip install -r requirements.txt`,
   start command `uvicorn app:app --host 0.0.0.0 --port $PORT`).
   - If you'd rather set it up by hand instead: **New +** → **Web
     Service** → pick your repo → set **Root Directory** to `backend`,
     **Build Command** to `pip install -r requirements.txt`, **Start
     Command** to `uvicorn app:app --host 0.0.0.0 --port $PORT`.
3. When prompted for `GEMINI_API_KEY`, paste your actual key (this goes
   into Render's dashboard, never into git).
4. Deploy. Once it's live, open the URL Render gives you (something like
   `https://askai-backend.onrender.com`) directly in your browser -- you
   should see `{"message": "AI Spreadsheet Assistant Running"}`. That
   confirms the backend is up.

**Free tier behavior to expect:** the service spins down after ~15
minutes of no traffic, and the first request after that takes 30-60
seconds to wake back up. That's normal for the free plan, not a bug.

## 3. Deploy the frontend on Vercel

1. Go to [vercel.com](https://vercel.com), sign up/log in with GitHub.
2. **Add New** → **Project** → import your repo.
3. Set **Root Directory** to `frontend`. Vercel auto-detects Vite --
   leave the build command/output directory as default (`npm run build`
   / `dist`).
4. Under **Environment Variables**, add:
   - `VITE_API_BASE` = the Render URL from step 2, e.g.
     `https://askai-backend.onrender.com` (no trailing slash).
5. Deploy. You'll get a URL like `https://your-project.vercel.app` --
   that's your shareable demo link.

## 4. Verify end-to-end

Open the Vercel URL, upload a spreadsheet, ask it a question, ask it to
plot a chart. If a chart doesn't render, see troubleshooting below.

## Troubleshooting

**"Network Error" in the browser console / nothing responds to chat.**
Almost always means `VITE_API_BASE` isn't actually reaching the built
frontend. Vite bakes env vars in *at build time*, so if you added or
changed `VITE_API_BASE` in Vercel after the first deploy, you need to
trigger a new deploy (Vercel's dashboard → Deployments → ⋯ → Redeploy) --
just saving the env var isn't enough.

**Uploaded files / chat history disappear after a while.**
Expected on Render's free tier -- its filesystem is ephemeral, so
anything written to disk (`uploads/`, `vector_db/`, `charts/`) and the
in-memory `state.py` data don't survive a redeploy or a restart. For a
personal demo, just re-upload your file when that happens. If you later
need uploads to persist permanently, that's a real infrastructure change
(a Render persistent disk or S3-style object storage, plus a real
database instead of in-memory dicts) -- worth doing before showing this
to real users, not necessary for a demo.

**`pip install -r requirements.txt` fails on Render.**
The requirements file has exact pinned versions (`==`) for everything.
If one specific package fails to find a matching wheel on Render's Linux
build image, loosen just that line (e.g. `numpy==2.4.6` → `numpy>=2.0`)
and push again. Don't preemptively loosen everything -- fix only the
line that actually errors.

**Charts don't render but the chat answers fine.**
Check that `chartUrl()` in `api.js` is producing a full `https://` URL
(open browser devtools → Network tab → look at the failed image
request). If it's still pointing at `127.0.0.1`, `VITE_API_BASE` wasn't
picked up -- see the "Network Error" fix above (redeploy after setting
the env var).

**CORS errors.**
`app.py` already has `allow_origins=["*"]`, so this shouldn't happen out
of the box. If you later lock CORS down to just your Vercel domain,
remember every future Vercel preview URL (from PRs/branches) gets its
own subdomain -- either allow `*.vercel.app` or only lock this down once
you're done actively developing.

## Later, if you outgrow the free tier / want a real domain

- Buy a domain (Namecheap, Cloudflare, etc.), point it at Vercel for the
  frontend (Vercel's dashboard has a one-click "Add Domain" flow) and
  optionally a subdomain like `api.yourdomain.com` at Render.
- Move off in-memory state (`state.py`) to a real database if you want
  data to survive restarts/scale past one instance.
- Render's paid plans add a persistent disk if you want uploaded files
  to survive redeploys without a full database migration.
