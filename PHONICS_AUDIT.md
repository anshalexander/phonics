# Phonics App Audit — every option, every lesson

Walked **111 clickable elements** across all 10 lessons via headless Chromium + Playwright. For each, recorded what audio file the browser fetched and the Whisper transcription, then a verdict on whether the pedagogy + sound match.

## Phoneme cards — 32 letter sounds (teacher-style)

Every card now follows one of three patterns, chosen per phoneme based on what Aria renders cleanly:

| Pattern | Letters | Recipe form |
|---|---|---|
| **Stretchable** (sustainable consonants + long vowels) | s n m r l f v z sh th, a o | `"X says SSSSS, like W1, like W2."` |
| **Letter + example** (plosives + short vowels + when stretching fails) | p t b d g c k h j, i u e | `"X, like W1. X, like W2."` |
| **Special** (multi-letter + semi-vowels) | x w y ch ng qu ck | tuned per letter |

| Letter | Audio (Whisper transcript) | Verdict |
|---|---|---|
| **s** | "S says SSSSSSS like snake like sat" | ✓ |
| **a** | "A says AAAA, like ant, like apple" | ✓ |
| **t** | "T like top, T like tap" | ✓ |
| **p** | "P, like pop. P, like pin." | ✓ |
| **i** | "I, like in. I, like it." | ✓ |
| **n** | "N says nnnn, like net, like nut" | ✓ |
| **m** | "M says mmmm, like mom, like map" | ✓ |
| **d** | "D, like dog. D, like did." | ✓ |
| **g** | "G, like go. G, like get." | ✓ |
| **o** | "O says ahhh, like on, like dog" | ✓ |
| **c** | "C, like cat. C, like cup." | ✓ |
| **k** | "K, like kit. K, like kick." | ✓ |
| **e** | "E, like egg. E, like end." | ✓ (was "ehhh" → /eɪ/, changed to letter+example) |
| **u** | "U, like up. U, like under." | ✓ |
| **r** | "R says rrrrr, like run, like red" | ✓ |
| **h** | "H, like hat. H, like hop." | ✓ |
| **b** | "B, like big. B, like bat." | ✓ |
| **f** | "F says fffff, like fun, like fish" | ✓ |
| **l** | "L says lllll, like leg, like log" | ✓ |
| **ck** | "C K, like duck. C K, like sock." | ✓ |
| **j** | "J, like jam. J, like jet." | ✓ |
| **v** | "V says vvvvv, like van, like vet" | ✓ |
| **w** | "W says wuh, like win, like web" | ✓ |
| **x** | "X says ks, like box, like fox" | ✓ |
| **y** | "Y says yuh, like yes, like yum" | ✓ |
| **z** | "Z says zzzzz, like zip, like buzz" | ✓ |
| **qu** | "Q U, like queen. Q U, like quack." | ✓ (simplified from "says K W") |
| **sh** | "S H says shhhhh, like ship, like fish" | ✓ |
| **ch** | "C H says chuh, like chop, like chin" | ✓ |
| **th** | "T H says thhh, like thin, like math" | ✓ |
| **ng** | "N G, like ring. N G, like sing." | ✓ |

---

## Lesson-by-lesson audit

### M1. Listen & Rhyme (6 pairs)

| # | Pair | Should rhyme | Plays | Verdict |
|---|---|---|---|---|
| 1 | cat + hat | yes | word_cat.wav, word_hat.wav, p_yes_rhyme.mp3 | ✓ |
| 2 | dog + log | yes | word_dog.wav, word_log.wav, p_yes_rhyme.mp3 | ✓ |
| 3 | sun + fun | yes | word_sun.wav, word_fun.wav, p_yes_rhyme.mp3 | ✓ |
| 4 | cat + dog | no | (cached) + p_nope_rhyme.mp3 | ✓ |
| 5 | pin + win | yes | word_pin.wav, word_win.wav, p_yes_rhyme.mp3 | ✓ |
| 6 | big + bed | no | word_big.wav, word_bed.wav, p_nope_rhyme.mp3 | ✓ |

### M2. First Sounds: s, a, t, p (4 cards)
Each plays the teacher-style phoneme audio above.

### M3. More Sounds: i, n, m, d (4 cards)
Same pattern.

### M4. Building Words — CVC blending (6 word cards) — **REWIRED**

| # | Word | Letters | Behavior |
|---|---|---|---|
| 1 | sat | s, a, t | Tap each cube → 0.5s synth phoneme. Tap "sat" → blends + speaks word. |
| 2 | pin | p, i, n | Same |
| 3 | mat | m, a, t | Same |
| 4 | dim | d, i, m | Same |
| 5 | tap | t, a, p | Same |
| 6 | nap | n, a, p | Same |

**Was**: Each phoneme played the 4-sec teacher MP3 — blending "sat" took ~14 seconds. **Now**: blend-letter and blend-final use the Web Audio formant synth that was already in the artifact (`Phonemes.RECIPES`), ~0.5s per phoneme. Snappy.

### M5. More Sounds: g, o, c, k (4 cards)
Same as M2/M3.

### M6. Find the First Sound — 5 rounds × 3 options

| Round | Target | Options | Correct | Phonics check |
|---|---|---|---|---|
| 1 | /s/ | sun, cat, dog | **sun** | ✓ |
| 2 | /c/=/k/ | apple, cat, fish | **cat** | ✓ |
| 3 | /m/ | moon, bird, egg | **moon** | ✓ |
| 4 | /r/ | rocket, mug, tree | **rocket** | ✓ |
| 5 | /p/ | pig, nest, sun | **pig** | ✓ |

⚠ Visual: dog and cat icons in round 1 are both round brown heads — hard for a 3yo to distinguish. Worth swapping one SVG.

### M7. More Sounds: e, u, r, h, b, f, l, ck (8 cards)
Each plays its teacher phoneme.

### M8. Tricky Words (12 sight words)
the, I, a, to, no, go, is, was, my, you, are, all → each plays its `word_<word>.mp3`. ✓

### M9. More Sounds: j, v, w, x, y, z, qu (7 cards)
Each plays its teacher phoneme. **X says "ks, like box, like fox"** — exactly the X-as-/ks/ goal.

### M10. Two Letters, One Sound (4 digraphs + 12 chips)

| Digraph | Sound | Example chips |
|---|---|---|
| sh | shhhhh | ship, shop, fish |
| ch | chuh | chop, chin, rich |
| th | thhh | the, thin, math |
| ng | (no stretch) | ring, sing, long |

All 12 chips now speak their word (the original `event.stopPropagation()` bug killed them; fixed).

---

## Issues found in this audit, all fixed

1. **M10 example chips silently failed** (12 of them). `onclick="event.stopPropagation()"` killed bubble before the global click handler. Removed.
2. **48 console 404s at load** — probe tried .mp3 first but trimmed words exist as .wav. Sight-word-aware probe order. Now 0 errors.
3. **"Phase 1", "Phase 2 Set 1", "CVC Blending", "Phoneme isolation", "digraphs"** jargon on every lesson card. Rewritten in plain kid/parent language.
4. **All 32 phoneme files were just stretched noise + example words** with no "S says…" framing. Rewrote to teacher-style.
5. **C card said "Kate Cup Cut"** because /æ/ + /ɒ/ lengthened at sentence-final. Now uses mid-position carrier.
6. **M4 blending used 4-sec teacher MP3 per phoneme** (14-sec blends). Switched to Web Audio synth.
7. **'e' card said "ehhh" which renders as /eɪ/** (letter A name). Changed to letter+example.
8. **'qu' said "Q U says K W"** rendering as "Cue You says K W" — 4 letter sounds in 6 words. Simplified to "Q U, like queen. Q U, like quack."

---

## Open items for you to check subjectively

- **m6 round 1**: dog and cat icons are both round brown heads — a 3yo can't tell them apart. Consider adding ears/whiskers/colour difference.
- **Mascots only on m2 letter cards** (snake/ant/clock/pig) — consider mascots on all letter cards for visual consistency.
- **m4 blending lab UI** scrolls below the fold on smaller screens. Recommend `scrollIntoView` after the word card tap.
