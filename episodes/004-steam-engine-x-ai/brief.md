# 004-steam-engine-x-ai · brief

**Pair:** A = Steam engine (Watt's engine and British coal) · B = AI (tokens and data centers)
**The bridge (one sentence, 30 words max: the one thing the viewer learns):** When each use of
a resource gets cheaper, people find many more uses, so total consumption can rise: coal after
Watt's engine, tokens after cheap AI.
**A helped B by:** The coal-era idea itself: in 2025 Microsoft's chief executive used Jevons's
1865 coal argument, by name, to explain why cheaper AI would be used more (C9).
**B helped A by:** AI's electricity demand now props up coal: coal supplies roughly 30% of data
center electricity, and US utilities have delayed coal-plant retirements, citing data centers (C10, C11).

## Claim ledger

Verification note for the creator: this research ran in a sandbox whose network allows only
package managers and GitHub, so the links below were checked through web-search extracts of
each page, not opened directly. Open every link before publishing (WORKFLOW.md, step 1).

| # | Claim, as said (beats) | Source 1 | Source 2 | Confidence |
|---|---|---|---|---|
| C1 | In 1769 James Watt patented a separate condenser ("a new invented method of lessening the consumption of steam and fuel in fire engines"); it kept the engine's cylinder hot. (B2) | [Britannica · Watt steam engine](https://www.britannica.com/print/article/2126358) | [Science Museum · James Watt and the separate condenser](https://blog.sciencemuseum.org.uk/james-watt-and-the-separate-condenser) | high |
| C2 | Engines with Watt's condenser used far less coal than Newcomen engines for the same work: sources give 25-30% of the fuel, "about 75% less" or "two-thirds less", so "less than half the coal" is safe. (B1, B2, B3) | [National MagLab · Steam condensing engine, 1769](https://nationalmaglab.org/magnet-academy/history-of-electricity-magnetism/museum/steam-condensing-engine-1769/) | [Watt steam engine (fuel use vs. Newcomen)](https://en.wikipedia.org/wiki/Watt_steam_engine) | high |
| C3 | Cheaper steam power spread beyond mine pumping: Watt's rotative engines drove mills, and steam later powered railways; Jevons credited engine economy with widening the uses of coal. (B3) | [Watt steam engine (rotative engines in mills)](https://en.wikipedia.org/wiki/Watt_steam_engine) | [The Coal Question (summary of Jevons's argument)](https://en.wikipedia.org/wiki/The_Coal_Question) | medium-high |
| C4 | British coal output grew more than four times from 1854 (64.7 million tons) to its 1913 peak (about 287 million tons). (B1, B3) | [NBER series via FRED · Coal production for United Kingdom](https://fred.stlouisfed.org/data/A01211GBA418NNBR) | [Hansard, 9 July 1937 · written answer: 1913 output 287.3 million tons](https://hansard.parliament.uk/html/Commons/1937-07-09/WrittenAnswers) | high |
| C5 | In *The Coal Question* (1865), W. Stanley Jevons argued that using coal more economically increases its consumption: "It is wholly a confusion of ideas to suppose that the economical use of fuel is equivalent to a diminished consumption. The very contrary is the truth." (B4) | [Jevons, *The Coal Question*, public-domain text (Econlib)](https://www.econlib.org/library/YPDBooks/Jevons/jvnCQ.html) | [Yale Energy History · Jevons, The Coal Question, 1865](https://energyhistory.yale.edu/w-stanley-jevons-the-coal-question-1865/) | high |
| C6 | AI language models read and write text as tokens, small pieces of words, and are priced per token. (B5) | [OpenAI Help · What are tokens and how to count them](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them) | [Google AI for Developers · Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens) | high |
| C7 | The price of reaching GPT-3.5-level performance fell from about $20 to $0.07 per million tokens between November 2022 and October 2024, more than 280-fold (Stanford AI Index 2025); said as "in two years ... fell over two hundred times". (B5) | [Stanford HAI · AI Index Report 2025](https://hai.stanford.edu/ai-index/2025-ai-index-report) | [Summary of the AI Index figure: $20 to $0.07 per million tokens](https://siliconcanals.com/the-cost-of-running-a-top-tier-ai-query-dropped-280-fold-in-roughly-18-months-from-20-per-million-tokens-in-late-2022-to-seven-cents-by-late-2024-a-price-collapse-with-no-real-parallel-in/) | high |
| C8 | Google processed about 9.7 trillion tokens a month across its products and APIs in 2024, and more than 480 trillion a month by May 2025: about 50 times more in one year. (B6) | [Mobile World Live · Pichai opens Google I/O with AI update](https://www.mobileworldlive.com/google/pichai-opens-google-i-o-with-ai-update/) | [DT Next · Gemini app crosses 400 million monthly users](https://www.dtnext.in/technology/gemini-ai-app-crosses-400-million-monthly-active-users-sundar-pichai-834361) | high |
| C9 | On 27 January 2025 Satya Nadella posted "Jevons paradox strikes again!": as AI gets more efficient and accessible, its use will skyrocket. Cheaper answers are built into more apps and agents ("Apps and agents add AI"). (B6) | [Fortune · Nadella on DeepSeek and the Jevons paradox](https://fortune.com/2025/01/27/microsoft-ceo-satya-nadella-deepseek-optimism-jevons-paradox) | [NPR Planet Money · AI, DeepSeek and the Jevons paradox](https://www.npr.org/sections/planet-money/2025/02/04/g-s1-46018/ai-deepseek-economics-jevons-paradox) | medium (the causal claim is an argument, not a measurement) |
| C10 | Coal currently supplies roughly 30% of the electricity used by data centers worldwide (IEA, *Energy and AI*, April 2025). (B7) | [IEA · Energy and AI, executive summary](https://www.iea.org/reports/energy-and-ai/executive-summary) | [Hurriyet Daily News (AFP) · AI surge to double data center electricity demand by 2030](https://www.hurriyetdailynews.com/ai-surge-to-double-data-center-electricity-demand-by-2030-iea-207891) | medium (check the IEA report's supply chapter; the press copies come from one AFP story) |
| C11 | In 2025 several US utilities postponed planned coal-plant retirements, in some cases citing data-center demand. (B7) | [DeSmog · 15 coal plant retirements delayed amid AI data centers](https://www.desmog.com/2025/12/12/15-coal-plant-retirements-delayed-ai-data-centers-trump-doe-orders/) | [Frontier Group · Data center energy use gives old power plants a new lease on life](https://frontiergroup.org/articles/data-center-energy-use-is-giving-old-dirty-power-plants-a-new-lease-on-life/) | medium-high (advocacy and trade press; confirm against EIA) |
| C12 | The IEA projects data-center electricity use to more than double, from about 415 TWh in 2024 to about 945 TWh in 2030, with AI the most important driver; said as "Experts expect data centers to use twice as much power this decade" (IEA shown on screen). (B8) | [IEA · Energy and AI, executive summary](https://www.iea.org/reports/energy-and-ai/executive-summary) | [Data Centre Magazine · IEA on AI and global energy demand](https://datacentremagazine.com/technology-and-ai/iea-asks-how-is-ai-reshaping-global-energy-demand) | high |
| F1 | "cheaper use brings more use" (B4) | framing: the one-line form of Jevons's argument in C5 | | n/a |
| F2 | "Cheaper AI does the same." / "Each job became cheaper, and the total grew." (B1, B9) | framing: synthesis of C2-C4 (coal) and C7-C8 (tokens) | | n/a |

## Myth check

- **The popular version of this story:** "James Watt invented the steam engine, it saved coal,
  so Britain burned more, and AI is exactly the same." Also: "Jevons named the Jevons paradox."
- **What the sources actually support:** Watt improved the Newcomen engine (1712); his 1769
  separate condenser cut fuel per unit of work by well over half. Jevons argued in 1865 that
  economy of fuel raises total consumption; British coal output did rise more than fourfold
  between 1854 and 1913, but coal demand also grew with population, iron, railways and exports,
  so the causal share of efficiency is Jevons's argument, not a measurement. The name "Jevons
  paradox" came later. For AI, prices per token fell sharply and token volumes rose sharply; that
  cheap tokens *cause* the rise is the argument Nadella and others make, and how far total energy
  use follows is still an IEA projection.
- **Words to avoid:** "invented" (for Watt), "named" (for Jevons; say "described"), "proved",
  and any claim that cheap AI *already* doubled electricity use. Say "experts expect" and show IEA.
- **Pace note:** years and "280" are slow to say; the VO keeps one year (1769) and says "over two
  hundred times" so the frozen voice lands inside the delivery band. 1865 and 280 stay on screen.
- **Number caution:** coal-saving figures for Watt's engine range from 60% to 75% less fuel;
  the script says "less than half the coal", which every source supports. Google's token
  figures are company statements and are already dated (later events report far more).

## Visual inventory

- **The trick to animate twice:** a three-step "rebound" stack. Top: one unit (an engine, or a
  chat answer) with its cost bar; the cost bar shrinks to a third. Middle: the single unit
  multiplies into a grid of twelve. Bottom: every unit's small cost flows into one TOTAL bar
  that grows far past the old single cost. B3 skin: blue engines, gray coal lumps, "COAL PER
  JOB" / "TOTAL COAL". B6 skin: orange answer bubbles, token chips, "PRICE PER ANSWER" /
  "TOKENS PER MONTH". The arrows, the multiply sign and the total bar's outline stay violet.
- **Objects, people, dates and places to show:** 1769 date badge; James Watt name pill; an
  engine schematic with the condenser sliding out to its own box; a coal heap that halves;
  1865 badge and W. S. Jevons pill; a word splitting into token chips; a price bar from $20 to
  $0.07; 9.7T to 480T tokens per month; a data center fed by a coal plant; IEA bars, 415 TWh
  to 945 TWh.
- **Archival images:** none. Every graphic is drawn in Manim.

## Infographic direction (series house style)

Design every visual, header and label for this episode. Earlier episodes are style references,
not sources: nothing from their subject, words, diagrams or sounds may appear here.

- **First-frame motion:** the cover shows a blue engine and an orange answer bubble as a mirrored
  pair. Under each, a small "per job" bar is already shrinking while a long violet total bar
  grows: the paradox in one move before the first word.
- **One focal visual for each beat:** B1 mirrored paradox; B2 engine gains its condenser and its
  coal heap halves; B3 rebound stack (coal); B4 "JEVONS PARADOX" badge over three cause tiles;
  B5 a word splits into tokens, then a price bar collapses; B6 rebound stack (tokens); B7 a coal
  plant powers a data center and its closing date slides later; B8 IEA bars grow; B9 this
  episode's Connection Map.
- **Meaningful change every 2-3 seconds:** shrinking bars, sliding condenser, falling coal,
  multiplying units, filling totals, splitting word, collapsing price, power line pulse,
  growing bars and the final link.
- **Smooth transformations:** B2's halved coal heap becomes B3's per-job cost bar; B5's
  collapsed price bar becomes B6's per-answer cost bar; B9's icons are B1's pair, so the loop
  closes.
- **B3/B6 shared mechanism:** one `rebound` helper with one geometry and one narration clock
  split by `REBOUND_PHASES`. B3 sets `self.rebound_time` once, capped to fit B6, and B6 passes
  the same value; only the skin (color, unit icon, labels) changes.
- **Phone-safe composition:** a tall stack (label, unit row, grid, total, verdict) centered on
  `STAGE_CENTER`, inside the safe area and above the caption band.
- **Symmetry plan:** the safe-area axis. Mirror B1's engine and bubble; center every stack;
  register grids as even rows; keep B8's two bars as a mirrored pair.
- **Closing loop:** the Connection Map's engine and bubble are the cover's, and its violet link
  becomes the cover's total bar on the loop.

## Dialogue delivery plan

- **Hook emphasis and pace:** enter at once; stress "saved" against "burned more", then a small
  turn before "Cheaper AI".
- **Mechanism rhythm:** three even steps (cost less, more places, total grew), the same rhythm in
  B3 and B6 so the ear hears the repeat.
- **Aha / reversal lift:** lift on "Each answer costs less" in B6; a short pause before "Now AI
  feeds coal" in B7.
- **Kicker landing:** slow down on "and the total grew", then a clean, neutral tagline.

## Hooks (write five, keep one)

1. **Watt's steam engine saved coal, and Britain burned more. Cheaper AI does the same.**
2. A 1769 steam engine explains why cheaper AI uses more electricity.
3. Saving coal made Britain burn more coal. AI tokens repeat the pattern.
4. In 1865, a coal book predicted the AI power boom.
5. The more efficient the steam engine, the more coal Britain burned. AI too.

Keep hook 1. It names both worlds, states the paradox with a concrete fuel and country in 15
words, and B3 answers it.

## Spare facts (not used here; they can seed another episode)

- Jevons also showed iron smelting: less coal per ton of iron in Scotland came with a large rise
  in total coal use. A second coal example would compete with the engine.
- Hallmarks on silver (England, from about 1300) × signed "content credentials" on photos: both
  stamp who made a thing and who checked it. A strong candidate for the next AI-era pair.
- DeepSeek's January 2025 release is the event that triggered Nadella's post; it is a story of
  its own.
