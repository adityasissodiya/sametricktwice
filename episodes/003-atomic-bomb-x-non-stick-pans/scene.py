"""Atomic-Bomb Project × Non-Stick Pans: series house-style infographic visuals.

The approved words live only in script.md; this file draws what they describe, with diagrams
made for this episode. Every animation is a share of its beat's narration (b.duration), so
the pictures stay inside the spoken line. B3 and B6 call one PTFE-surface mechanism with the
same geometry and the same clock: the pan in B6 replays the uranium-gas defense from B3.
"""

from kit import *

AXIS = STAGE_CENTER[0]

# B3 and B6 share these: the same surface, atoms, paths and phase timing; only the skin changes.
PTFE_PHASES = (0.22, 0.22, 0.28, 0.14, 0.14)  # build, fall, glance off, verdict, settle
REPLAY_MAX = 4.2  # seconds: the replay must also fit B6's line (about 4.7 s), the shorter one
GAS_SKIN = {"name": "gas", "color": A_COLOR, "base": "PIPE METAL",
            "particles": ("UF₆", "UF₆", "UF₆"), "verdict": "INERT"}
PAN_SKIN = {"name": "pan", "color": B_COLOR, "base": "ALUMINUM PAN",
            "particles": ("OIL", "EGG", "OIL"), "verdict": "LOW-GRIP"}
GLANCE = 0.85 * RIGHT + 1.55 * UP  # where a particle goes after it touches the fluorine row


class Episode(ShortScene):
    """Nine beats; every layout keyframe declares its alignment intent before it moves."""

    # --- drawings made for this episode ---------------------------------------------------

    def pipe_end(self, color=A_COLOR):
        """A pipe joint seen end-on: flange plate, bolts, the violet PTFE gasket ring, the bore
        and the gas inside it. Index 2 is the gasket, index 4 the gas."""
        plate = RoundedRectangle(corner_radius=0.24, width=2.3, height=2.3, fill_color=color,
                                 fill_opacity=0.12, stroke_color=color, stroke_width=4)
        bolts = VGroup(*[Dot([x, y, 0], radius=0.10, color=color)
                         for x in (-0.86, 0.86) for y in (-0.86, 0.86)])
        gasket = Circle(radius=0.80, stroke_color=LINK_COLOR, stroke_width=12)
        bore = Circle(radius=0.58, stroke_color=color, stroke_width=6, fill_color=BG, fill_opacity=1)
        gas = VGroup(*[Dot(0.33 * np.array([np.cos(a), np.sin(a), 0]), radius=0.10, color=color)
                       for a in np.linspace(0, TAU, 8, endpoint=False)])
        return VGroup(plate, bolts, gasket, bore, gas)

    def pan_section(self, color=B_COLOR, stroke=4, fill=0.22):
        """A frying pan cut in half: aluminum wall, handle and the PTFE lining (index 2), which
        follows the inner surface. Callers add the lining only when the story puts it there."""
        wall = Polygon(
            [-1.30, 0.45, 0], [-1.00, -0.45, 0], [1.00, -0.45, 0], [1.30, 0.45, 0],
            [1.14, 0.45, 0], [0.90, -0.29, 0], [-0.90, -0.29, 0], [-1.14, 0.45, 0],
            fill_color=color, fill_opacity=fill, stroke_color=color, stroke_width=stroke,
        )
        handle = RoundedRectangle(corner_radius=0.09, width=1.0, height=0.20, fill_color=color,
                                  fill_opacity=fill, stroke_color=color, stroke_width=stroke)
        handle.rotate(0.32).move_to([1.76, 0.61, 0])
        lining = VMobject(stroke_color=LINK_COLOR, stroke_width=9)
        lining.set_points_as_corners([[-1.08, 0.40, 0], [-0.86, -0.23, 0], [0.86, -0.23, 0], [1.08, 0.40, 0]])
        return VGroup(wall, handle, lining)

    def pan_badge(self, color=B_COLOR):
        """The pan on a plate the size of the pipe's flange, so the two worlds read as a pair.
        Index 1 is the pan (wall, handle, lining)."""
        plate = RoundedRectangle(corner_radius=0.24, width=2.3, height=2.3, fill_color=color,
                                 fill_opacity=0.12, stroke_color=color, stroke_width=4)
        pan = self.pan_section(color).scale(0.56).move_to(plate.get_center() + 0.12 * RIGHT + 0.05 * DOWN)
        return VGroup(plate, pan)

    def particle(self, word, color):
        disk = Circle(radius=0.42, fill_color=color, fill_opacity=0.20, stroke_color=color, stroke_width=4)
        return VGroup(disk, text(word, 23, color, BOLD).move_to(disk))

    def diffusion_stage(self):
        """One K-25 stage: a tall vessel with a porous barrier down its middle."""
        vessel = RoundedRectangle(corner_radius=0.16, width=1.05, height=2.6, fill_color=A_COLOR,
                                  fill_opacity=0.12, stroke_color=A_COLOR, stroke_width=3)
        barrier = DashedLine(vessel.get_top() + 0.22 * DOWN, vessel.get_bottom() + 0.22 * UP,
                             dash_length=0.12, color=MUTED, stroke_width=3)
        return VGroup(vessel, barrier)

    def factory(self):
        body = Rectangle(width=1.45, height=0.85, fill_color=MUTED, fill_opacity=0.16,
                         stroke_color=MUTED, stroke_width=3)
        left, top = body.get_left()[0], body.get_top()[1]
        roof = VMobject(stroke_color=MUTED, stroke_width=3)
        roof.set_points_as_corners([[left + 0.48 * i + d, top + (0.32 if d else 0), 0]
                                    for i in range(3) for d in (0, 0.48)])
        stack = Rectangle(width=0.22, height=0.62, fill_color=MUTED, fill_opacity=0.16, stroke_color=MUTED,
                          stroke_width=3).next_to(body, UP, buff=0).align_to(body, RIGHT).shift(0.18 * LEFT)
        return VGroup(body, roof, stack)

    def home(self):
        """A house with a pan inside. Index 2 is the pan's lining, drawn when PTFE arrives."""
        house = Polygon([-0.78, -0.62, 0], [0.78, -0.62, 0], [0.78, 0.22, 0], [0, 0.86, 0], [-0.78, 0.22, 0],
                        fill_color=B_COLOR, fill_opacity=0.12, stroke_color=B_COLOR, stroke_width=4)
        pan = self.pan_section(B_COLOR, stroke=3).scale(0.36).move_to([-0.08, -0.22, 0])
        return VGroup(house, pan[:2], pan[2])

    # --- the shared mechanism (B3 and B6) ---------------------------------------------------

    def ptfe_surface(self, skin):
        """The trick in close-up, laid out identically for every skin: metal, the PTFE layer
        with its carbon chain and tight row of fluorine atoms, three particles above it and a
        verdict below. Only the colors and words come from the skin."""
        color = skin["color"]
        base = RoundedRectangle(corner_radius=0.14, width=5.6, height=1.4, fill_color=color,
                                fill_opacity=0.14, stroke_color=color, stroke_width=4).move_to([AXIS, -0.55, 0])
        base_word = text(skin["base"], 26, color, BOLD).move_to(base)
        layer = RoundedRectangle(corner_radius=0.10, width=5.4, height=0.5, fill_color=LINK_COLOR,
                                 fill_opacity=0.30, stroke_color=LINK_COLOR, stroke_width=3).next_to(base, UP, buff=0)
        xs = [AXIS - 2.31 + 0.66 * i for i in range(8)]
        chain = [[x, layer.get_y() + (0.07 if i % 2 else -0.07), 0] for i, x in enumerate(xs)]
        bonds = VGroup(*[Line(p, q, color=MUTED, stroke_width=3) for p, q in zip(chain, chain[1:])])
        carbons = VGroup(*[VGroup(Circle(radius=0.17, fill_color=FAINT, fill_opacity=1, stroke_color=MUTED,
                                         stroke_width=2), text("C", 15, INK, BOLD)).move_to(p) for p in chain])
        fluorines = VGroup(*[VGroup(Circle(radius=0.27, fill_color=LINK_COLOR, fill_opacity=0.28,
                                           stroke_color=LINK_COLOR, stroke_width=3), text("F", 21, LINK_COLOR, BOLD))
                             .move_to([x, layer.get_top()[1] + 0.30, 0]) for x in xs])
        particles = VGroup(*[self.particle(word, color) for word in skin["particles"]])
        particles.arrange(RIGHT, buff=1.0).move_to([AXIS, 3.35, 0])
        verdict = pill(skin["verdict"], LINK_COLOR, size=28).next_to(base, DOWN, buff=0.38)
        with self.alignment_loop(f"PTFE surface, {skin['name']}") as align:
            align.centered(VGroup(base, layer), name="metal and PTFE layer")
            align.even_row(fluorines, name="fluorine row")
            align.even_row(particles, name="incoming particles")
            align.centered(verdict, name="verdict")
            align.inside_safe(VGroup(particles, fluorines, base, verdict), padding=0.14)
        ties = VGroup(*[Line(c.get_top(), f.get_bottom(), color=MUTED, stroke_width=2)
                        for c, f in zip(carbons, fluorines)])
        drop = (fluorines.get_top()[1] + 0.44 - particles.get_y()) * UP
        paths = [ArcBetweenPoints(p.get_center() + drop, p.get_center() + drop + GLANCE, angle=-PI / 3)
                 for p in particles]
        hit = [min(range(len(xs)), key=lambda i: abs(fluorines[i].get_x() - p.get_x())) for p in particles]
        return {"base": base, "base_word": base_word, "layer": layer, "bonds": bonds, "carbons": carbons,
                "ties": ties, "fluorines": fluorines, "particles": particles, "verdict": verdict,
                "drop": drop, "paths": paths, "hit": hit}

    def play_ptfe(self, s, run_time, intro=(), fade=()):
        """Particles fall onto the fluorine row and glance off; the metal behind never changes.
        One narration-relative clock (run_time) is split by PTFE_PHASES, so B6 replays B3."""
        t = [run_time * share for share in PTFE_PHASES]
        self.play(*[FadeIn(m) for m in intro], *[FadeOut(m) for m in fade],
                  Create(s["base"]), FadeIn(s["base_word"]), FadeIn(s["layer"]), Create(s["bonds"]),
                  FadeIn(s["carbons"]), Create(s["ties"]),
                  LaggedStart(*[GrowFromCenter(f) for f in s["fluorines"]], lag_ratio=0.06),
                  FadeIn(s["particles"], shift=0.25 * DOWN), run_time=t[0])
        self.play(s["particles"].animate.shift(s["drop"]), rate_func=rush_into, run_time=t[1])
        self.sfx("tap.wav", -10)
        self.play(*[MoveAlongPath(p, path) for p, path in zip(s["particles"], s["paths"])],
                  *[Indicate(s["fluorines"][i], color=LINK_COLOR, scale_factor=1.3) for i in s["hit"]],
                  rate_func=rush_from, run_time=t[2])
        self.sfx("ping.wav", -15)
        self.play(GrowFromCenter(s["verdict"]), s["particles"].animate.set_opacity(0.35), run_time=t[3])
        self.play(FadeOut(s["particles"]), Indicate(s["fluorines"], color=LINK_COLOR, scale_factor=1.06),
                  run_time=t[4])

    # --- the nine beats -----------------------------------------------------------------------

    def construct(self):
        # B1: the cover. War on the left, kitchen on the right; the PTFE gasket leaves the pipe
        # and becomes the pan's lining, which is the whole story in one move.
        with self.beat("B1") as b:
            war, kitchen = title("WAR", 58, A_COLOR), title("KITCHEN", 58, B_COLOR)
            words = VGroup(war, kitchen).arrange(RIGHT, buff=1.55).move_to([AXIS, 4.3, 0])
            pipe = self.pipe_end().scale(1.1).move_to([AXIS - 1.62, 1.75, 0])
            pan = self.pan_badge().scale(1.1).move_to([AXIS + 1.62, 1.75, 0])
            with self.alignment_loop("B1 cover") as align:
                align.centered(words, name="war to kitchen")
                align.mirror_pair(pipe, pan, y=1.75, min_gap=0.4, name="pipe and pan plates")
                align.inside_safe(VGroup(words, pipe, pan), padding=0.12)
            names = VGroup(text("BOMB PROJECT", 23, A_COLOR, BOLD), text("NON-STICK PAN", 23, B_COLOR, BOLD))
            for name, plate in zip(names, (pipe, pan)):
                name.set_x(plate.get_x()).set_y(plate.get_bottom()[1] - 0.42)
            arrow = Arrow(war.get_right(), kitchen.get_left(), buff=0.22, color=LINK_COLOR, stroke_width=7,
                          max_tip_length_to_length_ratio=0.3)
            with self.alignment_loop("B1 labels") as align:
                align.inside_safe(VGroup(words, arrow, pipe, pan, names), padding=0.12)

            self.add(words, pipe[:4], pipe[4], pan[0], pan[1][:2], names)
            centre = pipe[3].get_center()
            self.play(GrowArrow(arrow), Rotate(pipe[4], -TAU / 3, about_point=centre, rate_func=linear),
                      run_time=0.34 * b.duration)
            self.sfx("whoosh.wav", -14)
            self.play(TransformFromCopy(pipe[2], pan[1][2], path_arc=-PI / 2),
                      Rotate(pipe[4], -TAU / 3, about_point=centre, rate_func=linear),
                      run_time=0.40 * b.duration)
            self.play(Indicate(kitchen, color=B_COLOR, scale_factor=1.08),
                      Rotate(pipe[4], -TAU / 6, about_point=centre, rate_func=linear),
                      run_time=0.16 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B2: 1938. Gas in a cylinder links into chains and settles as a white solid: PTFE.
        with self.beat("B2") as b:
            header = beat_header(2, "A 1938 SURPRISE", A_COLOR)
            year = date_badge("1938", A_COLOR)
            body = RoundedRectangle(corner_radius=0.72, width=4.3, height=1.5, fill_color=FAINT,
                                    fill_opacity=0.55, stroke_color=MUTED, stroke_width=4)
            neck = Rectangle(width=0.34, height=0.62, fill_color=FAINT, fill_opacity=1, stroke_color=MUTED,
                             stroke_width=3).next_to(body, RIGHT, buff=0)
            valve = RoundedRectangle(corner_radius=0.06, width=0.30, height=0.92, fill_color=A_COLOR, fill_opacity=0.18,
                                     stroke_color=A_COLOR, stroke_width=3).next_to(neck, RIGHT, buff=0)
            cylinder = VGroup(body, neck, valve)
            chemist = pill("ROY PLUNKETT", A_COLOR, size=22)
            VGroup(year, cylinder, chemist).arrange(DOWN, buff=0.75).move_to([AXIS, 2.3, 0])
            with self.alignment_loop("B2 cylinder") as align:
                align.even_column([year, cylinder, chemist], gap=0.75, name="date, cylinder, chemist")
                align.inside_safe(VGroup(header, year, cylinder, chemist), padding=0.14)
            cx, cy = body.get_center()[:2]
            rng = np.random.default_rng(1938)
            gas = VGroup(*[Dot([cx + rng.uniform(-1.65, 1.65), cy + rng.uniform(-0.45, 0.45), 0],
                               radius=0.075, color=MUTED) for _ in range(12)])
            chain = VGroup(*[Dot([cx - 1.65 + 0.3 * i, cy - 0.36 + (0.07 if i % 2 else -0.07), 0],
                                 radius=0.075, color=INK) for i in range(12)])
            links = VGroup(*[Line(p.get_center(), q.get_center(), color=INK, stroke_width=3)
                             for p, q in zip(chain, chain[1:])])
            solid = RoundedRectangle(corner_radius=0.16, width=3.5, height=0.36, fill_color=INK,
                                     fill_opacity=0.92, stroke_width=0).move_to([cx, cy - 0.40, 0])
            block = RoundedRectangle(corner_radius=0.16, width=2.6, height=0.85, fill_color=LINK_COLOR,
                                     fill_opacity=0.28, stroke_color=LINK_COLOR, stroke_width=3)
            block_word = title("PTFE", 44, LINK_COLOR)
            ptfe = VGroup(block, block_word.move_to(block)).next_to(chemist, DOWN, buff=0.6)
            with self.alignment_loop("B2 PTFE result") as align:
                align.centered(ptfe, name="PTFE block")
                align.inside_safe(VGroup(header, year, cylinder, chemist, ptfe), padding=0.14)

            self.add(header)
            self.play(FadeIn(year, shift=0.2 * DOWN), DrawBorderThenFill(cylinder), FadeIn(gas),
                      run_time=0.14 * b.duration)
            self.sfx("ticks.wav", -15)
            self.play(Transform(gas, chain), Create(links), FadeIn(chemist, shift=0.15 * UP),
                      run_time=0.20 * b.duration)
            self.play(ReplacementTransform(VGroup(gas, links), solid), run_time=0.20 * b.duration)
            self.wait(0.10 * b.duration)
            self.play(ReplacementTransform(solid, block), FadeIn(block_word, scale=0.8),
                      run_time=0.26 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B3: K-25 sends uranium gas through stage after stage; the camera dives into one
        # PTFE gasket, where the shared mechanism shows why the gas could not eat it.
        with self.beat("B3") as b:
            header = beat_header(3, "URANIUM GAS", A_COLOR)
            stages = VGroup(*[self.diffusion_stage() for _ in range(4)]).arrange(RIGHT, buff=0.42)
            stages.move_to([AXIS, 2.3, 0])
            site = pill("K-25 · OAK RIDGE", A_COLOR, size=22).next_to(stages, DOWN, buff=0.45)
            with self.alignment_loop("B3 K-25 stages") as align:
                align.even_row(stages, y=2.3, gap=0.42, name="diffusion stages")
                align.centered(site, name="plant label")
                align.inside_safe(VGroup(header, stages, site), padding=0.14)
            pipes = VGroup(*[Line(left.get_right(), right.get_left(), color=A_COLOR, stroke_width=6)
                             for left, right in zip(stages, stages[1:])])
            gaskets = VGroup(*[Circle(radius=0.15, stroke_color=LINK_COLOR, stroke_width=6).move_to(p.get_center())
                               for p in pipes])
            route = Line(stages[0].get_center(), stages[-1].get_center())
            uf6 = self.particle("UF₆", A_COLOR).scale(0.72).move_to(route.get_start())
            surface = self.ptfe_surface(GAS_SKIN)
            proxy = surface["layer"].copy()

            self.add(header)
            self.play(LaggedStart(*[FadeIn(s, shift=0.15 * UP) for s in stages], lag_ratio=0.15),
                      Create(pipes), GrowFromCenter(gaskets), FadeIn(site), run_time=0.12 * b.duration)
            self.sfx("whoosh.wav", -16)
            self.play(MoveAlongPath(uf6, route), rate_func=linear, run_time=0.20 * b.duration)
            self.play(Indicate(gaskets, color=LINK_COLOR, scale_factor=1.4), run_time=0.04 * b.duration)
            self.sfx("swipe.wav", -15)
            cascade = VGroup(stages, pipes, gaskets[0], gaskets[2], site, uf6)
            self.play(cascade.animate.scale(2.6, about_point=gaskets[1].get_center()).set_opacity(0),
                      ReplacementTransform(gaskets[1], proxy), run_time=0.12 * b.duration)
            self.remove(cascade)
            self.ptfe_time = min(REPLAY_MAX, 0.9 * b.duration)
            self.play_ptfe(surface, self.ptfe_time, fade=[proxy])
            self.hold(b)
        self.clear_stage(0.2)

        # B4: the trick compressed into three moves: cover, bounce back, slide off.
        with self.beat("B4") as b:
            header = beat_header(4, "SURFACE TRICK", LINK_COLOR)
            badge = VGroup(title("INERT", 54, LINK_COLOR), title("·", 54, MUTED),
                           title("LOW-GRIP", 54, LINK_COLOR)).arrange(RIGHT, buff=0.22)
            tiles = VGroup(*[RoundedRectangle(corner_radius=0.18, width=1.8, height=2.1, fill_color=FAINT,
                                              fill_opacity=0.5, stroke_color=LINK_COLOR, stroke_width=2)
                             for _ in range(3)]).arrange(RIGHT, buff=0.28)
            VGroup(badge, tiles).arrange(DOWN, buff=1.05).move_to([AXIS, 2.55, 0])
            with self.alignment_loop("B4 three moves") as align:
                align.centered(badge, name="badge")
                align.even_row(tiles, gap=0.28, name="move tiles")
                align.inside_safe(VGroup(header, badge, tiles), padding=0.14)
            moves = VGroup(text("SHIELD", 22, LINK_COLOR, BOLD), text("RESIST", 22, LINK_COLOR, BOLD),
                           text("RELEASE", 22, LINK_COLOR, BOLD))
            for move, tile in zip(moves, tiles):
                move.next_to(tile, DOWN, buff=0.24)
            c0, c1, c2 = (tile.get_center() for tile in tiles)
            core = Circle(radius=0.30, fill_color=MUTED, fill_opacity=0.35, stroke_color=MUTED,
                          stroke_width=3).move_to(c0 + 0.25 * DOWN)
            bar = Line(c0 + 0.62 * LEFT + 0.58 * UP, c0 + 0.62 * RIGHT + 0.58 * UP, color=LINK_COLOR, stroke_width=9)
            cap = Arc(radius=0.50, start_angle=0, angle=PI, color=LINK_COLOR, stroke_width=9)
            cap.move_arc_center_to(core.get_center())
            wall = Line(c1 + 0.50 * RIGHT + 0.62 * UP, c1 + 0.50 * RIGHT + 0.62 * DOWN, color=LINK_COLOR, stroke_width=9)
            hit = c1 + 0.36 * RIGHT
            arrive = Arrow(c1 + 0.72 * LEFT + 0.52 * UP, hit, buff=0, color=INK, stroke_width=6,
                           max_tip_length_to_length_ratio=0.25)
            leave = Arrow(hit, c1 + 0.72 * LEFT + 0.52 * DOWN, buff=0, color=INK, stroke_width=6,
                          max_tip_length_to_length_ratio=0.25)
            slope = Line(c2 + 0.66 * LEFT + 0.40 * UP, c2 + 0.66 * RIGHT + 0.40 * DOWN, color=LINK_COLOR, stroke_width=9)
            drop = Circle(radius=0.17, fill_color=INK, fill_opacity=0.9, stroke_width=0)
            drop.move_to(slope.point_from_proportion(0.18) + 0.24 * UP)
            downhill = slope.get_end() - slope.get_start()

            self.add(header)
            self.play(FadeIn(badge, scale=0.92), FadeIn(tiles), FadeIn(core), Create(bar), Create(wall),
                      Create(slope), FadeIn(drop), run_time=0.34 * b.duration)
            self.play(Transform(bar, cap), FadeIn(moves[0]), run_time=0.18 * b.duration)
            self.sfx("spark.wav", -14)
            self.play(GrowArrow(arrive), FadeIn(moves[1]), run_time=0.09 * b.duration)
            self.play(ReplacementTransform(arrive, leave), run_time=0.09 * b.duration)
            self.play(drop.animate.shift(0.72 * downhill + 0.10 * DOWN).set_opacity(0.25), FadeIn(moves[2]),
                      run_time=0.20 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B5: the mid-1950s patent drawing becomes a real aluminum pan; PTFE settles inside.
        with self.beat("B5") as b:
            header = beat_header(5, "PAN PATENT", B_COLOR)
            year = pill("MID-1950s", B_COLOR, size=24)
            page = RoundedRectangle(corner_radius=0.16, width=3.4, height=3.3, fill_color=FAINT,
                                    fill_opacity=0.45, stroke_color=MUTED, stroke_width=3)
            heading = text("PATENT", 22, MUTED, BOLD).next_to(page.get_top(), DOWN, buff=0.28)
            sketch = self.pan_section(MUTED, stroke=3, fill=0.15)[:2].scale(0.78)
            sketch.move_to(page.get_center() + 0.12 * UP)
            lines = VGroup(*[Line([-1.15, 0, 0], [1.15 - 0.45 * (i % 2), 0, 0], color=MUTED, stroke_width=2)
                             for i in range(3)]).arrange(DOWN, buff=0.17, aligned_edge=LEFT)
            lines.next_to(page.get_bottom(), UP, buff=0.32)
            sheet = VGroup(page, heading, sketch, lines)
            makers = pill("MARC & COLETTE GRÉGOIRE", B_COLOR, size=22)
            VGroup(year, sheet, makers).arrange(DOWN, buff=0.45).move_to([AXIS, 1.85, 0])
            with self.alignment_loop("B5 patent sheet") as align:
                align.even_column([year, sheet, makers], gap=0.45, name="date, patent, makers")
                align.inside_safe(VGroup(header, year, sheet, makers), padding=0.14)
            pan = self.pan_section().scale(1.5).move_to(sheet.get_center())
            with self.alignment_loop("B5 aluminum pan") as align:
                align.centered(pan, name="pan")
                align.inside_safe(VGroup(header, year, pan, makers), padding=0.14)
            strip = Line(pan[2].get_corner(UL), pan[2].get_corner(UR), color=LINK_COLOR, stroke_width=9)
            strip.shift(1.15 * UP)
            tag = pill("PTFE", LINK_COLOR, size=22).next_to(pan[0], UP, buff=0.3).shift(0.15 * UP)

            self.add(header)
            self.play(FadeIn(year, shift=0.2 * DOWN), DrawBorderThenFill(page), FadeIn(heading), Create(sketch),
                      Create(lines), run_time=0.18 * b.duration)
            self.sfx("swipe.wav", -15)
            self.play(ReplacementTransform(sketch, pan[:2]), FadeOut(VGroup(page, heading, lines)),
                      FadeIn(makers, shift=0.2 * UP), run_time=0.26 * b.duration)
            self.play(FadeIn(strip, shift=0.3 * DOWN), run_time=0.08 * b.duration)
            self.sfx("wash.wav", -16)
            self.play(Transform(strip, pan[2]), run_time=0.26 * b.duration)
            self.play(FadeIn(tag, shift=0.15 * DOWN), run_time=0.10 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B6: the same surface, the same fall, the same glance: breakfast instead of uranium gas.
        with self.beat("B6") as b:
            header = beat_header(6, "BREAKFAST TEST", B_COLOR)
            surface = self.ptfe_surface(PAN_SKIN)
            self.play_ptfe(surface, self.ptfe_time, intro=[header])
            self.hold(b)
        self.clear_stage(0.2)

        # B7: PTFE will not grip smooth metal either, so the patent etched pits that it fills.
        with self.beat("B7") as b:
            header = beat_header(7, "MAKE IT STICK", LINK_COLOR)
            pits = np.linspace(AXIS - 2.1, AXIS + 2.1, 7)
            top, bottom, half = 0.95, -0.95, 2.6

            def metal(depth):
                points = [[AXIS - half, bottom, 0], [AXIS - half, top, 0]]
                for x in pits:
                    points += [[x - 0.17, top, 0], [x, top - depth, 0], [x + 0.17, top, 0]]
                points += [[AXIS + half, top, 0], [AXIS + half, bottom, 0]]
                return Polygon(*points, fill_color=B_COLOR, fill_opacity=0.16, stroke_color=B_COLOR, stroke_width=4)

            def coating(depth, y):
                points = [[AXIS - 2.35, y + 0.5, 0], [AXIS + 2.35, y + 0.5, 0], [AXIS + 2.35, y, 0]]
                for x in reversed(pits):
                    points += [[x + 0.17, y, 0], [x, y - depth, 0], [x - 0.17, y, 0]]
                points += [[AXIS - 2.35, y, 0]]
                return Polygon(*points, fill_color=LINK_COLOR, fill_opacity=0.42, stroke_color=LINK_COLOR,
                               stroke_width=3)

            block, etched = metal(0.0), metal(0.30)
            layer, filled = coating(0.0, 2.55), coating(0.30, top)
            word = text("PTFE", 22, INK, BOLD).move_to(layer.get_center() + 0.25 * UP)
            sheet = VGroup(layer, word)
            aluminum = pill("ALUMINUM", B_COLOR, size=22).next_to(block, DOWN, buff=0.4)
            with self.alignment_loop("B7 aluminum section") as align:
                align.centered(VGroup(block, aluminum), name="metal and label")
                align.centered(sheet, name="PTFE sheet")
                align.inside_safe(VGroup(header, sheet, block, aluminum), padding=0.14)
            hover = sheet.get_center()
            seated = sheet.copy().shift((top + 0.25 - layer.get_y()) * UP)
            slip = 1.05 * LEFT + 0.30 * DOWN
            no_grip = pill("NO GRIP", ALERT, size=22).move_to([AXIS + 1.35, top + 0.85, 0])
            acid = pill("ACID ETCH", MUTED, size=20).move_to([AXIS - 1.75, top + 0.55, 0])
            locked = pill("LOCKED", LINK_COLOR, size=24).move_to([AXIS, top + 1.35, 0])
            with self.alignment_loop("B7 labels") as align:
                align.centered(locked, name="locked label")
                align.inside_safe(VGroup(no_grip, acid, locked, seated), padding=0.14)

            self.add(header)
            self.play(DrawBorderThenFill(block), FadeIn(aluminum), FadeIn(sheet, shift=0.2 * DOWN),
                      run_time=0.10 * b.duration)
            self.play(sheet.animate.move_to(seated), rate_func=rush_into, run_time=0.10 * b.duration)
            self.wait(0.04 * b.duration)
            self.sfx("swipe.wav", -15)
            self.play(sheet.animate.shift(slip).rotate(0.16), FadeIn(no_grip, scale=0.9), run_time=0.16 * b.duration)
            self.play(sheet.animate.rotate(-0.16).move_to(hover), FadeOut(no_grip), run_time=0.10 * b.duration)
            self.wait(0.04 * b.duration)
            self.add(acid)
            self.sfx("wash.wav", -15)
            self.play(acid.animate.shift(3.5 * RIGHT), Transform(block, etched), run_time=0.20 * b.duration)
            self.play(Transform(layer, filled), word.animate.move_to(filled.get_center() + 0.12 * UP), FadeOut(acid),
                      rate_func=rush_into, run_time=0.12 * b.duration)
            self.play(GrowFromCenter(locked), Indicate(layer, color=LINK_COLOR, scale_factor=1.03),
                      run_time=0.06 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B8: after the war the violet material travels from secret equipment to factories
        # and homes; each stop lights up as it arrives.
        with self.beat("B8") as b:
            header = beat_header(8, "AFTER THE WAR", LINK_COLOR)
            secret, everyday = title("SECRET", 50, A_COLOR), title("EVERYDAY", 50, B_COLOR)
            heading = VGroup(secret, everyday).arrange(RIGHT, buff=1.3)
            equipment = self.pipe_end().scale(0.7)
            plant, house = self.factory().scale(1.15), self.home().scale(1.1)
            stops = VGroup(equipment, plant, house).arrange(RIGHT, buff=0.45)
            names = VGroup(text("EQUIPMENT", 22, A_COLOR, BOLD), text("FACTORIES", 22, MUTED, BOLD),
                           text("HOMES", 22, B_COLOR, BOLD))
            VGroup(heading, stops).arrange(DOWN, buff=0.95).move_to([AXIS, 2.6, 0])
            with self.alignment_loop("B8 secret to everyday") as align:
                align.centered(heading, name="heading")
                align.even_row(stops, gap=0.45, name="three stops")
                align.inside_safe(VGroup(header, heading, stops), padding=0.14)
            for name, stop in zip(names, stops):
                name.set_x(stop.get_x()).set_y(stops.get_bottom()[1] - 0.32)
            way = Arrow(secret.get_right(), everyday.get_left(), buff=0.2, color=LINK_COLOR, stroke_width=7,
                        max_tip_length_to_length_ratio=0.3)
            y_rail = names.get_bottom()[1] - 0.45
            rail = Line([stops[0].get_x(), y_rail, 0], [stops[2].get_x(), y_rail, 0], color=LINK_COLOR, stroke_width=6)
            nodes = VGroup(*[Circle(radius=0.11, stroke_color=LINK_COLOR, stroke_width=4, fill_color=BG,
                                    fill_opacity=1).move_to([s.get_x(), y_rail, 0]) for s in stops])
            traveler = Dot(rail.get_start(), radius=0.15, color=LINK_COLOR)
            roll = Circle(radius=0.26, fill_color=LINK_COLOR, fill_opacity=0.45, stroke_color=LINK_COLOR,
                          stroke_width=3).move_to(plant[0].get_center())
            first_leg = Line(rail.get_start(), nodes[1].get_center())
            second_leg = Line(nodes[1].get_center(), rail.get_end())
            with self.alignment_loop("B8 rail") as align:
                align.inside_safe(VGroup(heading, way, stops, names, rail), padding=0.14)

            self.add(header)
            shown = (equipment, plant, house[:2])
            self.play(FadeIn(heading), GrowArrow(way), LaggedStart(*[FadeIn(s, shift=0.15 * UP) for s in shown],
                                                                    lag_ratio=0.2),
                      FadeIn(names), Create(rail), FadeIn(nodes), FadeIn(traveler), run_time=0.20 * b.duration)
            self.sfx("ticks.wav", -15)
            self.play(MoveAlongPath(traveler, first_leg), rate_func=linear, run_time=0.40 * b.duration)
            self.play(GrowFromCenter(roll), Indicate(plant, color=MUTED, scale_factor=1.05), run_time=0.06 * b.duration)
            self.play(MoveAlongPath(traveler, second_leg), rate_func=linear, run_time=0.18 * b.duration)
            self.play(Create(house[2]), Indicate(everyday, color=B_COLOR, scale_factor=1.06),
                      run_time=0.08 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B9: this episode's Connection Map; its pipe and pan are B1's, so the loop closes.
        with self.beat("B9") as b:
            header = beat_header(9, "PTFE CONNECTION", LINK_COLOR)
            self.end_card(
                run_time=0.86 * b.duration,
                title=False,
                both_ways=False,
                tagline=("SAME TRICK", "TWO WORLDS"),
                sound="ping.wav",
                intro=[header],
                icons=(self.pipe_end(), self.pan_badge()),
            )
            self.hold(b)

        self.wait(0.25)
