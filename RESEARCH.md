# Research: why the rules are what they are

The design rules in this pipeline come from a review of peer-reviewed research on very short
narrated, animated science explainers (see [About the source](#about-the-source)). This file
maps each finding to a rule, the limit for that rule in `design.toml`, and the check that
enforces it. When a check fails, read its entry here before you change anything. Never loosen
a limit to make one episode pass.

## The bottom line

For under-60-second mobile explainers, the safest design is one narrated animation, one
learning goal, few redundant words on screen, explicit visual cues, and a moderate speech
rate. Avoid both rushed delivery and heavy simplification. A 60-second explainer should spend
its limited bandwidth on **structure, cueing and wording** before voice polish or extra
visual flourish ([Noetel 2021](#ref-noetel); [Moreno 2007](#ref-moreno); [Brock 2025](#ref-brock)).

The evidence is strongest for signaling, segmentation, short length, and matching animation to
content that really changes. It is mixed for captions and for synthetic versus human
narration. Most direct evidence comes from longer instructional videos, not from feeds of
under-60-second Shorts. So every limit here is a hypothesis that the channel's own numbers must
confirm: see [Open questions](#open-questions-to-test-on-this-channel).

## Rule map

| Rule | What it enforces | Limit (`design.toml`) | Gate | Evidence |
|---|---|---|---|---|
| `one-goal` | the brief's bridge is one sentence: one thing to learn | `bridge_max_words` 30 | `vid check` | one learning goal ([Fyfield 2022](#ref-fyfield); [Noetel 2021](#ref-noetel)) |
| `hook-length` | B1 is at most 15 words | `hook_max_words` | `vid check` | the first 30 s are critical ([Yang 2022](#ref-yang); [García-Martínez 2026](#ref-garcia)) |
| `hook-time` | B1 is over by 6 s | `hook_end_max` | `vid qa` | as above |
| `hook-relevance` | B1 names world A and world B | (keywords in `a:`/`b:`) | `vid check` | early relevance improves viewing ([Yang 2022](#ref-yang); [García-Martínez 2026](#ref-garcia)) |
| `cold-open` | no greeting or channel intro; first word at once; frame 0 shows a moving cover | `intro_phrases`, `narration_start_max`, `first_frame_*` | `vid check`, `vid qa` | fixed intros reduce retention ([Doherty 2023](#ref-doherty)) |
| `early-answer` | the mechanism beat (B3) starts in the first 35% | `answer_by` | `vid check`, `vid qa` | a precise gap, resolved at once ([Tan 2025](#ref-tan); [Singh & Manjaly 2021](#ref-singh); [Brock 2025](#ref-brock)) |
| `micro-units` | each beat at most 30 words and 3 sentences | `beat_max_*` | `vid check` | segmentation ([Spanjers 2010](#ref-spanjers); [Moreno 2007](#ref-moreno); [Zhang 2025](#ref-zhang25)) |
| `length` | 45-60 s | `ste.toml` `seconds`, `[qa] seconds` | `vid check`, `vid qa` | shorter videos hold attention ([Fyfield 2022](#ref-fyfield); [Noetel 2021](#ref-noetel)) |
| `minimal-text` | TXT at most 4 words, labels at most 5, no label repeats 4+ narration words | `txt_max_words`, `screen_max_words`, `echo_words` | `vid check` | redundant text can hurt ([Chan 2020](#ref-chan); [Doherty 2023](#ref-doherty)) |
| `title` | at most 60 characters, names both worlds | `title_max_chars` | `vid check` | concise titles ([Yang 2022](#ref-yang); [García-Martínez 2026](#ref-garcia)); long titles reduce retention ([Doherty 2023](#ref-doherty)) |
| `color-signals` | only the A, B, link and alert color families, plus neutrals | `hue_tolerance`, `neutral_*` | `vid check` | cueing ([Xie 2017](#ref-xie17); [Xie 2016](#ref-xie16)); color only for structure ([Liu 2021](#ref-liu21); [Skulmowski 2021](#ref-skulmowski)) |
| `plain-language` | 80% of VO sentences pass ASD-STE100 rules | `ste.toml` `target` | `vid check` | plain language ([Kerwer 2021](#ref-kerwer); [Wen & Yi 2024](#ref-wen)); do not dilute ([Thowaini 2018](#ref-thowaini); [Kloehn 2018](#ref-kloehn)) |
| `speech-rate` | 130-190 words per minute | `[qa] wpm` | `vid qa` | moderate rate ([Jones 2007](#ref-jones); [Chiu & Chen 2023](#ref-chiu); [Griffiths 1990](#ref-griffiths)) |
| `pauses` | median sentence pause 0.35-0.9 s | `sentence_pause` | `vid qa` | about 0.6 s sounds most natural ([Liu, S. 2022](#ref-liu22)) |
| `captions` | the `.srt` is exactly the approved VO | (none) | `vid qa` | captions help non-native viewers ([Perez 2013](#ref-perez); [Negi & Mitra 2022](#ref-negi)) |
| `dead-air` | no near-black stretch of 1 s or more, no frozen picture of 3 s or more | `black_max`, `freeze_max` | `vid qa` | transience and segmentation ([Spanjers 2010](#ref-spanjers)); house rule: change every 2-3 s |
| `sourced` | every beat with VO is in the claim ledger | (none) | `vid check` | house rule: accuracy protects trust |
| `every-beat` | scene.py speaks the full approved VO, in order | (none) | `vid check` | house rule: the approved VO is the video |
| `format`, `loudness` | 1080x1920, 60 fps, H.264/AAC 48 kHz; -14 LUFS, true peak -1.5 dBTP or lower | `lufs`, `true_peak_max` | `vid qa` | platform delivery |
| `motion-timing`, `motion-coverage` | beat-relative animation and frequent meaningful change | `b.duration` timing; at least 65% eligible story-beat motion | `vid check` | calibrated source proxy |
| `recognition-replay`, `causal-motion` | repeat the mechanism and show cause becoming effect | same B3/B6 geometry and timing; causal change in at least 7 of B1-B8 including B3/B6 | `vid check` | calibrated source proxy |
| `opening-quality`, `stage-coverage`, `layout-variety` | immediate hook, phone legibility and meaningful visual change | rendered opening, occupied safe stage and distinct compositions | `vid qa` | calibrated rendered proxy |
| `sfx-density`, `sfx-audibility`, `sfx-masking` | action-linked cues must register without competing with speech | rendered cue presence, audibility and narration separation | `vid qa` | calibrated audio proxy |
| `delivery-notes` | every spoken beat records performance intent; NOTE does not drive synthesis | one non-empty NOTE per spoken beat | `vid check` | authoring control, not proof of performance |
| `delivery-pace` | aggregate narration pace stays near the two house references | checker default 155-185 words/min pending configuration approval | `vid qa` | calibrated audio proxy |
| QA report identity and freshness | measurements belong to the named master and current rules | matching episode/video, report newer than master, current pipeline fingerprint | `vid status`, `vid final` | integrity control, not an audience claim |

The exact cutoffs used by these source, rendered and audio checks are calibrated against the
house style and reference output. Research supports the direction—fast openings, meaningful
change, legible layouts, moderate delivery, action-linked cues and intelligible speech—but does
not establish the pipeline's exact motion, pixel, similarity, density, gain or timing values.
Treat them as reproducible acceptance proxies and regression tripwires, not stronger research
claims.

## The findings, and what this pipeline does with them

### Openings and keeping watch time

**Findings.** Engagement data from YouTube science and STEM videos show that shorter videos,
stronger early relevance and concise titles improve viewing, and that the first 30 seconds are
especially critical ([Yang 2022](#ref-yang); [García-Martínez 2026](#ref-garcia)). Fixed
introductions, long titles and unnecessary visual or verbal additions reduce retention
([Doherty 2023](#ref-doherty)). Curiosity openers are promising but have thinner evidence:
question-driven nudges increased curiosity and intentional viewing on short-form video, with
weaker learning gains in realistic mixed feeds ([Tan 2025](#ref-tan)). Information gaps and
good questions raise curiosity and later recall ([Singh & Manjaly 2021](#ref-singh);
[Kedrick 2023](#ref-kedrick)). A curiosity opener works best as a **precise information gap
that the video resolves at once**, not a decorative teaser that delays the core explanation
([Tan 2025](#ref-tan); [Brock 2025](#ref-brock)). Seductive details are memorable but can
harm retention ([Brock 2025](#ref-brock); [Maloy 2019](#ref-maloy)).

**What we do.** B1 is a specific, surprising claim (a number, a date or an everyday object)
that names both worlds in 15 words or fewer, with no greeting. The cover is on screen at
frame 0, already moving, and the first word starts at once. The mechanism (B3) answers the
hook within the first third. Spare facts that do not serve the bridge go to the brief's
"Spare facts" list, not into the Short. Titles are 60 characters or fewer and name both
worlds.

**What we measure.** `hook-length`, `hook-relevance`, `cold-open`, `early-answer`, `title`
before rendering; `hook-time`, `cold-open`, `early-answer` on the export.

### Signaling: cue only what matters now

**Findings.** Signaling is one of the most consistently supported interventions in
multimedia learning. Meta-analyses show small-to-moderate gains in retention and transfer,
and the gains grow as cues reduce cognitive load ([Xie 2017](#ref-xie17);
[Xie 2016](#ref-xie16)). Structure cues such as previews, headings and pointer words improve
transfer even when they add no new content ([Mautone & Mayer 2001](#ref-mautone)). Moving or
progressive cues help in animated STEM visuals ([Rodemer 2022](#ref-rodemer)). Color coding
helps when it marks meaningful structure ([Liu 2021](#ref-liu21); [Choi 2023](#ref-choi)),
but more cueing is not always better, and color coding can backfire
([De Koning 2009](#ref-dekoning); [Skulmowski 2021](#ref-skulmowski)). The working rule for
60-second mobile animation: **one color family per concept, one motion path at a time, and no
simultaneous stacks of text, arrows and highlights unless each has its own job**
([Noetel 2021](#ref-noetel); [Yanwen 2026](#ref-yanwen); [Désiron 2026](#ref-desiron)).

**What we do.** Color always means the same thing: world A blue, world B orange, the shared
trick violet, a problem red (`ALERT`), everything else neutral. Captions color the same
keywords the same way. Every beat has a numbered header (a heading cue), and the narration
uses pointer phrases ("That is the trick", "the same trick").

**What we measure.** `color-signals` reads every color in `scene.py`. "One motion path at a
time" has no automatic check yet: read the contact sheets from `vid frames`.

### Segmentation and animation choice

**Findings.** Dynamic media disappear before viewers fully process them; segmentation reduces
this burden by breaking motion into meaningful units with processing time between them
([Spanjers 2010](#ref-spanjers); [Moreno 2007](#ref-moreno)). For under-60-second explainers,
hard cuts between 2-4 micro-units are likely more useful than formal chapters
([Zhang 2025](#ref-zhang25)). Animation beats static pictures when the target is motion,
sequence or change; for stable structure, a static labeled frame with narrated emphasis is
often cleaner ([Ploetzner 2021](#ref-ploetzner); [Ng 2013](#ref-ng);
[Strømme & Mork 2020](#ref-stromme); [Berney & Bétrancourt 2016](#ref-berney)).

**What we do.** The nine beats form three micro-units: World A and its trick (B1-B4), World B
and the recognition (B5-B6), the payback and the map (B7-B9). Each beat is one small idea.
**Animate only the change**: draw a stable diagram, then hold it still while the narration
points at it; move only the part that changes.

**What we measure.** `micro-units` (words and sentences per beat), `dead-air` (no empty or
frozen stretches), plus source-level proxies: `motion-timing`, `motion-coverage`,
`recognition-replay` and `causal-motion`. Their 65% coverage floor, 7-of-8 causal-motion rule
with B3/B6 required, and source patterns for recognizing timing and replay are calibrated
house/reference limits—not findings that viewers require those exact values. "Animate only the
change," path clarity, stable structure and seductive detail remain manual contact-sheet checks.

### Narration and language

**Findings.** Modern text-to-speech sometimes matches human narration on learning in short
animations ([Craig & Schroeder 2018](#ref-craig)), and AI-generated instructional videos can
match recorded ones on retention ([Xu 2024](#ref-xu); [Zhang 2025](#ref-zhang25)). Human voices
still win in some studies, especially when a synthetic voice is stylized in a distracting way
([Xiao 2025](#ref-xiao); [Jing 2024](#ref-jing); [Matveeva & Vikhrova 2026](#ref-matveeva)).
Speech rate matters more for comprehension than for engagement: faster synthetic speech
reduces comprehension for native and non-native listeners, while very slow speech brings no
gain ([Jones 2007](#ref-jones); [Chiu & Chen 2023](#ref-chiu); [McBride 2011](#ref-mcbride);
[Griffiths 1990](#ref-griffiths)). Listeners rated speech as most natural when punctuation
pauses were about 0.6 s: **slightly slowed delivery with clear phrase boundaries beats uniform
slowdown** ([Liu, S. 2022](#ref-liu22)). Plain language works better than "simplify
everything": use common words and short clauses, explain unavoidable technical terms, and do
not remove key information ([Kerwer 2021](#ref-kerwer); [Wen & Yi 2024](#ref-wen);
[Thowaini 2018](#ref-thowaini); [Kloehn 2018](#ref-kloehn)).

**What we do.** The frozen series voice is Kokoro `af_heart`: a plain adult voice, not a
stylized one. Scripts reach 80% ASD-STE100 and name each technical term in the glossary;
explain each one at first use.

**What we measure.** `plain-language` (STE score), `speech-rate`, `pauses`. Measured on the
current exports:

| Episode | Words/min | Median sentence pause |
|---|---|---|
| 001 Camera × Chip | 163.2 | 0.50 s |
| 002 Air traffic × Touchscreen | 177.3 | 0.52 s |

Both sit inside the moderate band; 002 is near its fast end. The pauses are already close to
the 0.6 s that sounds most natural, and they come from the model itself: `voice.toml`'s
`sentence_pause` and `clause_pause` act only between text batches of about 500 phonemes, and
every beat fits in one batch, so those two values never reach inside a beat. The lever for a
slower pace is `speed`. Measured on 002's narration (2026-10-07):

| `speed` | Narration | Words/min | Median sentence pause |
|---|---|---|---|
| 1.0 (frozen) | 53.8 s | 177.3 | 0.52 s |
| 0.95 | 55.5 s | 171.9 | 0.53 s |
| 0.9 | 57.6 s | 165.5 | 0.56 s |

That is proposal E1 below; it changes the frozen voice, so it needs the creator's approval.

### Captions and on-screen text

**Findings.** Same-language captions are one of the clearest aids for non-native viewers
([Perez 2013](#ref-perez); [Negi & Mitra 2022](#ref-negi); [Pujadas & Muñoz 2024](#ref-pujadas)),
but they are not a universal boost: with native narration, full on-screen text can hurt
deeper learning ([Chan 2020](#ref-chan)), and in some YouTube lecture data captions were
linked to lower retention, with shorter chunks and more signaling linked to higher retention
([Doherty 2023](#ref-doherty)). For a broad mobile audience the report recommends **selective
burned-in text, not verbatim transcripts**: keyword captions, highlighted terms, or
native-language subtitle options ([Teng 2023](#ref-teng); [Choi 2023](#ref-choi)). Watching
without sound makes viewers depend on subtitles but lowers comprehension and enjoyment, so
captions cannot fully replace narration ([Szarkowska 2024](#ref-szarkowska)).

**What we do.** Our audience is global and often non-native (that is why the script is STE),
so the burned-in captions stay, in short three-word chunks with the theme keywords
highlighted in their semantic colors. Big on-screen words (TXT) are keywords, never sentences.
Every upload includes the `.srt`, so YouTube can offer translated subtitles. Whether
keyword-only captions retain better is open question E2.

**What we measure.** `minimal-text` (TXT and labels short; no label echoes the narration),
`captions` (the `.srt` is exactly the approved VO).

## Checks a program cannot make yet

Automation still cannot decide whether a motion path communicates the intended cause, whether
stable structure stays still, whether the right thing is cued, or whether a detail is seductive.
The creator's three distinct phone-size reviews remain mandatory: watch once with sound, watch
once muted, and listen to the complete export sound-only with the picture hidden. In the
sound-only pass, judge whether pace, pauses, emphasis and turns follow each beat's `NOTE:`,
whether cues are meaningful and audible, and whether any cue masks narration. The automated
proxies above never replace these reviews.

Do the visual checks by reading every contact sheet (`vid frames <ep>`); do the audio checks
during the separate sound-only review described above:

- **One motion path at a time.** In any frame, only one thing travels; everything else is
  still or changes in place.
- **Animate only the change.** A stable diagram is drawn once and held; motion shows the
  mechanism, not decoration.
- **Cue only what matters now.** No stack of arrow + highlight + label + sound on the same
  object unless each does a different job.
- **Explain technical terms** at first use, in plain words, without removing the science.
- **No seductive details.** A fun fact that does not serve the bridge goes to "Spare facts".

## What earns money here

The platform rules below were checked on 2026-10-07 from news reports of YouTube's own
announcements. They change often: confirm them in YouTube Help before you rely on a number.

- **Shorts revenue needs sustained view volume.** YouTube announced on 10 August 2026 that,
  from 1 February 2027, a channel earns from the Shorts Creator Pool only while it has
  10 million qualified Shorts views in a rolling 90 days. New Partner Program applicants need
  1,000 subscribers plus 20 million Shorts views in 90 days, or 8,000 watch hours in 365 days.
  Qualified views exclude non-original content, re-uploads and compilations
  ([PPC Land, 2026](https://ppc.land/youtube-cuts-shorts-pay-for-channels-under-10m-views-from-february-2027/)).
- **Views count from the first frame, engaged views decide money.** Since 31 March 2025 a
  Shorts view counts when playback starts or replays; "engaged views" (watched past the first
  seconds) remain the measure for monetization
  ([PPC Land, 2025](https://ppc.land/youtube-changes-how-shorts-views-are-counted-from-march-31/)).
- **Originality is a monetization rule.** Since 15 July 2025, "inauthentic" (mass-produced or
  repetitive, template-only) content cannot earn; AI tools are allowed when they add value
  ([Gulf News, 2025](https://gulfnews.com/technology/youtube-updates-monetisation-policies-ai-and-repetitive-content-ban-begins-july-15-1.500192660)).

What this means for the pipeline:

1. **Win the first seconds.** Every view that stays past the opening becomes an engaged view.
   That is why the hook rules (`cold-open`, `hook-length`, `hook-relevance`, `hook-time`)
   are gates and not advice.
2. **Answer fast and end clean.** `early-answer` keeps viewers to the end; a final pose that
   flows into frame 0 invites a replay.
3. **Be original every time.** The 9-beat format is a style; each episode must bring new
   research, new diagrams and new words. `vid lint` (no carry-over) and the claim ledger
   (`sourced`) are the evidence that a human-directed process made each Short.
4. **Never upload compilations of Shorts as Shorts**; they do not earn qualified views.
5. **Measure.** Revenue follows engaged views, so record them (`analytics/results.csv`) and
   let the data change the limits.

## Open questions to test on this channel

The report's biggest open question is how these principles work in truly under-60-second
feed videos. Test one change at a time, on comparable episodes, and log each test in
`analytics/experiments.md`. Watch "stayed to watch" (viewed vs swiped away), average
percentage viewed and subscribers per 1,000 views in `vid report`.

| # | Question | Change to test | Needs approval |
|---|---|---|---|
| E1 | Does a slightly slower pace help non-native viewers stay? | `voice.toml` speed 1.0 → 0.95 (about 172 instead of 177 words/min, 1.7 s longer; see "Narration and language") | yes: the voice is frozen |
| E2 | Do keyword-only captions beat three-word verbatim captions? | a keyword caption mode in `kit/short.py` | yes: house style |
| E3 | Does a number or date in the hook raise "stayed to watch"? | hooks with and without one | no |
| E4 | Do shorter titles (40 characters or fewer) do better? | title length | no |
| E5 | Is 45 s better than 60 s for this format? | trim beats, not facts | no |

## About the source

The findings above are paraphrased from *Very Short Science Explainer Design*, a report the
creator generated with Consensus (consensus.app) in 2026. The report itself is not in this
repository: its license allows personal, non-commercial use only and needs the copyright
holders' consent for redistribution. The creator keeps the PDF locally; it is listed in
`.gitignore`. The references below are the peer-reviewed studies the report cites.

## References

- <a id="ref-berney"></a>Berney, S., & Bétrancourt, M. (2016). Does animation enhance learning? A meta-analysis. *Computers & Education, 101*, 150-167. https://doi.org/10.1016/j.compedu.2016.06.005
- <a id="ref-brock"></a>Brock, R., O'Dwyer, L., & Rogers, B. (2025). The effect of seductive details on knowledge retention in physics videos: A mixed methods study. *Journal of Research in Science Teaching*. https://doi.org/10.1002/tea.70005
- <a id="ref-chan"></a>Chan, K.-Y., et al. (2020). Effect of on-screen text on multimedia learning with native and foreign-accented narration. *Learning and Instruction*. https://doi.org/10.1016/j.learninstruc.2020.101305
- <a id="ref-chiu"></a>Chiu, C.-W., & Chen, T.-P. (2023). Speech rate and young EFL learners' listening comprehension. *English Language Teaching*. https://doi.org/10.5539/elt.v16n7p74
- <a id="ref-choi"></a>Choi, S. (2023). Visual saliency in captioned digital videos and learning of English collocations: An eye-tracking study. *Language Learning & Technology*. https://doi.org/10.64152/10125/73536
- <a id="ref-craig"></a>Craig, S., & Schroeder, N. L. (2018). Text-to-speech software and learning: Investigating the relevancy of the voice effect. *Journal of Educational Computing Research, 57*, 1534-1548. https://doi.org/10.1177/0735633118802877
- <a id="ref-dekoning"></a>De Koning, B. B., Tabbers, H. K., Rikers, R., & Paas, F. (2009). Towards a framework for attention cueing in instructional animations. *Educational Psychology Review, 21*, 113-140. https://doi.org/10.1007/s10648-009-9098-7
- <a id="ref-desiron"></a>Désiron, J. C., Endres, T., & Schneider, S. (2026). Is it not too redundant? When signaling overlap reduces extraneous load and enhances retention in a software video tutorial. *Frontiers in Psychology, 17*. https://doi.org/10.3389/fpsyg.2026.1795142
- <a id="ref-doherty"></a>Doherty, C. (2023). Using web log analysis to evaluate healthcare students' engagement behaviours with multimedia lectures on YouTube. *PLOS ONE, 18*. https://doi.org/10.1371/journal.pone.0284133
- <a id="ref-fyfield"></a>Fyfield, M., Henderson, M. B., & Phillips, M. (2022). Improving instructional video design: A systematic review. *Australasian Journal of Educational Technology*. https://doi.org/10.14742/ajet.7296
- <a id="ref-garcia"></a>García-Martínez, E., García-Martínez, S., & García-González, N. (2026). Analyzing STEM video characteristics on viewer engagement for dissemination and exercise contents: A data-driven approach. *International Journal of Science Education, Part B, 16*, 426-444. https://doi.org/10.1080/21548455.2026.2616740
- <a id="ref-griffiths"></a>Griffiths, R. (1990). Speech rate and NNS comprehension: A preliminary study in time-benefit analysis. *Language Learning, 40*, 311-336. https://doi.org/10.1111/j.1467-1770.1990.tb00666.x
- <a id="ref-jing"></a>Jing, B., et al. (2024). Cute computer-synthesized voice hinders learning performance in instructional videos. *The Journal of Experimental Education, 94*, 752-769. https://doi.org/10.1080/00220973.2024.2446169
- <a id="ref-jones"></a>Jones, C., Berry, L., & Stevens, C. (2007). Synthesized speech intelligibility and persuasion: Speech rate and non-native listeners. *Computer Speech & Language, 21*, 641-651. https://doi.org/10.1016/j.csl.2007.03.001
- <a id="ref-kedrick"></a>Kedrick, K., Schrater, P., & Koutstaal, W. (2023). The multifaceted role of self-generated question asking in curiosity-driven learning. *Cognitive Science, 47*(4), e13253. https://doi.org/10.1111/cogs.13253
- <a id="ref-kerwer"></a>Kerwer, M., et al. (2021). Straight from the scientist's mouth: Plain language summaries promote laypeople's comprehension and knowledge acquisition. *Collabra: Psychology*. https://doi.org/10.1525/collabra.18898
- <a id="ref-kloehn"></a>Kloehn, N., et al. (2018). Improving consumer understanding of medical text: Development and validation of a new SubSimplify algorithm. *Journal of Medical Internet Research, 20*. https://doi.org/10.2196/10779
- <a id="ref-liu21"></a>Liu, Y., et al. (2021). Impacts of color coding on programming learning in multimedia learning. *Frontiers in Psychology, 12*. https://doi.org/10.3389/fpsyg.2021.773328
- <a id="ref-liu22"></a>Liu, S., et al. (2022). How pause duration influences impressions of English speech: Comparison between native and non-native speakers. *Frontiers in Psychology, 13*. https://doi.org/10.3389/fpsyg.2022.778018
- <a id="ref-maloy"></a>Maloy, J., Fries, L., Laski, F., & Ramirez, G. (2019). Seductive details in the flipped classroom. *CBE Life Sciences Education, 18*. https://doi.org/10.1187/cbe.19-01-0004
- <a id="ref-matveeva"></a>Matveeva, E., & Vikhrova, E. (2026). The psychology of voice in digital education: Comparing natural and AI-generated narration. *Psychology. Journal of the Higher School of Economics*. https://doi.org/10.17323/1813-8918-2026-2-241-252
- <a id="ref-mautone"></a>Mautone, P. D., & Mayer, R. (2001). Signaling as a cognitive guide in multimedia learning. *Journal of Educational Psychology, 93*, 377-389. https://doi.org/10.1037/0022-0663.93.2.377
- <a id="ref-mcbride"></a>McBride, K. (2011). The effect of rate of speech and distributed practice on the development of listening comprehension. *Computer Assisted Language Learning, 24*, 131-154. https://doi.org/10.1080/09588221.2010.528777
- <a id="ref-moreno"></a>Moreno, R. (2007). Optimising learning from animations by minimising cognitive load. *Applied Cognitive Psychology, 21*, 765-781. https://doi.org/10.1002/acp.1348
- <a id="ref-negi"></a>Negi, S., & Mitra, R. (2022). Native language subtitling of educational videos: A multimodal analysis with eye tracking, EEG and self-reports. *British Journal of Educational Technology, 53*, 1793-1816. https://doi.org/10.1111/bjet.13214
- <a id="ref-ng"></a>Ng, H.-K., Kalyuga, S., & Sweller, J. (2013). Reducing transience during animation: A cognitive load perspective. *Educational Psychology, 33*, 755-772. https://doi.org/10.1080/01443410.2013.785050
- <a id="ref-noetel"></a>Noetel, M., et al. (2021). Multimedia design for learning: An overview of reviews with meta-meta-analysis. *Review of Educational Research, 92*, 413-454. https://doi.org/10.3102/00346543211052329
- <a id="ref-perez"></a>Perez, M. M., Van Den Noortgate, W., & Desmet, P. (2013). Captioned video for L2 listening and vocabulary learning: A meta-analysis. *System, 41*, 720-739. https://doi.org/10.1016/j.system.2013.07.013
- <a id="ref-ploetzner"></a>Ploetzner, R., Berney, S., & Bétrancourt, M. (2021). When learning from animations is more successful than learning from static pictures. *Instructional Science, 49*, 497-514. https://doi.org/10.1007/s11251-021-09541-w
- <a id="ref-pujadas"></a>Pujadas, G., & Muñoz, C. (2024). When to switch captions off? *Studies in Second Language Learning and Teaching*. https://doi.org/10.14746/ssllt.38036
- <a id="ref-rodemer"></a>Rodemer, M., et al. (2022). Dynamic signals in instructional videos support students to navigate through complex representations. *Applied Cognitive Psychology*. https://doi.org/10.1002/acp.3973
- <a id="ref-singh"></a>Singh, A., & Manjaly, J. A. (2021). The effect of information gap and uncertainty on curiosity and its resolution. *Journal of Cognitive Psychology, 33*, 403-423. https://doi.org/10.1080/20445911.2021.1908311
- <a id="ref-skulmowski"></a>Skulmowski, A. (2021). When color coding backfires: A guidance reversal effect when learning with realistic visualizations. *Education and Information Technologies, 27*, 4621-4636. https://doi.org/10.1007/s10639-021-10796-6
- <a id="ref-spanjers"></a>Spanjers, I. A. E., Van Gog, T., & Van Merriënboer, J. J. G. (2010). A theoretical analysis of how segmentation of dynamic visualizations optimizes students' learning. *Educational Psychology Review, 22*, 411-423. https://doi.org/10.1007/s10648-010-9135-6
- <a id="ref-stromme"></a>Strømme, T. A., & Mork, S. M. (2020). Students' conceptual sense-making of animations and static visualizations of protein synthesis. *Research in Science Education, 51*, 1013-1038. https://doi.org/10.1007/s11165-020-09920-2
- <a id="ref-szarkowska"></a>Szarkowska, A., et al. (2024). Watching subtitled videos with the sound off affects viewers' comprehension, cognitive load, immersion, enjoyment, and gaze patterns. *PLOS ONE, 19*, e0306251. https://doi.org/10.1371/journal.pone.0306251
- <a id="ref-tan"></a>Tan, F. F.-Y., et al. (2025). Curious Shorts: Curiosity-driven exploration and learning on short-form video platforms. *Proceedings of CHI 2025*. https://doi.org/10.1145/3706598.3713951
- <a id="ref-teng"></a>Teng, M. (2023). Effectiveness of captioned videos for incidental vocabulary learning and retention: The role of working memory. *Computer Assisted Language Learning, 38*, 206-234. https://doi.org/10.1080/09588221.2023.2173613
- <a id="ref-thowaini"></a>Thowaini, A., & Mohammad, A. (2018). Speech modification to non-native speakers and content dilution: Implications for English as a medium of instruction. https://doi.org/10.13016/m2vq2sd7p
- <a id="ref-wen"></a>Wen, J.-H., & Yi, L. (2024). Are plain language summaries more readable than scientific abstracts? *Public Understanding of Science, 34*, 114-126. https://doi.org/10.1177/09636625241252565
- <a id="ref-xiao"></a>Xiao, M., Li, W., Han, L., & Zheng, S. (2025). Optimising multimedia learning: Effects of pedagogical agents' appearance and voice. *Journal of Computer Assisted Learning, 41*. https://doi.org/10.1111/jcal.70101
- <a id="ref-xie16"></a>Xie, H.-P., et al. (2016). Cueing effect in multimedia learning: A meta-analysis. *Acta Psychologica Sinica, 48*, 540-555. https://doi.org/10.3724/sp.j.1041.2016.00540
- <a id="ref-xie17"></a>Xie, H.-P., et al. (2017). The more total cognitive load is reduced by cues, the better retention and transfer of multimedia learning. *PLoS ONE, 12*. https://doi.org/10.1371/journal.pone.0183884
- <a id="ref-xu"></a>Xu, T., et al. (2024). From recorded to AI-generated instructional videos: A comparison of learning performance and experience. *British Journal of Educational Technology, 56*, 1463-1487. https://doi.org/10.1111/bjet.13530
- <a id="ref-yang"></a>Yang, S., Brossard, D., Scheufele, D., & Xenos, M. (2022). The science of YouTube: What factors influence user engagement with online science videos? *PLOS ONE, 17*. https://doi.org/10.1371/journal.pone.0267697
- <a id="ref-yanwen"></a>Y., Hu, X.-Q., Peng, Q., & Wang, L. (2026). Effects of cueing interventions on online learning outcomes: A meta-analytic review of 40 studies. *Frontiers in Psychology, 17*. https://doi.org/10.3389/fpsyg.2026.1717604 (the report cites it as "Yanwen et al., 2026")
- <a id="ref-zhang25"></a>Zhang, Y., Lucas, M., Bem-Haja, P., & Pedro, L. (2025). AI versus human-generated voices and avatars: Rethinking user engagement and cognitive load. *Education and Information Technologies, 30*, 22547-22566. https://doi.org/10.1007/s10639-025-13654-x
