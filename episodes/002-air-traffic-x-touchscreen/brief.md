# 002-air-traffic-x-touchscreen · brief

**Pair:** A = Air traffic control · B = Touchscreen
**The bridge (one sentence):** Phone screens feel your finger with the same trick a 1965
radar lab used for air traffic control: a finger changes the charge on a wire.
**A helped B by:** E. A. Johnson's capacitive touch display (Royal Radar Establishment,
Malvern, 1965), built to let controllers pick items on a radar computer's screen.
**B helped A by:** touchscreens came back to the control room. NATS replaced paper flight
strips with touch-screen electronic strips (EXCDS) at Heathrow, Gatwick and London
Terminal Control in 2018.

## Claim ledger

| # | Claim, as said (beat) | Source 1 | Source 2 | Confidence |
|---|---|---|---|---|
| C1 | In 1965 Eric Johnson worked at a British radar lab (B1, B2) | [US patent 3,482,241 "Touch Displays"](https://patents.google.com/patent/US3482241A/en), inventor Eric Arthur Johnson, UK priority 5 Aug 1965 | [Bill Buxton, input-device timeline](https://billbuxton.com/inputTimeline.html): "E.A. Johnson of the Royal Radar Establishment, Malvern, UK" (1965) | high |
| C2 | He wanted controllers to pick a flight on the screen with one touch (B2) | [US 3,482,241](https://patents.google.com/patent/US3482241A/en): air traffic control flight-plan amendments; the operator "touches the place on the cathode ray tube screen where the item is displayed" to select it | [SEECheck](https://seecheck.org/?p=6615) quoting Johnson (1965, *Electronics Letters* 1(8)): a device was "programmed for air traffic control tasks" | high |
| C3 | He put thin wires across the screen (B3) | Johnson 1965 via [SEECheck](https://seecheck.org/?p=6615): "wires, sensitive to the touch of a finger, on the front side of the cathode ray tube" | [US 3,482,241](https://patents.google.com/patent/US3482241A/en): "electric wires in the screen, one to each site" | high |
| C4 | A finger changes how much charge a wire can hold, and a circuit feels it (B3) | [US 3,482,241](https://patents.google.com/patent/US3482241A/en): the finger's "capacitance to earth ... is sufficient to throw the bridge off balance" | [Wikipedia, Touchscreen](https://en.wikipedia.org/wiki/Touchscreen): Johnson's work was on capacitive touchscreens | high |
| C5 | About forty years later, phone makers removed the keys; the front became a screen (B5) | [Apple press release, 9 Jan 2007](https://www.apple.com/newsroom/2007/01/09Apple-Reinvents-the-Phone-with-iPhone/): "a large multi-touch display ... control iPhone with just their fingers", replacing "small plastic keyboards" | [Wikipedia, Touchscreen](https://en.wikipedia.org/wiki/Touchscreen): LG Prada (May 2007) was the first phone with a capacitive touchscreen, shortly before the iPhone | high |
| C6 | A grid of clear wires under the glass; a finger takes charge where two wires cross, and the phone finds the spot (B6) | [Apple patent US 7,663,607](https://patents.google.com/patent/US7663607B2/en) (filed 2004): transparent driving and sensing lines on two layers form "a capacitive coupling node"; a finger "steals charge" | [Wikipedia, Touchscreen](https://en.wikipedia.org/wiki/Touchscreen): the capacitance change "at every intersection on the grid" locates touches | high |
| C7 | Touchscreens returned to air traffic control; many British controllers now move flight strips with a touch, not on paper (B7) | [Airport Technology, Apr 2018](https://www.airport-technology.com/news/nats-install-electronic-flight-strip-system-london-terminal): NATS installs EXCDS "in place of paper strips" for Heathrow, Gatwick and London airspace | [The Points Guy, Apr 2018](https://thepointsguy.com/news/british-air-traffic-control-is-going-digital-the-us-is-not): Heathrow and Gatwick move from paper strips to EXCDS on "touch-sensitive display screens" | high |
| C8 | Most phones and tablets feel your finger this way (B8) | [Bill Buxton](https://billbuxton.com/inputTimeline.html): Johnson used "capacitive sensing - as do most consumer devices today" | [Wikipedia, Touchscreen](https://en.wikipedia.org/wiki/Touchscreen): capacitive multi-touch screens in mobile devices | high |
| F1 | "Every tap ... uses an idea from a 1965 radar lab", "Air traffic control taught screens to feel a finger" (B1, B9) | framing: the capacitive finger-touch display was first described at the Royal Radar Establishment in 1965 (C1-C4) and phones use capacitive sensing (C6, C8) | | n/a |
| F2 | "That is the trick: touch, charge, find" (B4) | framing, not a fact claim: a three-word name for the mechanism in C3-C4 (a finger touches a wire, changes its charge, and the circuit finds which wire) | | n/a |

## Myth check

- "CERN invented the touchscreen (1973)": CERN's Beck and Stumpe screen came eight years
  after Johnson. Do not call CERN first.
- "Johnson's screen used a transparent ITO coating": several web articles say so, but his
  paper and patent describe wires on the screen face. Show wires.
- "UK controllers used it until the 1990s" / "it was not used until the 1990s": web articles
  contradict each other and no primary source settles it. Say nothing about deployment dates.
- "The iPhone had the first capacitive touchscreen": the LG Prada came first (May 2007). Say
  "phone makers", not "Apple invented".
- "Hurst invented the touchscreen (1971)": that was a resistive sensor, after Johnson.

## Visual inventory

- The trick (plays twice): a screen panel, sensing wires, a finger coming in, violet charge
  lines into the fingertip, a meter that jumps for one line, then the touched spot lights.
  B3: radar screen with four wires and flight labels. B6: phone glass with a grid of clear
  wires.
- People and dates: Eric Johnson 1965 (name in narration only), phones 2007, NATS 2018
  (not shown). Use date badges; no photos.
- Archival images: none. Every graphic is drawn in Manim.
- Brand names: none on screen. Flight labels on the radar are made-up examples.

## Infographic direction (series house style)

- First-frame motion: the cover is on screen at frame 0. AIR TRAFFIC × TOUCHSCREEN sits over
  a phone whose screen is a radar scope, and its sweep is already turning.
- One focal visual per beat: phone radar (B1), radar scope with moving blips (B2), wired
  screen (B3), three cards (B4), keypad phone turning into a full screen (B5), phone glass
  grid (B6), touch flight strips replacing paper (B7), field of devices (B8), Connection
  Map (B9).
- Transformations instead of cuts: the keypad melts into the screen, the paper strip becomes
  an electronic strip, two arrows become one link.
- B3/B6 shared mechanism: `Episode.trick()` with `RADAR_SKIN` and `PHONE_SKIN`. Same panel,
  finger path, charge lines, meter and timing (`self.trick_time`); only the material,
  wire layout, labels and color change. Charge stays violet in both.
- Phone-safe composition: diagrams on the safe-area axis x = -0.4; captions stay clear.
- Symmetry plan: B1 title/phone column (gap 0.30), B2 date/place pair and centered scope,
  B3/B6 meter + panel as an even row, B4 and B6 card rows, B5 centered phone, B7 mirrored
  radar/phone pair and centered strip board, B8 device rows in an even column, B9 map
  centered with its tagline. 12 registered loops, all passing.
- Closing loop: the map ends with the two worlds joined. B1 opens on a phone that already
  holds a radar, so the replay flows straight back.

## Dialogue delivery plan

The approved VO never changes; each beat's `NOTE:` in script.md carries its direction.

- Hook emphasis and pace: stress "every tap" and "1965".
- Dates and names: a small pocket of space around "In 1965" and "Eric Johnson".
- Mechanism rhythm: "touch, charge, find" as three separate beats.
- Aha / reversal lift: recognition on "the same trick" (B6); a turn on "Then touchscreens
  returned" (B7).
- Kicker landing: balance the two sentences, pause, land "Same trick, two worlds."

## Hooks

1. Every tap on your phone uses an idea from a 1965 radar lab. (chosen)
2. Your touchscreen was born to guide planes.
3. The first finger touchscreen was built for air traffic control.
4. Before phones, touchscreens helped guide planes.
5. Your phone feels your finger with a trick from a radar lab.

## Spare facts

- Johnson's patent shows a 4 x 4 matrix of touch sites (16 positions), each sensed by its own
  bridge circuit ([US 3,482,241](https://patents.google.com/patent/US3482241A/en)).
- Controllers evaluated it: Orr and Hopkins, "The Role of Touch Display in Air Traffic
  Control", *The Controller* 7 (1968), cited by [Buxton](https://billbuxton.com/inputTimeline.html).
- Apple's iPhone was announced on 9 January 2007; the LG Prada shipped in May 2007 with the
  first capacitive touchscreen on a phone ([Wikipedia](https://en.wikipedia.org/wiki/Touchscreen)).
