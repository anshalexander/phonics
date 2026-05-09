# Phonics Playground — project handoff for Claude Code

## What this project is

A self-contained phonics learning artifact for ages 3–6, built as a single
HTML file (`SATPIN_StoryMode.html`) plus supporting research docs and a
neural-voice audio generation script. The user is **Anshul**. Original goal:
research how to teach phonics to kids, then build an interactive site with
real AI voice that explains phonics playfully.

## Project state when you (Claude Code) take over

**The big unsolved problem: audio quality.** I (the Cowork-mode agent that
built this) was running in a network-locked sandbox and could not:
- run `edge-tts` (DNS blocked to Microsoft's TTS endpoint)
- install Whisper for transcription verification (PyTorch wheels blocked)
- play audio to actually hear what was generated
- reach HuggingFace for any other ASR model

Anshul has been running the audio generation manually on his Mac. He's
frustrated because the audio still sounds wrong — specifically:
- "cat" sometimes sounded like "kate" (root cause diagnosed: sentence-final
  vowel lengthening, which is a documented English prosody rule)
- "x" pronounced as letter names "K, S" instead of /ks/
- Inconsistent pronunciations across runs

**You can do what I couldn't.** You can run edge-tts, install whisper,
play audio with `afplay`, install ffmpeg, etc. Use those tools.

## File inventory

Everything lives in this directory:

```
outputs/
├── CLAUDE.md                       ← this file
├── SATPIN_StoryMode.html           ← the main artifact (~1700 lines, single file)
├── SATPIN_Curriculum.docx          ← parent/teacher curriculum doc
├── SATPIN_Deck.pptx                ← parent/teacher slide deck
├── Phonics_Syllabus_Research.md    ← research synthesis (10 modules, citations)
├── SATPIN_phoneme_preview.wav      ← 15s preview of synthesized phonemes
├── generate_voices.py              ← edge-tts neural voice generator
├── start.command                   ← double-click to start local server
└── audio/                          ← generated MP3s + recording instructions
```

## Architecture

### The artifact (`SATPIN_StoryMode.html`)

Single self-contained HTML file. No build step, no node_modules. Has:
- **Cover scene** — title, "Start" button, mascot parade
- **Lesson menu** — 10-card grid, each card opens one module
- **10 lesson scenes** generated from a `MODULES` array — letters,
  rhyming, blending, first-sound game, sight words, digraphs
- **AudioBus** — single source-of-truth that cancels in-flight audio when
  new audio starts (fixes the double-voice bug)
- **Phonemes module** — Web Audio formant synthesis fallback (RECIPES
  dict has playFricative/playVowel/playPlosive/playNasal recipes per letter)
- **Recording feature** — mic icon on every letter card, in-browser recording
- **Speech module** — checks for matching MP3 first, falls back to Web
  Speech API. Strongly excludes male voices (Alex, Daniel, Fred…) on macOS.
- **CSS animations** — slithering snake, twitching mouse, propeller plane,
  etc. All inline SVG with CSS keyframes.

### The 10 modules (research-aligned)

Based on UK Letters and Sounds Phase 1–3 + Reading Rockets Science of
Reading consensus. See `Phonics_Syllabus_Research.md` for full citations.

1. **Listen & Rhyme** — Phase 1 phonological awareness
2. **First Sounds: s, a, t, p** — Phase 2 Set 1
3. **More Sounds: i, n, m, d** — Phase 2 Set 2
4. **Building Words (CVC Blending)** — synthetic phonics
5. **More Sounds: g, o, c, k** — Phase 2 Set 3
6. **Find the First Sound** — phoneme isolation game
7. **More Sounds: ck, e, u, r, h, b, f, l** — Phase 2 Sets 4–5
8. **Tricky Words (Sight Words)** — the, I, to, no, go, was, my, you, are, all
9. **More Sounds: j, v, w, x, y, z, qu** — Phase 3 single letters
10. **Two Letters, One Sound: sh, ch, th, ng** — Phase 3 digraphs

### The audio pipeline

`generate_voices.py` writes three categories of MP3 (and WAV) into `audio/`:

- **Phonemes** (`audio/<letter>.mp3`) — for letter cards. Texts use
  example words instead of letter spellings: `'Box. Fox. Six.'` for X.
- **Words** (`audio/word_<word>.wav`) — for word cards & TTS-fallback.
  Generated using carrier sentence `"Now, {word}, please."` then **trimmed**
  via `trim_to_middle_word()` to extract just the target word. Output is
  ~0.25 sec WAV files.
- **Phrases** (`audio/p_<key>.mp3`) — for system prompts ("Welcome!",
  "Listen!", "Yes!", etc.).

The artifact's `Speech.speak()` looks up text in `PHRASE_KEYS` and
`WORD_LIST` and prefers MP3/WAV over Web Speech API.

### Voice: Microsoft Aria neural via edge-tts

Free, no account, no API key. ~120 audio files generated per run. Runs
from Anshul's Mac (not from this sandbox).

## Open issues you should pick up

### 1. Verify audio quality (HIGH PRIORITY)

Anshul wants confirmation that words actually sound right. **You can install
Whisper and transcribe each generated MP3 to verify pronunciation** —
Cowork-mode-me could not.

Suggested next step:
```bash
pip3 install openai-whisper
python3 -c "
import whisper
model = whisper.load_model('tiny.en')
import os
for f in sorted(os.listdir('audio')):
    if f.startswith('word_') and f.endswith(('.mp3', '.wav')):
        r = model.transcribe(f'audio/{f}')
        print(f, '→', r['text'].strip())
"
```

If a word transcribes wrong, the carrier sentence in `generate_voices.py`
needs adjustment, OR the audio needs deeper trimming.

### 2. Use `afplay` to actually listen (HIGH PRIORITY)

You have audio output. After every change, before declaring success:
```bash
afplay audio/word_cat.mp3
afplay audio/x.mp3
```
Anshul cannot tell what's wrong from text descriptions; you should listen
and confirm yourself before claiming "this is fixed".

### 3. The carrier-trim approach may need refinement

Current `trim_to_middle_word()` uses multi-threshold silence detection.
Test results before user re-ran:
- 9/10 words trim cleanly to 0.20–0.35 sec
- "ant" fails (vowel-initial words have weak segment boundaries)

Possible next steps:
- Try `pydub` + `librosa.effects.split()` instead of hand-rolled threshold
- Use Whisper word-level timestamps (`word_timestamps=True`) to find exact
  word boundaries, then ffmpeg-cut precisely
- For vowel-initial words, generate with a different carrier like
  `"This is, {w}, okay."`

### 4. Anshul said the lessons are "confusing for adults"

Last user message before handoff: *"all you lessons how it is working
it is very confusing for adults only — you need to test it by playing it
yourself and playing the sounds and testing what it is pronouncing and
how it is pronouncing.. then figure out if that even make sense that too
for kids of 3-4 years of age"*

So beyond audio, **the lesson UX may need simplification**:
- 10 lessons might be too many for the target age (3–4)
- Some lesson titles use phonics jargon ("Phase 2 Set 1") in lesson cards
- The blending module (`m4`) is currently tap-to-hear-letters then tap-word;
  was previously drag-and-drop which Anshul said didn't work
- Test with `afplay` and review whether each lesson's audio + visual
  combination would actually make sense to a non-reading 3-year-old

### 5. The "kate" perception issue may persist even after trimming

Even with carrier+trim, the trimmed "cat" (~0.25 sec) should be acoustically
short /æ/. But if Anshul still hears "kate", the problem may be that **the
mid-sentence "cat" inside "Now, cat, please." has rising intonation**
because comma-bounded phrases get question-like contour in some neural
voices. If so, try alternative carriers: `"{word}. Yes, {word}."` or
`"The word is {word}, exactly."`

Worst case, fall back to **OpenAI TTS** (paid, but better at single-word
output) or **ElevenLabs** (has a free tier; supports IPA).

## Constraints

- Anshul is not a developer. Keep instructions to: open Terminal, paste
  command, see result.
- He uses macOS (paths above are his actual paths).
- He says he can sign in to free accounts but won't add a credit card.
- Don't introduce any tool or service that requires payment without
  explicit confirmation first.
- Keep the artifact a single HTML file. No build step.
- All audio must work offline once generated. The artifact is intended to
  be openable as a static file or via the included `start.command` server.

## What I (Cowork-mode) think is the right move next

1. Run the script as-is (`python3 generate_voices.py`)
2. Use `afplay` to listen to 5–10 word files (cat, hat, sat, pin, dog,
   sun, ant, x, sh, ng) — actually listen, don't trust the spec
3. Install whisper, transcribe each, compare to expected
4. For any failures, iterate the carrier sentence and re-test
5. Once audio is solid, do the same for the **lesson UX** —
   open the artifact in your own browser via the `start.command`,
   walk through every lesson, and report any confusing parts to Anshul

The user is patient but tired. Concrete demonstrable progress > theory.

## Useful commands

```bash
# Start local server (the right way to test the artifact)
./start.command

# Regenerate all audio
python3 generate_voices.py

# Listen
afplay audio/word_cat.mp3

# Transcribe (after `pip3 install openai-whisper`)
python3 -c "
import whisper
m = whisper.load_model('tiny.en')
print(m.transcribe('audio/word_cat.mp3')['text'])
"

# Acoustic analysis (formants, duration)
python3 -c "
import librosa, numpy as np
y, sr = librosa.load('audio/word_cat.mp3', sr=22050)
print(f'duration: {len(y)/sr:.2f}s, peak RMS: {librosa.feature.rms(y=y).max():.3f}')
"
```

## Conversation history summary

We iterated through these versions of the audio approach:
1. Web Speech API only → robotic, said "ess" for "s"
2. Web Audio formant synthesis → phonetically correct, robotic
3. edge-tts with `rate='-25%'` slowdown → "cat" sounded like "kate"
   (vowel stretching diagnosed acoustically with librosa)
4. edge-tts with doubled `"cat. cat."` → inconsistent pronunciations
5. edge-tts with carrier `"It's a cat."` → kate effect because cat at
   sentence-final position
6. edge-tts with mid-sentence `"Say cat please."` → most words OK; some
   trimmed cleanly, others failed
7. **Current:** edge-tts with comma-forced pauses `"Now, cat, please."` →
   trim function with multi-threshold silence detection extracts just
   the target word as a ~0.25 sec WAV

Each iteration was acoustically validated with librosa. None were
auditorily validated because I had no audio output. Your turn.
