#!/usr/bin/env python3
"""
Record your own voice for every phoneme + word in the phonics app.

Usage:
  python3 record_phonemes.py

Walks you through each phoneme with an Alphablocks-style cue. For each:
  1. Shows the letter and how to say it
  2. Counts down 3-2-1
  3. Records 2.5 seconds from your default mic
  4. Plays it back so you can hear yourself
  5. Ask: keep, retry, or skip

Files save to audio/<letter>.mp3 — replaces Aria's TTS audio.
You can stop anytime (Ctrl-C) and resume later — finished letters
are skipped on next run unless you pass --redo.
"""
import os, sys, subprocess, time, shutil

# Cue per phoneme — how to say it for an Alphablocks-style result.
# Hold sustainables for ~2 sec; plosives are short bursts.
PHONEMES = [
    ('s',  'Hiss like a snake: "ssssssss" (hold ~2 sec)'),
    ('a',  'Short open mouth: "aaaa" — like the start of "ant"'),
    ('t',  'Quick tongue tap: "t" — short, no vowel after'),
    ('p',  'Quick lip pop: "p" — short, no vowel after'),
    ('i',  'Short smile: "ih" — like in "in"'),
    ('n',  'Hum through nose: "nnnn" (hold ~2 sec)'),
    ('m',  'Lips closed hum: "mmmm" (hold ~2 sec)'),
    ('d',  'Quick tongue tap voiced: "d" — short'),
    ('g',  'Back of throat: "g" — short, like in "go"'),
    ('o',  'Round mouth: "oooo" — like in "on" / "dog"'),
    ('c',  'Same as K — back of throat: "k" — short'),
    ('k',  'Back of throat: "k" — short, like in "kit"'),
    ('e',  'Short open: "ehh" — like in "egg"'),
    ('u',  'Relaxed mouth: "uhh" — like in "up"'),
    ('r',  'Tongue back: "rrrr" (hold ~2 sec)'),
    ('h',  'Just breath: "h" — short like in "hat"'),
    ('b',  'Lip pop voiced: "b" — short'),
    ('f',  'Top teeth on lower lip: "fffff" (hold)'),
    ('l',  'Tongue tip up: "llll" (hold)'),
    ('j',  'Quick: "j" — like start of "jam"'),
    ('v',  'Top teeth, voiced: "vvvv" (hold)'),
    ('w',  'Round lips: "wuh" — short'),
    ('y',  'Tongue high: "yuh" — short like in "yes"'),
    ('z',  'Buzzing: "zzzzz" (hold)'),
    ('x',  'Two sounds together: "ks" — like the end of "box"'),
    ('qu', 'Two sounds: "kw" — like start of "queen"'),
    ('ck', 'Same as K — short "k"'),
    ('ch', 'Quick: "ch" — like start of "chop"'),
    ('sh', 'Soft hiss: "shhhh" (hold)'),
    ('th', 'Tongue between teeth: "thhh" (hold)'),
    ('ng', 'Back-of-throat hum: "ng" — like end of "ring"'),
]

OUTDIR = 'audio'
BACKUP = 'audio_aria_backup'
RECORD_SEC = 2.5

# ANSI colors
def C(code, txt): return f'\033[{code}m{txt}\033[0m'
RED, GRN, YEL, CYN, BLD = '31', '32', '33', '36', '1'

def have(cmd):
    return shutil.which(cmd) is not None

def record_one(letter, hint):
    out = f'{OUTDIR}/{letter}.mp3'
    print()
    print(C(BLD, '═' * 60))
    print(C(BLD, f'  Letter: {letter.upper():<3}     {hint}'))
    print(C(BLD, '═' * 60))
    while True:
        input(C(YEL, f'  Press ENTER when ready to record {letter}...'))
        for n in [3, 2, 1]:
            print(C(CYN, f'  {n}...'), end='', flush=True)
            time.sleep(0.7)
        print(C(GRN, ' RECORDING NOW (' + str(RECORD_SEC) + ' sec)'))
        # Record 2.5 sec from default mic to a temp wav, then convert to mp3
        tmpwav = f'/tmp/_rec_{letter}.wav'
        # avfoundation device :0 = default audio in (or :1 for built-in)
        # -y = overwrite
        cmd = ['ffmpeg', '-y', '-loglevel', 'error',
               '-f', 'avfoundation', '-i', ':0',
               '-t', str(RECORD_SEC), '-ac', '1', '-ar', '22050', tmpwav]
        r = subprocess.run(cmd, stderr=subprocess.PIPE)
        if r.returncode != 0:
            print(C(RED, '  ERROR recording: ' + r.stderr.decode()[:200]))
            print(C(YEL, '  If macOS asked for mic permission, allow it then retry.'))
            return False
        print(C(GRN, '  ✓ recorded. Playing back...'))
        subprocess.run(['afplay', tmpwav])
        print()
        choice = input(C(YEL, '  [k]eep / [r]e-record / [s]kip / [q]uit ? '))
        if choice.startswith('k'):
            # Convert wav to mp3 with normalization
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error',
                            '-i', tmpwav, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                            '-codec:a', 'libmp3lame', '-b:a', '64k', out])
            os.remove(tmpwav)
            sz = os.path.getsize(out)
            print(C(GRN, f'  ✓ saved {out} ({sz} bytes)'))
            return True
        elif choice.startswith('s'):
            os.remove(tmpwav)
            print(C(YEL, f'  skipped {letter}'))
            return False
        elif choice.startswith('q'):
            print(C(YEL, '  quitting — re-run anytime to continue'))
            sys.exit(0)
        # 'r' or anything else: loop and re-record

def main():
    if not have('ffmpeg'):
        print(C(RED, 'ERROR: ffmpeg not installed. Install: brew install ffmpeg'))
        sys.exit(1)
    if not have('afplay'):
        print(C(RED, 'ERROR: afplay missing. (Should be on every Mac.)'))
        sys.exit(1)
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    os.makedirs(OUTDIR, exist_ok=True)
    redo = '--redo' in sys.argv

    # Back up Aria-generated phoneme files on first run only
    if not os.path.exists(BACKUP):
        os.makedirs(BACKUP)
        for L, _ in PHONEMES:
            src = f'{OUTDIR}/{L}.mp3'
            if os.path.exists(src):
                shutil.copy2(src, f'{BACKUP}/{L}.mp3')
        print(C(GRN, f'(backed up Aria-generated phonemes to {BACKUP}/)'))

    print(C(BLD, '\n' + '─' * 60))
    print(C(BLD, '  PHONICS PHONEME RECORDER'))
    print(C(BLD, '─' * 60))
    print(C(YEL, '  Tip: each sound should be 1-2 seconds. Make it crisp like'))
    print(C(YEL, '  Alphablocks — short for plosives (p, t, b, d, k, g),'))
    print(C(YEL, '  longer for sustainables (s, m, n, f, v, l, r, sh).'))
    print(C(YEL, '  You can quit anytime ([q]) and resume from this letter.'))
    print()
    # Determine which to record
    todo = []
    for L, hint in PHONEMES:
        # If file exists AND was just backed up (meaning it was Aria-only),
        # we still want to re-record. Use a marker file to track Anshul-recorded.
        marker = f'{OUTDIR}/.recorded_{L}'
        if os.path.exists(marker) and not redo:
            print(C(GRN, f'  already recorded: {L}  (use --redo to redo)'))
            continue
        todo.append((L, hint))

    if not todo:
        print(C(GRN, '  All phonemes already recorded! Use --redo to re-record.'))
        return
    print(C(CYN, f'  {len(todo)} phonemes to record. Estimated time: {len(todo) * 8} seconds.'))
    print()

    for L, hint in todo:
        if record_one(L, hint):
            with open(f'{OUTDIR}/.recorded_{L}', 'w') as f: f.write('1')

    print(C(GRN, '\n✓ done. Reload the artifact in your browser to hear your voice.'))
    print(C(YEL, '  Aria backups still in audio_aria_backup/ if you want to roll back.'))

if __name__ == '__main__':
    main()
