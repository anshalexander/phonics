# Deploying the Phonics Playground

The artifact is a single HTML file plus an `audio/` folder of MP3/WAV files
— pure static. Two ways to serve it:

| Use case | Tool | Command |
|---|---|---|
| Quick local check | Python | `./start.command` |
| Production-like local test (matches Vercel) | Docker | `docker compose up` |
| Public deployment (free, automatic CDN) | Vercel | `vercel deploy` |

---

## Local development with Docker

One command builds and serves on port 8765 (same port `start.command` used,
so existing bookmarks still work):

```bash
docker compose up --build
```

Then open <http://localhost:8765>. The compose file mounts `audio/` and
`SATPIN_StoryMode.html` as **read-only volumes**, so:

- Re-recording phonemes (`python3 record_phonemes.py`) shows up immediately
  on a browser refresh — no rebuild needed.
- Editing the HTML shows up immediately too (with the 5-min cache busted
  via Cmd+Shift+R hard refresh).

### Stop / clean up

```bash
docker compose down              # stop the container
docker compose down --rmi local  # also remove the image
```

### What's in the image

- `nginx:1.27-alpine` (~10 MB base)
- `nginx.conf` with gzip + tiered caching (audio: 1 year immutable; HTML: 5 min)
- Permissions-Policy header so the in-app mic recorder works
- Healthcheck on `/`

Final image is ~14 MB compressed (~80 MB on disk including the audio bundle).

---

## Deploying to Vercel

Vercel hosts static sites for free with their global CDN — perfect for
this artifact (it's all static files, no build step, no backend).

### One-time setup

```bash
npm i -g vercel              # install CLI
vercel login                  # auth (free account, no card needed)
```

### Deploy

```bash
cd <this-folder>
vercel                        # preview deploy → vercel.app URL
vercel --prod                 # production deploy → your project URL
```

`vercel.json` controls:

- **Root redirect**: `/` → `/SATPIN_StoryMode.html`
- **Audio caching**: 1 year immutable (so the CDN serves audio from
  edge cache — kid taps a letter, instant playback worldwide)
- **HTML caching**: 5 min, must-revalidate (your edits propagate quickly)
- **Security headers**: nosniff, frame-options, mic-only-self
  permissions-policy (the artifact records mic for kid voice playback)

### What gets deployed

`.vercelignore` excludes the Python tooling, recording markers, backups,
internal docs, and curriculum files. Only the runtime essentials ship:

- `SATPIN_StoryMode.html`
- `audio/` (all phoneme + word + phrase MP3/WAV files — your voice
  recordings are part of this)
- `vercel.json`

Total deploy size: ~3-4 MB.

### Iterating after deploy

Re-record phonemes locally → `vercel --prod` to push. The audio files
keep the same names, but their content changes. Vercel's `immutable`
cache header would normally hide the change from existing browser
tabs; in practice this only matters for users who already have the page
open. Hard reload (Cmd+Shift+R) bypasses cache for them.

If you want guaranteed cache busting on every deploy, append a query
string to audio URLs in the HTML (e.g., `audio/s.mp3?v=2`) — but this
isn't necessary for the small audience this artifact targets.

---

## Comparison

|   | `start.command` | `docker compose` | Vercel |
|---|---|---|---|
| Setup | None | Docker Desktop | Free Vercel account |
| Behaves like prod | ❌ no cache headers | ✅ matches Vercel | ✅ |
| Public URL | ❌ localhost only | ❌ localhost only | ✅ HTTPS + CDN |
| Mic recording works | ✅ (file://-style) | ✅ | ✅ |
| Survives reboot | ❌ | ✅ (`restart: unless-stopped`) | ✅ |

For just testing on your Mac: `start.command` is fine. To share with
family / put on a tablet: deploy to Vercel.

---

## Checklist before first Vercel deploy

```bash
# 1. Make sure you've recorded all 32 phonemes (or that you're OK with
#    Aria's TTS for any unrecorded letters)
ls audio/.recorded_* | wc -l    # should be ~31

# 2. Make sure the artifact opens locally
open SATPIN_StoryMode.html      # should redirect via local server, OR:
docker compose up               # http://localhost:8765

# 3. Confirm vercel.json is valid JSON
python3 -c "import json; json.load(open('vercel.json'))"

# 4. Deploy a preview first to spot-check on the live URL
vercel
# Vercel prints a preview URL — open it, click around, verify audio plays.

# 5. Once satisfied, push to production
vercel --prod
```
