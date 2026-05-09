#!/usr/bin/env python3
"""
Generate ALL the Aria neural-voice audio the Phonics Playground uses:
  - 32 phoneme clips    → audio/<letter>.mp3
  - 70+ word clips      → audio/word_<word>.mp3
  - 17 phrase clips     → audio/p_<key>.mp3

Run on your Mac:
  pip3 install edge-tts
  python3 generate_voices.py

Re-run any time. It overwrites existing files.
"""
import asyncio, os, sys
try:
    import edge_tts
except ImportError:
    print("ERROR: edge-tts not installed.\nRun:   pip3 install edge-tts"); sys.exit(1)

VOICE = 'en-US-AriaNeural'
# Phonemes use normal speed: slowdown stretches vowels into wrong qualities
# (/æ/ → /eɪ/, the original 'cat→kate' issue) and makes consonants robotic.
RATE  = '+0%'
PITCH = '+5Hz'

# ---------- 1. PHONEMES (isolated letter sounds) ----------
#
# Teacher-style framing — every card opens with the letter name, then the
# phoneme sound, then 1-2 example words. Like a preschool flashcard:
#   "S says ssss, like snake, like sat."
#
# WHY THE OLD APPROACH FAILED: Just playing 'ssssss. Snake. Sun.' gave
# kids a hiss followed by random words with nothing to anchor what the
# LETTER was. Without "S says..." framing, it sounds like white noise.
#
# Three formats, chosen per phoneme based on what Aria can actually render:
#
# 1. STRETCHABLE phonemes (sustainable consonants, long vowels):
#    "X says <stretched-sound>, like <w1>, like <w2>."
#    Aria handles 'ssssss', 'mmmmm', 'aaaa' as a sustained sound.
#
# 2. PLOSIVES (p, t, b, d, k, c, g, h, j) and SHORT vowels (i, u):
#    "<Letter>, like <w1>. <Letter>, like <w2>."
#    Reason: TTS reads 'puh' as 'POO' and 'kuh' as 'COO'. Isolated stops
#    can't be synthesised — they need a vowel release, and Aria picks the
#    wrong vowel. Real teachers flashcard plosives the same way:
#    "P! Pop! P! Pin!" — the kid abstracts /p/ from same-onset twice.
#
# 3. SPECIAL multi-letter (x, qu, ck, ch, ng): tuned per letter to what
#    Aria actually says cleanly.
PHONEMES = {
    # --- Sustainable consonants — stretched phoneme works inline ---
    's':  'S says ssssss, like snake, like sat.',
    'n':  'N says nnnnnn, like net, like nut.',
    'm':  'M says mmmmmm, like mom, like map.',
    'r':  'R says rrrrr, like run, like red.',
    'l':  'L says llllll, like leg, like log.',
    'f':  'F says fffff, like fun, like fish.',
    'v':  'V says vvvvv, like van, like vet.',
    'z':  'Z says zzzzz, like zip, like buzz.',

    # --- Stretchable digraphs ---
    'sh': 'S H says shhhhh, like ship, like fish.',
    'th': 'T H says thhhh, like thin, like math.',

    # --- Vowels --- long vowels stretch; short ones don't render well so
    # use the letter+example format and let the example words carry the sound.
    'a':  'A says aaaa, like ant, like apple.',     # /æ/
    'e':  'E, like egg. E, like end.',              # /ɛ/ — stretched 'ehhh' renders as /eɪ/, confuses kid
    'o':  'O says ahhh, like on, like dog.',        # /ɒ/
    'i':  'I, like in. I, like it.',                # /ɪ/ — too short to stretch
    'u':  'U, like up. U, like under.',             # /ʌ/ — too short to stretch

    # --- Plosives --- letter + example pattern. NEVER write 'puh'/'kuh':
    # Aria pronounces them as POO/COO (kid hears "PEE POO" — useless).
    'p':  'P, like pop. P, like pin.',
    't':  'T, like top. T, like tap.',
    'b':  'B, like big. B, like bat.',
    'd':  'D, like dog. D, like did.',
    'g':  'G, like go. G, like get.',
    'c':  'C, like cat. C, like cup.',
    'k':  'K, like kit. K, like kick.',
    'h':  'H, like hat. H, like hop.',
    'j':  'J, like jam. J, like jet.',

    # --- Semi-vowels — Aria can render 'wuh'/'yuh' acceptably ---
    'w':  'W says wuh, like win, like web.',
    'y':  'Y says yuh, like yes, like yum.',

    # --- Complex multi-letter — tuned formats ---
    'x':  'X says ks, like box, like fox.',
    # 'Q U says kw' renders as 'Cue You says K W' — kid hears two letter
    # names plus a third sound, very confusing. Letter+example is cleaner.
    'qu': 'Q U, like queen. Q U, like quack.',
    'q':  'Q, like queen. Q always brings U along.',
    'ck': 'C K, like duck. C K, like sock.',        # ck = silent c + /k/
    'ch': 'C H says chuh, like chop, like chin.',
    'ng': 'N G, like ring. N G, like sing.',        # ng can't stretch alone
}

# ---------- 2. WORDS (just say the word, slowly and clearly) ----------
WORDS = sorted(set([
    # rhyme module
    'cat','hat','dog','log','sun','fun','pin','win','big','bed',
    # CVC blend module
    'sat','mat','dim','tap','nap','pat','at','an','in','on',
    # letter card example words
    'ant','it','egg','up','run','jam','van','box','yes','zip',
    'kit','duck','queen','leg','go',
    # first-sound module labels
    'apple','fish','moon','bird','rocket','mug','tree','pig','nest','snake',
    # tricky / sight words
    'the','I','a','to','no','was','my','you','are','all','is',
    # digraph example words
    'ship','shop','chop','chin','rich','thin','math','ring','sing','long',
]))

# ---------- 3. PHRASES (system prompts + transitions) ----------
PHRASES = {
    'welcome':         "Welcome! Pick a lesson to start.",
    'tap_letter':      "Tap any letter to hear its sound.",
    'tap_pair':        "Tap a pair. Do they rhyme?",
    'tap_word':        "Tap a word. We'll sound it out together.",
    'tap_blend':       "Tap each letter to hear its sound.",
    'tiny_words':      "These tiny words show up everywhere. Tap to hear.",
    'two_one':         "Two letters, one sound! Tap any pair.",
    'listen':          "Listen!",
    'which_one':       "Which one?",
    'yes':             "Yes!",
    'try_again':       "Try again!",
    'yes_rhyme':       "Yes! They rhyme!",
    'nope_rhyme':      "Nope, those don't rhyme.",
    'recording_now':   "Recording. Say the sound now.",
    'lesson_done':     "Lesson complete! Great work!",
    'all_found':       "All done! You found every sound!",
    'almost':          "Almost! Let's try again.",
}

def filename_for_word(w):
    safe = ''.join(ch for ch in w.lower() if ch.isalnum() or ch in '_-')
    return f'word_{safe}.mp3'

def filename_for_phrase(key):
    return f'p_{key}.mp3'

async def render(text, fn, outdir, rate=RATE):
    path = os.path.join(outdir, fn)
    try:
        comm = edge_tts.Communicate(text, VOICE, rate=rate, pitch=PITCH)
        await comm.save(path)
    except Exception as e:
        print(f'  err {fn:30}  {e}')
        return False
    return True

_WHISPER_MODEL = None
def _get_whisper():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is not None: return _WHISPER_MODEL
    try:
        import whisper
        _WHISPER_MODEL = whisper.load_model('base.en')
        return _WHISPER_MODEL
    except ImportError:
        return None

def trim_with_whisper(mp3_path, target_word, pad_ms=90):
    """Use Whisper word-level timestamps to extract just `target_word`
    from a carrier sentence ('Now, {w}, please.'). Returns True on success.

    Whisper knows exactly where each word starts and ends, so this avoids
    the failure modes of energy-based segmentation:
      - weak onsets (/p/, /tʃ/) that don't show as RMS peaks
      - weak codas (/k/, /t/, /ks/) that get cut at threshold crossing
      - multi-syllable words ('apple', 'rocket') that split into 2 RMS
        segments and confuse a 'find the middle' picker.
    """
    model = _get_whisper()
    if model is None: return False
    try:
        import librosa, numpy as np, re
        from scipy.io import wavfile
        # Bias Whisper toward recognizing target_word — without this prompt
        # vowel-initial words (ant, egg) get transcribed as common-English
        # neighbors ("and", "egg" → "ed").
        result = model.transcribe(
            mp3_path, word_timestamps=True, fp16=False,
            language='en', temperature=0.0,
            initial_prompt=f"Phonics word: {target_word}.",
        )
        target = target_word.lower().strip()
        # Flatten all words from all segments into a single list so we can
        # peek at the NEXT word's start time. Whisper's word['end'] is
        # unreliable for multi-syllable words ('rocket' ends at "rock"),
        # but the start of the FOLLOWING word ("please") is accurate.
        all_words = [w for seg in result.get('segments', [])
                     for w in seg.get('words', [])]
        # Primary match: exact alphabetic match. Fallback: position-based
        # match — in "Now, X, please." the target is the middle word, even
        # if Whisper transcribed it as a phonetic neighbor.
        target_idx = None
        for i, w in enumerate(all_words):
            w_clean = re.sub(r'[^a-z]', '', w['word'].lower())
            if w_clean == target:
                target_idx = i
                break
        if target_idx is None and len(all_words) == 3:
            cleaned = [re.sub(r'[^a-z]', '', w['word'].lower()) for w in all_words]
            if cleaned[0] == 'now' and cleaned[2] == 'please':
                target_idx = 1
        for i, w in enumerate(all_words):
            if i == target_idx:
                y, sr = librosa.load(mp3_path, sr=22050, mono=True)
                pad = pad_ms / 1000.0
                start_t = w['start'] - pad
                if i + 1 < len(all_words):
                    next_start = all_words[i+1]['start']
                    # End just before the next word begins (30 ms gap so
                    # we don't capture the next word's onset).
                    end_t = next_start - 0.03
                    # Sanity: never let end_t exceed word['end'] + 350 ms
                    # (multi-syllable words shouldn't be longer than that).
                    end_t = min(end_t, w['end'] + 0.35)
                else:
                    end_t = w['end'] + pad
                s = max(0, int(start_t * sr))
                e = min(len(y), int(end_t * sr))
                if e <= s: return False
                seg_audio = y[s:e].copy()
                if len(seg_audio) < sr * 0.1: return False
                fade = int(0.015 * sr)
                if len(seg_audio) > 2 * fade:
                    seg_audio[:fade] *= np.linspace(0, 1, fade)
                    seg_audio[-fade:] *= np.linspace(1, 0, fade)
                wav_path = mp3_path.rsplit('.', 1)[0] + '.wav'
                wavfile.write(wav_path, sr, (seg_audio * 32767).astype(np.int16))
                os.remove(mp3_path)
                return True
        return False
    except Exception as e:
        print(f'    (whisper trim failed: {e})')
        return False

def trim_to_middle_word(mp3_path):
    """Energy-based fallback for when Whisper isn't installed. Finds the
    middle of three RMS-active segments in a carrier 'Now, {w}, please.'
    Less reliable than the Whisper trim — fails on weak phoneme edges
    and multi-syllable words. Use trim_with_whisper when possible."""
    try:
        import librosa, numpy as np
        from scipy.io import wavfile
    except ImportError:
        return False
    try:
        y, sr = librosa.load(mp3_path, sr=22050, mono=True)
        if len(y) < sr * 0.2: return False
        rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0]
        segments = []
        for thresh_mult in [0.18, 0.25, 0.30, 0.35, 0.42]:
            threshold = rms.max() * thresh_mult
            active = rms > threshold
            segs, in_seg, start = [], False, 0
            for i, a in enumerate(active):
                if a and not in_seg: in_seg, start = True, i
                elif not a and in_seg:
                    in_seg = False
                    if i - start >= 4: segs.append((start, i))
            if in_seg and len(active) - start >= 4: segs.append((start, len(active)))
            if len(segs) >= 3:
                segments = segs; break
        if len(segments) < 3: return False
        if len(segments) == 3:
            s_frame, e_frame = segments[1]
        else:
            total = segments[-1][1] - segments[0][0]
            mid_target = segments[0][0] + total * 0.5
            s_frame, e_frame = min(segments, key=lambda s: abs((s[0]+s[1])/2 - mid_target))
        pad = int(0.09 * sr)
        s = max(0, s_frame * 256 - pad)
        e = min(len(y), e_frame * 256 + pad)
        seg_audio = y[s:e].copy()
        if len(seg_audio) < sr * 0.1: return False
        fade = int(0.015 * sr)
        if len(seg_audio) > 2 * fade:
            seg_audio[:fade] *= np.linspace(0, 1, fade)
            seg_audio[-fade:] *= np.linspace(1, 0, fade)
        wav_path = mp3_path.rsplit('.', 1)[0] + '.wav'
        wavfile.write(wav_path, sr, (seg_audio * 32767).astype(np.int16))
        os.remove(mp3_path)
        return True
    except Exception as e:
        print(f'    (trim failed: {e})')
        return False

async def main():
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(here, 'audio')
    os.makedirs(outdir, exist_ok=True)
    print(f'Voice: {VOICE}    Rate: {RATE}    Output: {outdir}')

    print(f'\n[1/3] {len(PHONEMES)} phoneme clips...')
    for L, txt in PHONEMES.items():
        ok = await render(txt, f'{L}.mp3', outdir)
        print(f'  {"ok" if ok else "FAIL"}  {L}.mp3')

    print(f'\n[2/3] {len(WORDS)} word clips...')
    for w in WORDS:
        # FINAL PRONUNCIATION RECIPE — verified acoustically with librosa.
        #
        # Issue we hit: sentence-final words get LENGTHENED by every neural
        # TTS engine (it's a universal English prosody rule). Lengthened /æ/
        # sounds like /eɪ/ — so "It's a cat." sounded like "It's a kate".
        #
        # Fix: keep the word in the MIDDLE of the phrase so it doesn't take
        # final-position stress. Also clip the audio to extract just the
        # target word, so the kid hears ONLY the word, not the carrier.
        #
        # Carrier we use: "Say {w} please."
        #   - "Say"  → primes the listener
        #   - "{w}"  → in mid-position, gets normal (short) duration
        #   - "please" → eats the sentence-final lengthening
        # We then pydub-trim out the carrier words.
        SIGHT_NO_CARRIER = {'i','a','the','to','no','is','was','my','you','are','all','an','at','on','in','it','up','go','so','do','am','as'}
        if w.lower() in SIGHT_NO_CARRIER:
            text = f'{w}.'
            should_trim = False
        else:
            # Commas force ~250 ms pauses between words. Without them Aria
            # blends "Say hat please" into 2 acoustic segments instead of 3,
            # and the trim function can't isolate the target word.
            text = f'Now, {w}, please.'
            should_trim = True
        fn = filename_for_word(w)
        ok = await render(text, fn, outdir, rate='+0%')
        if not ok: continue
        # Trim "Now, {w}, please." down to just the {w} segment.
        # Prefer Whisper word-timestamp trim (robust to weak onsets/codas
        # and multi-syllable words). Fall back to energy-based trim if
        # Whisper isn't installed or fails to locate the word.
        if should_trim:
            mp3_path = os.path.join(outdir, fn)
            trimmed = trim_with_whisper(mp3_path, w)
            if trimmed:
                tag = '[whisper-trim]'
            elif trim_to_middle_word(mp3_path):
                tag = '[energy-trim]'
            else:
                tag = '[full]'
        else:
            tag = '[full]'
        print(f'  ok  {fn:30}  {tag:10} ← "{text}"')

    print(f'\n[3/3] {len(PHRASES)} phrase clips...')
    for key, txt in PHRASES.items():
        ok = await render(txt, filename_for_phrase(key), outdir)
        if ok: print(f'  ok  {filename_for_phrase(key):30}  ← "{txt}"')

    print('\nDone! Reload the artifact in your browser.')
    print('You should now hear Aria everywhere — letters, words, AND prompts.')

    # Auto-run an acoustic verification on a few critical words.
    print('\n--- VERIFICATION (acoustic) ---')
    try:
        import librosa, numpy as np
        # Vowel F1 ranges (Hz, child/female pitch)
        EXPECT = {
            'cat': ('æ', 660, 900), 'hat': ('æ', 660, 900),
            'sat': ('æ', 660, 900), 'pin': ('ɪ', 350, 550),
            'dog': ('ɒ', 500, 700), 'sun': ('ʌ', 580, 750),
            'big': ('ɪ', 350, 550),
        }
        for w, (ipa, lo, hi) in EXPECT.items():
            p = os.path.join(outdir, filename_for_word(w))
            if not os.path.exists(p): continue
            y, sr = librosa.load(p, sr=22050, mono=True)
            y_t, _ = librosa.effects.trim(y, top_db=25)
            rms = librosa.feature.rms(y=y_t, frame_length=1024, hop_length=256)[0]
            if len(rms) < 5: continue
            # Find the LAST high-energy region — that's the target word
            # because "Say {w} please" puts {w} in the middle and "please"
            # is unstressed, so {w} usually has the highest local RMS.
            peak = int(np.argmax(rms))
            half = int(0.06 * sr / 256)
            seg = y_t[max(0,peak-half)*256:min(len(rms),peak+half)*256]
            if len(seg) < sr*0.04: continue
            try:
                a = librosa.lpc(librosa.effects.preemphasis(seg), order=12)
                roots = np.roots(a); roots = roots[np.imag(roots)>=0]
                freqs = sorted(np.arctan2(np.imag(roots), np.real(roots))*sr/(2*np.pi))
                f1 = next((f for f in freqs if 90<f<4000), None)
            except Exception:
                f1 = None
            ok = f1 is not None and lo <= f1 <= hi
            mark = '✓' if ok else '?'
            f1str = f'{f1:.0f}Hz' if f1 else '---'
            print(f'  {mark} {w:6}  vowel /{ipa}/  F1={f1str:10} (expect {lo}-{hi})')
        print('\nIf any are marked "?", listen to that file and tell Claude.')
    except Exception as e:
        print(f'(verification skipped: {e})')

if __name__ == '__main__':
    asyncio.run(main())
