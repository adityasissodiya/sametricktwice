"""Carrots × TV Screens: series house-style infographic visuals.

The approved words live only in script.md; this file draws what they describe, with diagrams
made for this episode. Every animation is a share of its beat's narration (b.duration). B3 and
B6 call one light-gate mechanism with the same geometry and the same clock: a TV pixel in B6
replays Lehmann's crossed-filter test from B3, with voltage in place of heat.
"""

from kit import *

AXIS = STAGE_CENTER[0]

# B3 and B6 share these: one stack, one light path, one phase clock; only the skin changes.
GATE_PHASES = (0.20, 0.40, 0.10, 0.18, 0.12)  # build, light passes, control arrives, rods turn, verdict
# The shares follow the three sentences of B3 and B6: setup, light passes, control switches it off.
GATE_MAX = 9.0  # seconds: the replay must also fit B6's line (about 9.8 s)
ROD_ROWS, ROD_COLS = 3, 6
LINED_UP = PI / 4  # every rod starts at the same tilt: in line
HEAT_SKIN = {"skin_id": "heat", "shade": A_COLOR, "knob_word": "HEAT", "lit_word": "LIGHT PASSES",
             "dark_word": "LIGHT STOPS", "sink": "VIEW"}
VOLT_SKIN = {"skin_id": "voltage", "shade": B_COLOR, "knob_word": "VOLTAGE", "lit_word": "PIXEL ON",
             "dark_word": "PIXEL OFF", "sink": "PIXEL"}


def scrambled(seed=1889):
    """Random tilts for rods that heat has knocked out of line."""
    rng = np.random.default_rng(seed)
    return [float(a) for a in rng.uniform(-PI / 2, PI / 2, ROD_ROWS * ROD_COLS)]


class Episode(ShortScene):
    """Nine beats; every layout keyframe declares its alignment intent before it moves."""

    # --- drawings made for this episode ---------------------------------------------------

    def carrot(self, color=A_COLOR):
        """A carrot root with growth rings and three leaves; the root is index 0."""
        root = Polygon([-0.38, 0.55, 0], [0.38, 0.55, 0], [0.06, -1.0, 0], [-0.06, -1.0, 0],
                       fill_color=color, fill_opacity=0.30, stroke_color=color, stroke_width=4)
        rings = VGroup(*[Line([-0.30 + 0.07 * i, y, 0], [0.08 - 0.03 * i, y - 0.05, 0], color=color, stroke_width=3)
                         for i, y in enumerate((0.25, -0.12, -0.46))])
        leaves = VGroup(*[Ellipse(width=0.22, height=0.62, fill_color=color, fill_opacity=0.18, stroke_color=color,
                                  stroke_width=3).rotate(a).move_to([x, 0.86, 0])
                          for x, a in ((-0.20, 0.45), (0.0, 0.0), (0.20, -0.45))])
        return VGroup(root, rings, leaves)

    def television(self, color=B_COLOR):
        """A flat TV front: bezel, glowing screen area (index 1) and a short stand."""
        bezel = RoundedRectangle(corner_radius=0.10, width=2.0, height=1.3, fill_color=BG, fill_opacity=1,
                                 stroke_color=color, stroke_width=5)
        glass_area = RoundedRectangle(corner_radius=0.06, width=1.7, height=1.0, fill_color=color,
                                      fill_opacity=0.22, stroke_width=0)
        stand = VGroup(Line([0, -0.65, 0], [0, -0.88, 0], color=color, stroke_width=5),
                       Line([-0.42, -0.88, 0], [0.42, -0.88, 0], color=color, stroke_width=5))
        return VGroup(bezel, glass_area, stand)

    def board(self, drawing, color):
        """A square plate for a world's icon, so both worlds read as a matched pair."""
        plate = RoundedRectangle(corner_radius=0.26, width=2.3, height=2.3, fill_color=color,
                                 fill_opacity=0.10, stroke_color=color, stroke_width=4)
        drawing.scale_to_fit_height(1.45).move_to(plate)
        return VGroup(plate, drawing)

    def rod(self, angle=LINED_UP, length=0.38, color=LINK_COLOR, width=7):
        return Line(LEFT * length / 2, RIGHT * length / 2, color=color, stroke_width=width).rotate(angle)

    def slatted(self, width, vertical, label):
        """A polarizing filter seen edge-on as a slatted strip; vertical slats cross horizontal ones."""
        strip = RoundedRectangle(corner_radius=0.10, width=width, height=0.46, fill_color=FAINT, fill_opacity=0.8,
                                 stroke_color=MUTED, stroke_width=3)
        if vertical:
            slats = VGroup(*[Line([x, -0.16, 0], [x, 0.16, 0], color=MUTED, stroke_width=3)
                             for x in np.linspace(-width / 2 + 0.25, width / 2 - 0.25, 9)])
        else:
            slats = VGroup(*[Line([-width / 2 + 0.18, y, 0], [width / 2 - 0.18, y, 0], color=MUTED, stroke_width=3)
                             for y in (-0.10, 0.0, 0.10)])
        word = text(label, 18, MUTED, BOLD).next_to(strip, RIGHT, buff=0.18)
        return VGroup(strip, slats, word)

    def flame(self, color=A_COLOR):
        outer = VMobject(fill_color=color, fill_opacity=0.30, stroke_color=color, stroke_width=4)
        outer.set_points_smoothly([[0, 0.62, 0], [0.26, 0.15, 0], [0.30, -0.25, 0], [0, -0.48, 0], [-0.30, -0.25, 0],
                                   [-0.26, 0.15, 0], [0, 0.62, 0]])
        inner = outer.copy().scale(0.5).shift(0.12 * DOWN).set_fill(color, opacity=0.6)
        return VGroup(outer, inner)

    def battery(self, color=B_COLOR):
        body = RoundedRectangle(corner_radius=0.08, width=0.62, height=1.0, fill_color=color, fill_opacity=0.25,
                                stroke_color=color, stroke_width=4)
        cap = Rectangle(width=0.24, height=0.12, fill_color=color, fill_opacity=0.8, stroke_width=0).next_to(body, UP, buff=0)
        plus = VGroup(Line([-0.11, 0.2, 0], [0.11, 0.2, 0]), Line([0, 0.09, 0], [0, 0.31, 0])).set_stroke(INK, 4)
        minus = Line([-0.11, -0.22, 0], [0.11, -0.22, 0]).set_stroke(INK, 4)
        return VGroup(body, cap, plus, minus)

    def sample(self, state):
        """Reinitzer's compound: a solid crystal, a cloudy liquid full of rods, or a clear liquid."""
        if state == 0:
            shape = RegularPolygon(6, fill_color=INK, fill_opacity=0.75, stroke_color=INK, stroke_width=3).scale(0.62)
            return VGroup(shape)
        drop = Ellipse(width=1.9, height=0.95, stroke_color=INK, stroke_width=4,
                       fill_color=LINK_COLOR if state == 1 else BG, fill_opacity=0.32 if state == 1 else 0.0)
        if state == 2:
            return VGroup(drop)
        specks = VGroup(*[self.rod(LINED_UP, 0.22, width=5).move_to([x, y, 0])
                          for x in (-0.55, -0.15, 0.25, 0.6) for y in (-0.15, 0.15)])
        return VGroup(drop, specks)

    # --- the shared mechanism (B3 and B6) ---------------------------------------------------

    def light_gate_parts(self, skin, turns):
        """The trick laid out identically for every skin: light, a filter, the rod cell, a crossed
        filter and the output. Only the control, its color and the words change."""
        shade = skin["shade"]
        lamp = VGroup(Circle(radius=0.22, fill_color=INK, fill_opacity=0.95, stroke_width=0),
                      *[Line(0.30 * np.array([np.cos(a), np.sin(a), 0]), 0.46 * np.array([np.cos(a), np.sin(a), 0]),
                             color=INK, stroke_width=4) for a in np.linspace(0, TAU, 8, endpoint=False)])
        lamp.move_to([AXIS, 4.25, 0])
        upper = self.slatted(3.4, False, "FILTER").move_to([AXIS + 0.42, 3.40, 0])
        cell = RoundedRectangle(corner_radius=0.16, width=3.4, height=1.55, fill_color=FAINT, fill_opacity=0.55,
                                stroke_color=LINK_COLOR, stroke_width=3).move_to([AXIS, 2.0, 0])
        rods = VGroup(*[self.rod() for _ in range(ROD_ROWS * ROD_COLS)])
        rods.arrange_in_grid(rows=ROD_ROWS, cols=ROD_COLS, buff=(0.16, 0.12)).move_to(cell)
        lower = self.slatted(3.4, True, "CROSSED").move_to([AXIS + 0.53, 0.62, 0])
        screen_box = RoundedRectangle(corner_radius=0.14, width=3.0, height=0.95, fill_color=FAINT, fill_opacity=0.9,
                                      stroke_color=shade, stroke_width=4).move_to([AXIS, -0.60, 0])
        sink_word = text(skin["sink"], 20, shade, BOLD).move_to(screen_box)
        lit = pill(skin["lit_word"], LINK_COLOR, size=24).move_to([AXIS, -1.62, 0])
        dark = pill(skin["dark_word"], LINK_COLOR, size=24).move_to(lit)
        knob = (self.flame() if skin["skin_id"] == "heat" else self.battery()).scale_to_fit_height(1.0)
        knob.move_to([AXIS - 2.62, 2.12, 0])
        knob_label = text(skin["knob_word"], 18, shade, BOLD).next_to(knob, DOWN, buff=0.14)
        with self.alignment_loop(f"Light gate, {skin['skin_id']}") as align:
            align.centered(lamp, name="light source")
            align.centered(cell, name="rod cell")
            align.centered(screen_box, name="output")
            align.centered(lit, name="verdict")
            align.inside_safe(VGroup(lamp, upper, cell, lower, screen_box, lit, knob, knob_label), padding=0.12)
        rods.move_to(cell)
        sink_word.move_to(screen_box)
        push = Arrow(knob.get_right(), cell.get_left(), buff=0.10, color=shade, stroke_width=6,
                     max_tip_length_to_length_ratio=0.35)
        beam_hi = Line(lamp.get_bottom(), lower[0].get_bottom(), color=INK, stroke_width=6).set_opacity(0.55)
        beam_lo = Line(lower[0].get_bottom(), screen_box.get_top(), color=INK, stroke_width=6).set_opacity(0.55)
        spark = Dot(lamp.get_bottom(), radius=0.10, color=INK)
        blocked = Dot(lamp.get_bottom(), radius=0.10, color=INK)
        through = Line(lamp.get_bottom(), screen_box.get_center())
        halt = Line(lamp.get_bottom(), lower[0].get_top())
        for part in (beam_hi, beam_lo):
            part.set_z_index(-1)
        return {"lamp": lamp, "upper": upper, "cell": cell, "rods": rods, "lower": lower, "screen_box": screen_box,
                "sink_word": sink_word, "lit": lit, "dark": dark, "knob": knob, "knob_label": knob_label,
                "push": push, "beam_hi": beam_hi, "beam_lo": beam_lo, "spark": spark, "blocked": blocked,
                "through": through, "halt": halt, "turns": turns}

    def light_gate(self, g, run_time, intro=()):
        """Light passes the lined-up rods; then the control turns them and the light stops. One
        narration-relative clock (run_time) is split by GATE_PHASES, so B6 replays B3."""
        t = [run_time * share for share in GATE_PHASES]
        self.play(*[FadeIn(m) for m in intro], FadeIn(g["lamp"], scale=0.8), FadeIn(g["upper"]), FadeIn(g["cell"]),
                  FadeIn(g["rods"]), FadeIn(g["lower"]), FadeIn(g["screen_box"]), FadeIn(g["sink_word"]),
                  run_time=t[0])
        self.sfx("tap.wav", -12)
        self.add(g["spark"])
        self.play(MoveAlongPath(g["spark"], g["through"]), Create(g["beam_hi"]), Create(g["beam_lo"]),
                  g["screen_box"].animate.set_fill(INK, opacity=0.85), FadeIn(g["lit"], shift=0.1 * UP),
                  run_time=t[1])
        self.sfx("spark.wav", -14)
        self.play(FadeIn(g["knob"], scale=0.6), FadeIn(g["knob_label"]), GrowArrow(g["push"]), FadeOut(g["spark"]),
                  run_time=t[2])
        self.sfx("shutter.wav", -15)
        self.add(g["blocked"])
        self.play(*[Rotate(r, angle=a - LINED_UP, about_point=r.get_center()) for r, a in zip(g["rods"], g["turns"])],
                  MoveAlongPath(g["blocked"], g["halt"]), FadeOut(g["beam_lo"]),
                  g["screen_box"].animate.set_fill(FAINT, opacity=0.9), run_time=t[3])
        self.sfx("ping.wav", -15)
        self.play(ReplacementTransform(g["lit"], g["dark"]), Indicate(g["lower"][1], color=INK, scale_factor=1.06),
                  run_time=t[4])

    # --- the nine beats -----------------------------------------------------------------------

    def construct(self):
        # B1: the cover. A carrot and a TV mirror each other while the rods between them turn
        # into line and a light dot crosses from one world to the other.
        with self.beat("B1") as b:
            words = VGroup(title("CARROT LAB", 50, A_COLOR), title("→", 50, LINK_COLOR), title("TV", 50, B_COLOR))
            words.arrange(RIGHT, buff=0.32).move_to([AXIS, 4.45, 0])
            root = self.board(self.carrot(), A_COLOR).move_to([AXIS - 1.62, 2.45, 0])
            telly = self.board(self.television(), B_COLOR).move_to([AXIS + 1.62, 2.45, 0])
            with self.alignment_loop("B1 cover") as align:
                align.centered(words, name="carrot lab to TV")
                align.mirror_pair(root, telly, y=2.45, min_gap=0.4, name="carrot and TV plates")
                align.inside_safe(VGroup(words, root, telly), padding=0.12)
            names = VGroup(text("CARROTS", 24, A_COLOR, BOLD), text("TV SCREENS", 24, B_COLOR, BOLD))
            for name, plate in zip(names, (root, telly)):
                name.set_x(plate.get_x()).set_y(plate.get_bottom()[1] - 0.38)
            strip = RoundedRectangle(corner_radius=0.16, width=5.4, height=0.95, fill_color=FAINT, fill_opacity=0.55,
                                     stroke_color=LINK_COLOR, stroke_width=3).move_to([AXIS, -0.35, 0])
            tilts = scrambled(seed=4)[:9]
            rods = VGroup(*[self.rod(a, 0.46) for a in tilts]).arrange(RIGHT, buff=0.18).move_to(strip)
            caption = text("LIQUID CRYSTAL", 24, LINK_COLOR, BOLD).next_to(strip, DOWN, buff=0.25)
            with self.alignment_loop("B1 rod strip") as align:
                align.centered(VGroup(strip, caption), name="rod strip")
                align.inside_safe(VGroup(words, root, telly, names, strip, caption), padding=0.12)
            rods.move_to(strip)
            glint = Dot(radius=0.11, color=INK).move_to(strip.get_left() + 0.1 * RIGHT)
            across = Line(strip.get_left() + 0.1 * RIGHT, strip.get_right() + 0.1 * LEFT)

            self.add(words, root, telly, names, strip, rods, glint)
            # linear from frame zero: an eased start would leave the first quarter-second still
            self.play(*[Rotate(r, angle=LINED_UP - a, about_point=r.get_center(), rate_func=linear)
                        for r, a in zip(rods, tilts)],
                      MoveAlongPath(glint, across, rate_func=linear), run_time=0.46 * b.duration)
            self.sfx("whoosh.wav", -14)
            self.play(FadeIn(caption, shift=0.1 * UP), telly[1][1].animate.set_fill(B_COLOR, opacity=0.6),
                      glint.animate.move_to(telly.get_center()), run_time=0.30 * b.duration)
            self.play(Indicate(words[2], color=B_COLOR, scale_factor=1.12), run_time=0.14 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B2: 1888. Cholesterol from a carrot becomes a sample; the thermometer climbs past two
        # marks and the sample melts twice: solid, cloudy, clear.
        with self.beat("B2") as b:
            header = beat_header(2, "A BOTANIST'S PUZZLE", A_COLOR)
            names = VGroup(date_badge("1888", A_COLOR), pill("F. REINITZER", A_COLOR, size=24)).arrange(RIGHT, buff=0.45)
            names.move_to([AXIS, 4.0, 0])
            root = self.carrot().scale_to_fit_height(1.55).move_to([AXIS - 1.75, 2.35, 0])
            vial = pill("CHOLESTEROL", A_COLOR, size=24).move_to([AXIS + 1.25, 2.35, 0])
            track = Line([AXIS - 2.6, -1.05, 0], [AXIS + 2.6, -1.05, 0], color=MUTED, stroke_width=10)
            with self.alignment_loop("B2 carrot and thermometer") as align:
                align.centered(names, name="date and botanist")
                align.centered(track, name="thermometer")
                align.inside_safe(VGroup(header, names, root, vial, track), padding=0.14)
            hop = Arrow(root.get_right(), vial.get_left(), buff=0.2, color=A_COLOR, stroke_width=6,
                        max_tip_length_to_length_ratio=0.25)
            x0, x1 = track.get_start()[0], track.get_end()[0]
            mark_x = [x0 + (x1 - x0) * f for f in (0.42, 0.78)]
            marks = VGroup(*[Line([x, -1.32, 0], [x, -0.78, 0], color=INK, stroke_width=4) for x in mark_x])
            temps = VGroup(text("145.5 °C", 20, MUTED, BOLD), text("178.5 °C", 20, MUTED, BOLD))
            for temp, x in zip(temps, mark_x):
                temp.move_to([x, -1.62, 0])
            mercury = Rectangle(width=0.2, height=0.16, fill_color=INK, fill_opacity=0.9, stroke_width=0)
            mercury.move_to([x0 + 0.1, -1.05, 0])
            states = [self.sample(i).move_to([AXIS, 0.55, 0]) for i in range(3)]
            words = [text(w, 22, INK, BOLD).move_to([AXIS, -0.25, 0]) for w in ("SOLID", "CLOUDY", "CLEAR")]
            blob, word = states[0], words[0]

            self.add(header)
            self.play(FadeIn(names, shift=0.2 * DOWN), FadeIn(root, shift=0.2 * RIGHT), FadeIn(track), FadeIn(marks),
                      FadeIn(temps), FadeIn(mercury), FadeIn(blob), FadeIn(word), run_time=0.14 * b.duration)
            self.sfx("swipe.wav", -15)
            self.play(GrowArrow(hop), TransformFromCopy(root, vial), run_time=0.18 * b.duration)
            self.sfx("ticks.wav", -15)
            self.play(mercury.animate.stretch_to_fit_width(mark_x[0] - x0 + 0.05, about_edge=LEFT),
                      Transform(blob, states[1]), Transform(word, words[1]), run_time=0.20 * b.duration)
            self.play(mercury.animate.stretch_to_fit_width(mark_x[1] - x0 + 0.05, about_edge=LEFT),
                      Transform(blob, states[2]), Transform(word, words[2]), run_time=0.20 * b.duration)
            self.play(Indicate(marks, color=LINK_COLOR, scale_factor=1.2), run_time=0.12 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B3: Lehmann's crossed filters. Lined-up rods turn the light through; heat scrambles them
        # and the view goes dark.
        with self.beat("B3") as b:
            header = beat_header(3, "OTTO LEHMANN'S TEST", A_COLOR)
            gate = self.light_gate_parts(HEAT_SKIN, scrambled())
            self.gate_time = min(GATE_MAX, 0.90 * b.duration)
            self.light_gate(gate, self.gate_time, intro=[header])
            self.hold(b)
        self.clear_stage(0.2)

        # B4: three panels: a crystal holds still, a liquid crystal drifts but stays in line, a
        # liquid tumbles. The badge changes from Lehmann's name to today's.
        with self.beat("B4") as b:
            header = beat_header(4, "A NEW STATE", LINK_COLOR)
            old_name = title("FLOWING CRYSTALS", 48, LINK_COLOR).move_to([AXIS, 3.95, 0])
            new_name = title("LIQUID CRYSTALS", 48, LINK_COLOR).move_to(old_name)
            tiles = VGroup(*[RoundedRectangle(corner_radius=0.18, width=1.85, height=2.6, fill_color=FAINT,
                                              fill_opacity=0.55, stroke_color=LINK_COLOR, stroke_width=2)
                             for _ in range(3)]).arrange(RIGHT, buff=0.28).move_to([AXIS, 1.55, 0])
            with self.alignment_loop("B4 states of matter") as align:
                align.centered(old_name, name="badge")
                align.even_row(tiles, gap=0.28, name="three states")
                align.inside_safe(VGroup(header, old_name, tiles), padding=0.14)
            new_name.move_to(old_name)
            lattice = VGroup(*[self.rod(PI / 2, 0.42) for _ in range(9)]).arrange_in_grid(3, 3, buff=(0.30, 0.18))
            flowing = VGroup(*[self.rod(LINED_UP, 0.42) for _ in range(9)]).arrange_in_grid(3, 3, buff=(0.22, 0.24))
            jumble_tilts = scrambled(seed=12)[:9]
            jumble = VGroup(*[self.rod(a, 0.42) for a in jumble_tilts]).arrange_in_grid(3, 3, buff=(0.22, 0.24))
            for group, tile in zip((lattice, flowing, jumble), tiles):
                group.move_to(tile)
            labels = VGroup(text("CRYSTAL", 20, MUTED, BOLD), text("LIQUID CRYSTAL", 20, LINK_COLOR, BOLD),
                            text("LIQUID", 20, MUTED, BOLD))
            for label, tile in zip(labels, tiles):
                label.next_to(tile, DOWN, buff=0.22)
            rng = np.random.default_rng(7)
            drift = [0.22 * np.array([rng.uniform(-1, 1), rng.uniform(-1, 1), 0]) for _ in range(9)]

            self.add(header)
            self.play(FadeIn(old_name, scale=0.94), FadeIn(tiles), FadeIn(lattice), FadeIn(flowing), FadeIn(jumble),
                      FadeIn(labels), run_time=0.24 * b.duration)
            self.sfx("wash.wav", -16)
            self.play(*[r.animate.shift(d) for r, d in zip(flowing, drift)],
                      *[Rotate(r, angle=1.4 * (i % 3 - 1) + 0.6, about_point=r.get_center()) for i, r in enumerate(jumble)],
                      run_time=0.34 * b.duration)
            self.play(Transform(old_name, new_name), Indicate(labels[1], color=LINK_COLOR, scale_factor=1.08),
                      run_time=0.28 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B5: a century later. A deep tube TV seen from the side shrinks into Sharp's 2.7 cm panel,
        # which turns to face us.
        with self.beat("B5") as b:
            header = beat_header(5, "A CENTURY LATER", B_COLOR)
            names = VGroup(date_badge("1988", B_COLOR), pill("SHARP · 14-INCH", B_COLOR, size=24)).arrange(RIGHT, buff=0.45)
            names.move_to([AXIS, 4.0, 0])
            deep = Polygon([AXIS - 1.6, 2.95, 0], [AXIS - 1.6, 0.55, 0], [AXIS + 1.7, 1.2, 0], [AXIS + 1.7, 2.3, 0],
                           fill_color=MUTED, fill_opacity=0.25, stroke_color=MUTED, stroke_width=4)
            face = Line([AXIS - 1.6, 2.95, 0], [AXIS - 1.6, 0.55, 0], color=B_COLOR, stroke_width=8)
            span = DoubleArrow([AXIS - 1.6, -0.2, 0], [AXIS + 1.7, -0.2, 0], buff=0, color=MUTED, stroke_width=4,
                               tip_length=0.2)
            depth_word = text("DEEP BOX", 22, MUTED, BOLD).next_to(span, DOWN, buff=0.18)
            with self.alignment_loop("B5 deep box") as align:
                align.centered(names, name="date and maker")
                align.inside_safe(VGroup(header, names, deep, span, depth_word), padding=0.14)
            thin = Rectangle(width=0.16, height=2.4, fill_color=B_COLOR, fill_opacity=0.5, stroke_color=B_COLOR,
                             stroke_width=4).move_to([AXIS, 1.75, 0])
            thin_span = DoubleArrow([AXIS - 0.35, -0.2, 0], [AXIS + 0.35, -0.2, 0], buff=0, color=B_COLOR,
                                    stroke_width=4, tip_length=0.16)
            thin_word = text("2.7 CM", 24, B_COLOR, BOLD).move_to(depth_word)
            front = self.television().scale_to_fit_width(3.6).move_to([AXIS, 1.75, 0])
            hint = VGroup(*[self.rod(LINED_UP, 0.3, width=6) for _ in range(8)]).arrange(RIGHT, buff=0.12)
            hint.move_to(front[1])
            with self.alignment_loop("B5 thin panel") as align:
                align.centered(VGroup(front, thin_span, thin_word), name="flat TV")
                align.inside_safe(VGroup(header, names, front, thin_span, thin_word), padding=0.14)

            self.add(header)
            self.play(FadeIn(deep), Create(face), GrowFromCenter(span), FadeIn(depth_word), run_time=0.14 * b.duration)
            self.sfx("swipe.wav", -15)
            self.play(ReplacementTransform(VGroup(deep, face), thin), ReplacementTransform(span, thin_span),
                      ReplacementTransform(depth_word, thin_word), run_time=0.30 * b.duration)
            self.play(FadeIn(names, shift=0.2 * DOWN), run_time=0.14 * b.duration)
            self.play(ReplacementTransform(thin, front), FadeIn(hint), run_time=0.26 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B6: the same stack, the same clock: a pixel, with voltage in place of heat. The rods
        # stand upright instead of scattering, and the pixel goes dark.
        with self.beat("B6") as b:
            header = beat_header(6, "INSIDE EVERY PIXEL", B_COLOR)
            gate = self.light_gate_parts(VOLT_SKIN, [PI / 2] * (ROD_ROWS * ROD_COLS))
            self.light_gate(gate, self.gate_time, intro=[header])
            self.hold(b)
        self.clear_stage(0.2)

        # B7: the reverse problem. Reinitzer's band sits in oven heat; the room-temperature band
        # that screens needed slides down the scale.
        with self.beat("B7") as b:
            header = beat_header(7, "TOO HOT FOR A TV", LINK_COLOR)
            low, high, y_low, y_high = 0.0, 200.0, -1.75, 3.95
            spine_x = AXIS - 1.75

            def at(celsius):
                return y_low + (y_high - y_low) * (celsius - low) / (high - low)

            spine = Line([spine_x, y_low, 0], [spine_x, y_high, 0], color=MUTED, stroke_width=6)
            notches = VGroup(*[Line([spine_x - 0.12, at(c), 0], [spine_x + 0.12, at(c), 0], color=MUTED, stroke_width=4)
                               for c in (0, 50, 100, 150, 200)])
            numbers = VGroup(*[text(f"{c} °C", 18, MUTED, BOLD).next_to([spine_x - 0.15, at(c), 0], LEFT, buff=0.08)
                               for c in (0, 50, 100, 150, 200)])
            room = DashedLine([spine_x, at(20), 0], [AXIS + 2.55, at(20), 0], color=B_COLOR, dash_length=0.12,
                              stroke_width=3)
            room_word = text("ROOM", 20, B_COLOR, BOLD).next_to(room, UP, buff=0.08).align_to(room, RIGHT)
            with self.alignment_loop("B7 temperature scale") as align:
                align.inside_safe(VGroup(header, spine, notches, numbers, room, room_word), padding=0.14)
            hot = Rectangle(width=2.2, height=at(178.5) - at(145.5), fill_color=LINK_COLOR, fill_opacity=0.6,
                            stroke_color=LINK_COLOR, stroke_width=3)
            hot.move_to([spine_x + 1.45, (at(145.5) + at(178.5)) / 2, 0])
            hot_word = VGroup(text("REINITZER, 1888", 20, A_COLOR, BOLD), text("OVEN HEAT", 20, MUTED, BOLD))
            hot_word.arrange(DOWN, buff=0.08).next_to(hot, DOWN, buff=0.15)
            cool = Rectangle(width=2.2, height=at(35.0) - at(22.5), fill_color=LINK_COLOR, fill_opacity=0.6,
                             stroke_color=LINK_COLOR, stroke_width=3)
            cool.move_to([spine_x + 1.45, (at(22.5) + at(35.0)) / 2, 0])
            cool_word = VGroup(text("GRAY'S TEAM, 1973", 20, B_COLOR, BOLD), text("22-35 °C", 20, MUTED, BOLD))
            cool_word.arrange(DOWN, buff=0.08).next_to(cool, UP, buff=0.3)
            with self.alignment_loop("B7 bands") as align:
                align.inside_safe(VGroup(hot, hot_word, cool, cool_word, room_word), padding=0.14)

            self.add(header)
            self.play(Create(spine), FadeIn(notches), FadeIn(numbers), Create(room), FadeIn(room_word),
                      run_time=0.16 * b.duration)
            self.sfx("ticks.wav", -15)
            self.play(GrowFromEdge(hot, LEFT), FadeIn(hot_word), run_time=0.22 * b.duration)
            self.play(ReplacementTransform(hot, cool), ReplacementTransform(hot_word, cool_word),
                      run_time=0.34 * b.duration)
            self.play(Indicate(cool, color=LINK_COLOR, scale_factor=1.06), run_time=0.12 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B8: a field of TVs: rods fill all but one, the single OLED set.
        with self.beat("B8") as b:
            header = beat_header(8, "TVS TODAY", B_COLOR)
            sets = VGroup(*[self.television(B_COLOR if i != 13 else MUTED).scale(0.48) for i in range(20)])
            sets.arrange_in_grid(rows=4, cols=5, buff=(0.22, 0.32)).move_to([AXIS, 1.65, 0])
            legend = text("LIQUID CRYSTAL TVS", 22, LINK_COLOR, BOLD).next_to(sets, DOWN, buff=0.35)
            with self.alignment_loop("B8 field of TVs") as align:
                align.centered(VGroup(sets, legend), name="TV field")
                align.inside_safe(VGroup(header, sets, legend), padding=0.14)
            source = self.rod(LINED_UP, 0.32).move_to([AXIS, 4.2, 0])
            fills = VGroup(*[self.rod(LINED_UP, 0.32, width=6).move_to(s[1]) for i, s in enumerate(sets) if i != 13])
            oled = text("OLED", 16, MUTED, BOLD).move_to(sets[13][1])

            self.add(header)
            self.play(LaggedStart(*[FadeIn(s) for s in sets], lag_ratio=0.03), FadeIn(source), run_time=0.22 * b.duration)
            self.sfx("pixels.wav", -14)
            self.play(LaggedStart(*[TransformFromCopy(source, f) for f in fills], lag_ratio=0.04),
                      run_time=0.46 * b.duration)
            self.play(FadeIn(oled), FadeIn(legend, shift=0.1 * UP), FadeOut(source), run_time=0.20 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B9: this episode's Connection Map; its plates are B1's, so the loop closes.
        with self.beat("B9") as b:
            header = beat_header(9, "CRYSTAL CONNECTION", LINK_COLOR)
            self.end_card(
                run_time=0.88 * b.duration,
                title=False,
                both_ways=True,
                tagline=("SAME TRICK", "TWO WORLDS"),
                sound="ping.wav",
                intro=[header],
                icons=(self.board(self.carrot(), A_COLOR), self.board(self.television(), B_COLOR)),
            )
            self.hold(b)

        self.wait(0.25)
