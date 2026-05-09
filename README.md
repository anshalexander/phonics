# Phonics Playground

A self-contained interactive phonics learning artifact for kids aged 3–6.
Single HTML file + audio. Works offline once loaded.

## What it teaches

10 lessons aligned with UK Letters & Sounds Phase 1–3 + the
Science-of-Reading consensus:

1. Listen & Rhyme — hearing sound patterns
2. First Sounds: s, a, t, p
3. More Sounds: i, n, m, d
4. Building Words (CVC blending)
5. More Sounds: g, o, c, k
6. Find the First Sound (phoneme isolation game)
7. More Sounds: ck, e, u, r, h, b, f, l
8. Tricky Words (sight words)
9. More Sounds: j, v, w, x, y, z, qu
10. Two Letters, One Sound — sh, ch, th, ng

## How the audio works

- **Phonemes** (`audio/<letter>.mp3`) — real-voice recordings of each
  letter sound, recorded by the parent via `record_phonemes.py` so the
  kid hears their own family teacher. Recordings replace the Aria-TTS
  fallback that ships in the repo as a placeholder.
- **Words** (`audio/word_<word>.{mp3,wav}`) — Microsoft Aria neural TTS
  via `edge-tts` (free, no API key). Carrier-trimmed to single words.
- **Phrases** (`audio/p_<key>.mp3`) — system prompts ("Welcome!",
  "Listen!", etc.), Aria neural.

The HTML uses a tiered fallback: real-voice recording → real-voice TTS
file → Web Audio formant synth (last resort).

## Quick start (local)

```bash
# Option A: Python (default)
./start.command       # serves at http://localhost:8765

# Option B: Docker (production-like, matches Vercel)
docker compose up --build

# Option C: open the file directly
open SATPIN_StoryMode.html  # works but audio probe is slower under file://
```

## Re-recording your own phonemes

```bash
python3 record_phonemes.py
```

Walks you through each phoneme with an Alphablocks-style cue. ~3 minutes
total for all 32. Recordings save to `audio/<letter>.mp3` and replace
the Aria placeholder. Re-run with `--redo` to redo all, or
`rm audio/.recorded_<letter>` to redo a single one.

## Regenerating the TTS audio (Aria fallback)

```bash
pip3 install edge-tts librosa scipy openai-whisper
python3 generate_voices.py
```

Generates 32 phoneme files + 70+ word files + 17 phrase prompts. Uses
Whisper word-level timestamps to extract single-word audio cleanly from
carrier sentences.

## Deploying

See [DEPLOYMENT.md](DEPLOYMENT.md). TL;DR:

```bash
vercel --prod                  # public CDN, free
# OR
docker compose up              # self-host
```

## Project structure

```
.
├── SATPIN_StoryMode.html      # the app — single file, ~74 KB
├── audio/                     # ~150 audio files (~3 MB)
│   ├── <letter>.mp3           # phonemes (your recordings)
│   ├── word_<word>.{mp3,wav}  # word audio
│   └── p_<key>.mp3            # phrase prompts
├── generate_voices.py         # TTS audio generator (edge-tts + Whisper trim)
├── record_phonemes.py         # interactive recorder for parent's voice
├── start.command              # local dev launcher
├── Dockerfile + nginx.conf    # container build
├── docker-compose.yml         # one-command local dev
├── vercel.json                # Vercel deploy config
├── DEPLOYMENT.md              # full deploy instructions
├── PHONICS_AUDIT.md           # per-lesson click-by-click audit
└── Phonics_Syllabus_Research.md  # research grounding
```

## Architecture notes

- **Audio bus** — all playback goes through `AudioBus` so a new sound
  cancels in-flight audio. Prevents double-voice when kids tap fast.
- **Phoneme module** — has both real-audio playback AND a Web Audio
  formant synth fallback (with playFricative / playVowel / playPlosive /
  playNasal recipes per letter). The synth never gets used in practice
  if the audio files are present.
- **Speech module** — for whole-word and phrase audio. Probes file
  existence at startup with sight-word-aware extension order to avoid
  404 spam in the console.
- **Recorder module** — in-browser mic recording per letter card.
  Used during development and as a kid-friendly retry feature.
