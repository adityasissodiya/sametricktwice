"""Steam Engine × AI: series house-style infographic visuals.

The approved words live only in script.md; this file draws what they describe, with diagrams
made for this episode. Every animation is a share of its beat's narration (b.duration), so the
pictures stay inside the spoken line. B3 and B6 call one rebound mechanism with the same
geometry and the same clock: cheaper tokens in B6 replay the cheaper coal of B3.
"""

from kit import *

AXIS = STAGE_CENTER[0]
COAL_FILL = "#3B404C"  # a dark neutral: coal is a material here, not a meaning

# B3 and B6 share these: one stack, one set of paths, one phase clock; only the skin changes.
REBOUND_PHASES = (0.14, 0.22, 0.26, 0.26, 0.12)  # build, cheaper, more uses, total grows, result
REBOUND_MAX = 6.2  # seconds: the replay must also fit B6's line (about 6.9 s), the shorter one
UNIT_BAR = 3.3  # width of one job's cost bar before it gets cheaper
TOTAL_W, TOTAL_H = 5.6, 0.62  # the total bar's frame
COAL_SKIN = {"tag": "coal", "hue": A_COLOR, "unit": "COAL PER JOB", "uses": "MORE ENGINES",
             "total": "BRITISH COAL OUTPUT", "result": "64.7M → 287M TONS"}
TOKEN_SKIN = {"tag": "tokens", "hue": B_COLOR, "unit": "PRICE PER ANSWER", "uses": "MORE APPS AND AGENTS",
              "total": "GOOGLE TOKENS PER MONTH", "result": "9.7T → 480T"}


class Episode(ShortScene):
    """Nine beats; every layout keyframe declares its alignment intent before it moves."""

    # --- drawings made for this episode ---------------------------------------------------

    def engine_icon(self, color=A_COLOR):
        """A beam engine from the side: ground, boiler, upright cylinder, A-frame post, the
        rocking beam (index 4) and the pump rod (index 5)."""
        ground = Line([-1.0, -0.82, 0], [1.1, -0.82, 0], color=color, stroke_width=4)
        boiler = RoundedRectangle(corner_radius=0.24, width=1.15, height=0.58, fill_color=color,
                                  fill_opacity=0.22, stroke_color=color, stroke_width=4).move_to([-0.38, -0.53, 0])
        cylinder = Rectangle(width=0.38, height=0.78, fill_color=color, fill_opacity=0.34,
                             stroke_color=color, stroke_width=4).move_to([-0.58, 0.15, 0])
        post = Polygon([0.06, -0.82, 0], [0.46, -0.82, 0], [0.26, 0.70, 0], fill_color=color,
                       fill_opacity=0.12, stroke_color=color, stroke_width=4)
        beam = VGroup(Line([-0.80, 0.72, 0], [1.02, 0.72, 0], color=color, stroke_width=8),
                      Dot([0.26, 0.72, 0], radius=0.08, color=INK))
        rod = Line([0.96, 0.72, 0], [0.96, -0.82, 0], color=color, stroke_width=4)
        return VGroup(ground, boiler, cylinder, post, beam, rod)

    def answer_icon(self, color=B_COLOR):
        """A chat answer: a speech bubble with a short tail and three dots (index 2)."""
        tail = Polygon([-0.60, -0.30, 0], [-0.12, -0.30, 0], [-0.78, -0.78, 0], fill_color=color,
                       fill_opacity=0.22, stroke_color=color, stroke_width=4)
        bubble = RoundedRectangle(corner_radius=0.32, width=1.9, height=1.2, fill_color=BG, fill_opacity=1,
                                  stroke_color=color, stroke_width=4).move_to([0, 0.22, 0])
        inner = bubble.copy().set_stroke(width=0).set_fill(color, opacity=0.22)
        dots = VGroup(*[Dot([x, 0.22, 0], radius=0.12, color=color) for x in (-0.48, 0, 0.48)])
        return VGroup(tail, VGroup(bubble, inner), dots)

    def plate(self, icon, color):
        """A square plate for a world's icon, so both worlds read as a matched pair."""
        board = RoundedRectangle(corner_radius=0.26, width=2.3, height=2.3, fill_color=color,
                                 fill_opacity=0.10, stroke_color=color, stroke_width=4)
        icon.scale_to_fit_height(1.45).move_to(board)
        return VGroup(board, icon)

    def coal_lump(self, size=0.22, seed=0):
        rng = np.random.default_rng(seed)
        corners = [[size * (0.78 + 0.3 * rng.random()) * np.cos(a), size * (0.70 + 0.3 * rng.random()) * np.sin(a), 0]
                   for a in np.linspace(0, TAU, 7)[:-1]]
        return Polygon(*corners, fill_color=COAL_FILL, fill_opacity=1, stroke_color=MUTED, stroke_width=2)

    def coal_heap(self, rows, size=0.24, seed=7):
        """Lumps stacked in rows of (n, n-1, ...), widest at the bottom."""
        heap = VGroup()
        for level, count in enumerate(rows):
            for i in range(count):
                x = (i - (count - 1) / 2) * size * 1.75
                heap.add(self.coal_lump(size, seed + 10 * level + i).move_to([x, level * size * 1.35, 0]))
        return heap

    def token_tile(self, piece, color=B_COLOR):
        word = text(piece, 34, INK, BOLD)
        box = RoundedRectangle(corner_radius=0.14, width=word.width + 0.42, height=0.82, fill_color=color,
                               fill_opacity=0.24, stroke_color=color, stroke_width=4)
        return VGroup(box, word.move_to(box))

    def coal_plant(self, color=A_COLOR):
        hall = Rectangle(width=1.55, height=0.78, fill_color=color, fill_opacity=0.18, stroke_color=color,
                         stroke_width=4).move_to([0.05, -0.45, 0])
        stacks = VGroup(*[Rectangle(width=0.24, height=1.0, fill_color=color, fill_opacity=0.30, stroke_color=color,
                                    stroke_width=4).move_to([x, 0.44, 0]) for x in (-0.38, 0.10)])
        heap = self.coal_heap((3, 2), size=0.13, seed=31).move_to([0.42, -0.05, 0])
        return VGroup(stacks, hall, heap)

    def data_center(self, color=B_COLOR):
        rack = RoundedRectangle(corner_radius=0.12, width=1.35, height=1.75, fill_color=color, fill_opacity=0.16,
                                stroke_color=color, stroke_width=4)
        slots = VGroup(*[Line([-0.48, y, 0], [0.30, y, 0], color=color, stroke_width=4) for y in (0.55, 0.18, -0.19, -0.56)])
        lights = VGroup(*[Dot([0.46, y, 0], radius=0.06, color=INK) for y in (0.55, 0.18, -0.19, -0.56)])
        return VGroup(rack, slots, lights)

    # --- the shared mechanism (B3 and B6) ---------------------------------------------------

    def rebound_stack(self, skin, draw):
        """The trick laid out identically for every skin: one job and its cost bar, a block of
        twelve jobs, and the total bar with its result. Only colors, icons and words change."""
        hue = skin["hue"]
        unit_label = text(skin["unit"], 22, MUTED, BOLD).move_to([AXIS, 4.18, 0])
        icon = draw(hue).scale_to_fit_height(0.95)
        bar = Rectangle(width=UNIT_BAR, height=0.46, fill_color=hue, fill_opacity=0.55, stroke_width=0)
        row = VGroup(icon, bar).arrange(RIGHT, buff=0.35).move_to([AXIS, 3.40, 0])
        users = VGroup(*[draw(hue).scale_to_fit_height(0.50) for _ in range(12)])
        users.arrange_in_grid(rows=3, cols=4, buff=(0.46, 0.26)).move_to([AXIS, 1.48, 0])
        uses_label = text(skin["uses"], 22, hue, BOLD).move_to([AXIS, 0.10, 0])
        total_label = text(skin["total"], 22, MUTED, BOLD).move_to([AXIS, -0.50, 0])
        frame = RoundedRectangle(corner_radius=0.14, width=TOTAL_W, height=TOTAL_H, stroke_color=LINK_COLOR,
                                 stroke_width=4).move_to([AXIS, -1.12, 0])
        result = pill(skin["result"], LINK_COLOR, size=26).move_to([AXIS, -1.95, 0])
        with self.alignment_loop(f"Rebound stack, {skin['tag']}") as align:
            align.centered(unit_label, name="unit label")
            align.centered(row, name="one job and its cost")
            align.centered(users, name="block of jobs")
            align.centered(uses_label, name="uses label")
            align.centered(VGroup(total_label, frame), name="total bar")
            align.centered(result, name="result pill")
            align.inside_safe(VGroup(unit_label, row, users, uses_label, total_label, frame, result), padding=0.12)
        fill = Rectangle(width=1.1, height=TOTAL_H - 0.16, fill_color=LINK_COLOR, fill_opacity=0.62, stroke_width=0)
        fill.align_to(frame, LEFT).shift(0.08 * RIGHT).set_y(frame.get_y())
        cheaper = pill("CHEAPER", LINK_COLOR, size=22).move_to([bar.get_left()[0] + UNIT_BAR / 3 + 0.95, row.get_y(), 0])
        drops = VGroup(*[Dot(u.get_center(), radius=0.07, color=LINK_COLOR) for u in users])
        landing = [fill.get_right() + (0.35 + 0.33 * i) * RIGHT for i in range(12)]
        routes = [Line(d.get_center(), p) for d, p in zip(drops, landing)]
        return {"unit_label": unit_label, "icon": icon, "bar": bar, "users": users, "uses_label": uses_label,
                "total_label": total_label, "frame": frame, "fill": fill, "result": result, "cheaper": cheaper,
                "drops": drops, "routes": routes}

    def rebound(self, s, run_time, intro=()):
        """One job gets cheaper, jobs multiply, and the total grows past where it began. One
        narration-relative clock (run_time) is split by REBOUND_PHASES, so B6 replays B3."""
        t = [run_time * share for share in REBOUND_PHASES]
        self.play(*[FadeIn(m) for m in intro], FadeIn(s["unit_label"]), FadeIn(s["icon"], scale=0.9),
                  GrowFromEdge(s["bar"], LEFT), Create(s["frame"]), FadeIn(s["fill"]), FadeIn(s["total_label"]),
                  run_time=t[0])
        self.sfx("tap.wav", -12)
        self.play(s["bar"].animate.stretch_to_fit_width(UNIT_BAR / 3, about_edge=LEFT),
                  GrowFromCenter(s["cheaper"]), run_time=t[1])
        self.sfx("pixels.wav", -14)
        self.play(LaggedStart(*[TransformFromCopy(s["icon"], u) for u in s["users"]], lag_ratio=0.07),
                  FadeIn(s["uses_label"], shift=0.15 * UP), run_time=t[2])
        self.sfx("power-up.wav", -14)
        self.add(s["drops"])
        self.play(LaggedStart(*[MoveAlongPath(d, p) for d, p in zip(s["drops"], s["routes"])], lag_ratio=0.05),
                  s["fill"].animate.stretch_to_fit_width(TOTAL_W - 0.16, about_edge=LEFT),
                  run_time=t[3])
        self.sfx("ping.wav", -15)
        self.play(GrowFromCenter(s["result"]), FadeOut(s["drops"]),
                  Indicate(s["fill"], color=LINK_COLOR, scale_factor=1.04), run_time=t[4])

    # --- the nine beats -----------------------------------------------------------------------

    def construct(self):
        # B1: the cover. Each world's cost per job shrinks while the shared total keeps growing;
        # the engine's beam is already rocking at frame zero.
        with self.beat("B1") as b:
            less, more = title("LESS EACH", 52, INK), title("MORE TOTAL", 52, LINK_COLOR)
            words = VGroup(less, more).arrange(RIGHT, buff=0.55).move_to([AXIS, 4.45, 0])
            engine = self.plate(self.engine_icon(), A_COLOR).move_to([AXIS - 1.62, 2.55, 0])
            answer = self.plate(self.answer_icon(), B_COLOR).move_to([AXIS + 1.62, 2.55, 0])
            with self.alignment_loop("B1 cover") as align:
                align.centered(words, name="less each, more total")
                align.mirror_pair(engine, answer, y=2.55, min_gap=0.4, name="engine and answer plates")
                align.inside_safe(VGroup(words, engine, answer), padding=0.12)
            names = VGroup(text("STEAM ENGINE", 24, A_COLOR, BOLD), text("AI", 24, B_COLOR, BOLD))
            costs = VGroup(*[Rectangle(width=1.9, height=0.34, fill_color=c, fill_opacity=0.6, stroke_width=0)
                             for c in (A_COLOR, B_COLOR)])
            for name, cost, board in zip(names, costs, (engine, answer)):
                name.set_x(board.get_x()).set_y(board.get_bottom()[1] - 0.38)
                cost.set_x(board.get_x()).set_y(board.get_bottom()[1] - 1.0)
            frame = RoundedRectangle(corner_radius=0.14, width=TOTAL_W, height=TOTAL_H, stroke_color=LINK_COLOR,
                                     stroke_width=4).move_to([AXIS, -0.70, 0])
            fill = Rectangle(width=0.9, height=TOTAL_H - 0.16, fill_color=LINK_COLOR, fill_opacity=0.62, stroke_width=0)
            fill.align_to(frame, LEFT).shift(0.08 * RIGHT).set_y(frame.get_y())
            total = text("TOTAL", 22, MUTED, BOLD).next_to(frame, DOWN, buff=0.25)
            with self.alignment_loop("B1 bars") as align:
                align.centered(VGroup(frame, total), name="total bar")
                align.inside_safe(VGroup(words, engine, answer, names, costs, frame, total), padding=0.12)
            beam, pivot = engine[1][4], engine[1][4][1].get_center()

            self.add(words, engine, answer, names, costs, frame, fill, total)
            # linear from frame zero: an eased start would leave the first quarter-second still
            self.play(*[c.animate(rate_func=linear).stretch_to_fit_width(0.65, about_edge=LEFT) for c in costs],
                      fill.animate(rate_func=linear).stretch_to_fit_width(3.2, about_edge=LEFT),
                      Rotate(beam, 0.24, about_point=pivot, rate_func=there_and_back), run_time=0.40 * b.duration)
            self.sfx("whoosh.wav", -14)
            self.play(fill.animate.stretch_to_fit_width(TOTAL_W - 0.16, about_edge=LEFT),
                      Rotate(beam, -0.24, about_point=pivot, rate_func=there_and_back), run_time=0.36 * b.duration)
            self.play(Indicate(more, color=LINK_COLOR, scale_factor=1.08), run_time=0.14 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B2: 1769. The condenser slides out of the engine's cylinder into its own box beside the
        # boiler; steam follows the new pipe, and the coal heap shrinks to about 30 percent.
        with self.beat("B2") as b:
            header = beat_header(2, "WATT'S CONDENSER", A_COLOR)
            year = date_badge("1769", A_COLOR)
            watt = pill("JAMES WATT", A_COLOR, size=24)
            names = VGroup(year, watt).arrange(RIGHT, buff=0.5).move_to([AXIS, 4.0, 0])
            engine = self.engine_icon().scale_to_fit_height(2.7).move_to([AXIS + 0.35, 1.55, 0])
            heap = self.coal_heap((4, 3, 2, 1), size=0.27).move_to([AXIS, -1.05, 0])
            with self.alignment_loop("B2 engine and coal") as align:
                align.centered(names, name="date and inventor")
                align.centered(heap, name="coal heap")
                align.inside_safe(VGroup(header, names, engine, heap), padding=0.14)
            cylinder, boiler = engine[2], engine[1]
            condenser = RoundedRectangle(corner_radius=0.16, width=0.95, height=0.95, fill_color=A_COLOR,
                                         fill_opacity=0.32, stroke_color=A_COLOR, stroke_width=4).move_to(cylinder)
            parked = np.array([AXIS - 2.35, boiler.get_y(), 0])
            pipe = VMobject(stroke_color=A_COLOR, stroke_width=6)
            pipe.set_points_as_corners([cylinder.get_left(), [parked[0], cylinder.get_y(), 0], parked + 0.475 * UP])
            steam = VGroup(*[Dot(cylinder.get_center() + [0, 0.3 - 0.3 * i, 0], radius=0.08, color=INK) for i in range(3)])
            flow = VMobject().set_points_as_corners([cylinder.get_center(), [parked[0], cylinder.get_y(), 0], parked])
            label = pill("CONDENSER", A_COLOR, size=20).move_to(parked + 0.88 * DOWN)
            small = self.coal_heap((2, 1), size=0.27, seed=90)
            small.move_to([AXIS, heap.get_bottom()[1] + small.height / 2, 0])
            half = pill("UNDER HALF", LINK_COLOR, size=24).next_to(small, RIGHT, buff=0.55)
            with self.alignment_loop("B2 result") as align:
                align.centered(small, name="smaller heap")
                align.inside_safe(VGroup(header, names, engine, condenser.copy().move_to(parked), label, small, half),
                                  padding=0.14)

            self.add(header)
            self.play(FadeIn(names, shift=0.2 * DOWN), Create(engine), FadeIn(condenser),
                      FadeIn(heap, shift=0.2 * UP), FadeIn(steam), run_time=0.16 * b.duration)
            self.sfx("swipe.wav", -15)
            self.play(condenser.animate.move_to(parked), Create(pipe), run_time=0.24 * b.duration)
            self.sfx("wash.wav", -16)
            self.play(LaggedStart(*[MoveAlongPath(s, flow) for s in steam], lag_ratio=0.25), FadeIn(label),
                      run_time=0.14 * b.duration)
            self.play(ReplacementTransform(heap, small), FadeOut(steam), run_time=0.26 * b.duration)
            self.play(GrowFromCenter(half), Indicate(small, color=LINK_COLOR, scale_factor=1.1),
                      run_time=0.12 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B3: the rebound. One engine's coal per job shrinks, engines multiply, and the coal
        # total grows past where it began.
        with self.beat("B3") as b:
            header = beat_header(3, "MORE ENGINES, MORE COAL", A_COLOR)
            stack = self.rebound_stack(COAL_SKIN, self.engine_icon)
            self.rebound_time = min(REBOUND_MAX, 0.86 * b.duration)
            self.rebound(stack, self.rebound_time, intro=[header])
            self.hold(b)
        self.clear_stage(0.2)

        # B4: Jevons's rule as three tiles that play in order: cost down, uses up, total up.
        with self.beat("B4") as b:
            header = beat_header(4, "AN ECONOMIST'S RULE", LINK_COLOR)
            badge = title("JEVONS PARADOX", 58, LINK_COLOR)
            when = VGroup(date_badge("1865", LINK_COLOR), pill("W. S. JEVONS", LINK_COLOR, size=24)).arrange(RIGHT, buff=0.45)
            tiles = VGroup(*[RoundedRectangle(corner_radius=0.18, width=1.85, height=2.7, fill_color=FAINT,
                                              fill_opacity=0.55, stroke_color=LINK_COLOR, stroke_width=2)
                             for _ in range(3)]).arrange(RIGHT, buff=0.28)
            VGroup(badge, when, tiles).arrange(DOWN, buff=0.55).move_to([AXIS, 1.75, 0])
            with self.alignment_loop("B4 rule") as align:
                align.centered(badge, name="badge")
                align.centered(when, name="date and author")
                align.even_row(tiles, gap=0.28, name="three tiles")
                align.inside_safe(VGroup(header, badge, when, tiles), padding=0.14)
            words = VGroup(text("COST DOWN", 20, LINK_COLOR, BOLD), text("USES UP", 20, LINK_COLOR, BOLD),
                           text("TOTAL UP", 20, LINK_COLOR, BOLD))
            for word, tile in zip(words, tiles):
                word.next_to(tile, DOWN, buff=0.24)
            c0, c1, c2 = (tile.get_center() for tile in tiles)
            cost = Rectangle(width=1.3, height=0.36, fill_color=INK, fill_opacity=0.85, stroke_width=0).move_to(c0)
            seed = Dot(c1, radius=0.12, color=INK)
            crowd = VGroup(*[Dot(radius=0.12, color=INK) for _ in range(9)]).arrange_in_grid(3, 3, buff=0.26).move_to(c1)
            grow = Rectangle(width=0.7, height=0.4, fill_color=LINK_COLOR, fill_opacity=0.7, stroke_width=0)
            grow.move_to([c2[0], tiles.get_bottom()[1] + 0.45, 0])

            self.add(header)
            self.play(FadeIn(badge, scale=0.92), FadeIn(when), FadeIn(tiles), FadeIn(cost), FadeIn(seed),
                      FadeIn(grow), run_time=0.28 * b.duration)
            self.play(cost.animate.stretch_to_fit_width(0.42), FadeIn(words[0]), run_time=0.20 * b.duration)
            self.sfx("spark.wav", -14)
            self.play(*[TransformFromCopy(seed, d) for d in crowd], FadeIn(words[1]), run_time=0.20 * b.duration)
            self.play(grow.animate.stretch_to_fit_height(1.9, about_edge=DOWN), FadeIn(words[2]),
                      run_time=0.20 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B5: a word splits into tokens; then the price of one quality level collapses.
        with self.beat("B5") as b:
            header = beat_header(5, "CHEAPER TOKENS", B_COLOR)
            whole = text("everything", 40, INK, BOLD)
            frame = RoundedRectangle(corner_radius=0.14, width=whole.width + 0.6, height=0.82, stroke_color=MUTED,
                                     stroke_width=3)
            word = VGroup(frame, whole.move_to(frame)).move_to([AXIS, 3.95, 0])
            tiles = VGroup(self.token_tile("every"), self.token_tile("thing")).arrange(RIGHT, buff=0.22)
            tiles.move_to(word)
            kind = text("TOKENS", 22, B_COLOR, BOLD).next_to(tiles, DOWN, buff=0.25)
            base = Line([AXIS - 2.0, -1.75, 0], [AXIS + 2.0, -1.75, 0], color=MUTED, stroke_width=4)
            price_bar = Rectangle(width=1.7, height=3.9, fill_color=B_COLOR, fill_opacity=0.55, stroke_color=B_COLOR,
                                  stroke_width=3).next_to(base, UP, buff=0)
            price = title("$20", 46, B_COLOR).next_to(price_bar, UP, buff=0.18)
            year = text("2022", 24, MUTED, BOLD).next_to(base, DOWN, buff=0.22)
            per = text("PER MILLION TOKENS", 20, MUTED, BOLD).next_to(year, DOWN, buff=0.12)
            with self.alignment_loop("B5 tokens and price") as align:
                align.centered(word, name="whole word")
                align.even_row(tiles, gap=0.22, name="token tiles")
                align.centered(VGroup(base, price_bar), name="price bar")
                align.inside_safe(VGroup(header, word, kind, price, price_bar, base, year, per), padding=0.14)
            low = title("$0.07", 46, B_COLOR).move_to([AXIS, base.get_y() + 0.55, 0])
            later = text("2024", 24, MUTED, BOLD).move_to(year)
            drop = pill("÷280", LINK_COLOR, size=40).move_to([AXIS, 0.85, 0])

            self.add(header)
            self.play(FadeIn(word, shift=0.15 * DOWN), run_time=0.10 * b.duration)
            self.sfx("swipe.wav", -15)
            self.play(ReplacementTransform(word, tiles), FadeIn(kind, shift=0.1 * UP), run_time=0.18 * b.duration)
            self.play(GrowFromEdge(price_bar, DOWN), Create(base), FadeIn(price), FadeIn(year), FadeIn(per),
                      run_time=0.12 * b.duration)
            self.sfx("ticks.wav", -15)
            self.play(price_bar.animate.stretch_to_fit_height(0.08, about_edge=DOWN), ReplacementTransform(price, low),
                      ReplacementTransform(year, later), run_time=0.32 * b.duration)
            self.play(GrowFromCenter(drop), run_time=0.14 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B6: the same stack, the same clock: answers instead of engines, tokens instead of coal.
        with self.beat("B6") as b:
            header = beat_header(6, "MORE ANSWERS, MORE TOKENS", B_COLOR)
            stack = self.rebound_stack(TOKEN_SKIN, self.answer_icon)
            self.rebound(stack, self.rebound_time, intro=[header])
            self.hold(b)
        self.clear_stage(0.2)

        # B7: the link runs back: a coal plant powers a data center, coal fills about 30 percent
        # of its power, and the plant's closing date slides later.
        with self.beat("B7") as b:
            header = beat_header(7, "AI FEEDS COAL", LINK_COLOR)
            plant = self.coal_plant().scale(1.05)
            center = self.data_center()
            plant.move_to([AXIS - 1.65, 3.15, 0])
            center.move_to([AXIS + 1.65, 3.15, 0])
            with self.alignment_loop("B7 plant and data center") as align:
                align.balanced_pair(plant, center, y=3.15, gap=1.5, name="plant and data center")
                align.inside_safe(VGroup(header, plant, center), padding=0.14)
            tags = VGroup(text("COAL PLANT", 22, A_COLOR, BOLD), text("DATA CENTER", 22, B_COLOR, BOLD))
            for tag, icon in zip(tags, (plant, center)):
                tag.set_x(icon.get_x()).set_y(2.0)
            wire = Line(plant.get_right() + 0.1 * RIGHT, center.get_left() + 0.1 * LEFT, color=LINK_COLOR, stroke_width=6)
            pulses = VGroup(*[Dot(wire.get_start(), radius=0.09, color=LINK_COLOR) for _ in range(3)])
            mix_frame = RoundedRectangle(corner_radius=0.12, width=5.4, height=0.64, fill_color=FAINT, fill_opacity=0.6,
                                         stroke_color=MUTED, stroke_width=3).move_to([AXIS, 0.55, 0])
            coal = Rectangle(width=0.08, height=0.48, fill_color=A_COLOR, fill_opacity=0.75, stroke_width=0)
            coal.align_to(mix_frame, LEFT).shift(0.08 * RIGHT).set_y(mix_frame.get_y())
            mix_label = text("DATA CENTER POWER", 20, MUTED, BOLD).next_to(mix_frame, UP, buff=0.18)
            share = text("ABOUT 30% COAL", 22, A_COLOR, BOLD).next_to(mix_frame, DOWN, buff=0.18).align_to(mix_frame, LEFT)
            track = Line([AXIS - 2.6, -1.45, 0], [AXIS + 2.6, -1.45, 0], color=MUTED, stroke_width=4)
            ticks = VGroup(*[Line([x, -1.57, 0], [x, -1.33, 0], color=MUTED, stroke_width=3)
                             for x in np.linspace(AXIS - 2.6, AXIS + 2.6, 7)])

            def flag(words, color):
                tip = Triangle(fill_color=color, fill_opacity=0.9, stroke_width=0).scale(0.16).rotate(PI)
                return VGroup(tip, text(words, 20, color, BOLD).next_to(tip, UP, buff=0.1))

            planned = flag("PLANNED CLOSE", MUTED).next_to([AXIS - 1.4, -1.45, 0], UP, buff=0.04)
            marker = flag("CLOSE", A_COLOR).next_to([AXIS - 1.4, -1.45, 0], UP, buff=0.04)
            later = pill("DELAYED", A_COLOR, size=20).move_to([AXIS + 1.4, -2.05, 0])
            with self.alignment_loop("B7 power mix and close date") as align:
                align.centered(VGroup(mix_label, mix_frame), name="power mix")
                align.centered(track, name="close-date track")
                align.inside_safe(VGroup(header, plant, center, tags, mix_label, mix_frame, share, track, planned, later),
                                  padding=0.14)

            self.add(header)
            self.play(FadeIn(plant, shift=0.15 * RIGHT), FadeIn(center, shift=0.15 * LEFT), FadeIn(tags),
                      Create(wire), FadeIn(mix_frame), FadeIn(mix_label), FadeIn(coal), run_time=0.14 * b.duration)
            self.sfx("ticks.wav", -15)
            self.play(LaggedStart(*[MoveAlongPath(p, wire) for p in pulses], lag_ratio=0.3), run_time=0.20 * b.duration)
            self.play(coal.animate.stretch_to_fit_width(0.30 * (5.4 - 0.16), about_edge=LEFT), FadeIn(share),
                      FadeOut(pulses), run_time=0.24 * b.duration)
            self.play(Create(track), FadeIn(ticks), FadeIn(marker, shift=0.15 * DOWN), run_time=0.10 * b.duration)
            self.sfx("swipe.wav", -15)
            self.add(planned)
            self.bring_to_front(marker)
            self.play(marker.animate.shift(2.8 * RIGHT), FadeIn(later, shift=0.1 * UP), run_time=0.22 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B8: the IEA's projection: the 2030 bar grows past twice the 2024 bar.
        with self.beat("B8") as b:
            header = beat_header(8, "IEA PROJECTION", B_COLOR)
            base = Line([AXIS - 2.4, -1.65, 0], [AXIS + 2.4, -1.65, 0], color=MUTED, stroke_width=4)
            now = Rectangle(width=1.5, height=2.0, fill_color=B_COLOR, fill_opacity=0.45, stroke_color=B_COLOR,
                            stroke_width=3)
            soon = now.copy()
            now.move_to([AXIS - 1.15, base.get_y() + 1.0, 0])
            soon.move_to([AXIS + 1.15, base.get_y() + 1.0, 0])
            with self.alignment_loop("B8 bars") as align:
                align.mirror_pair(now, soon, min_gap=0.6, name="2024 and 2030 bars")
                align.centered(base, name="baseline")
                align.inside_safe(VGroup(header, base, now, soon), padding=0.14)
            years = VGroup(text("2024", 26, MUTED, BOLD), text("2030", 26, MUTED, BOLD))
            for year, bar in zip(years, (now, soon)):
                year.set_x(bar.get_x()).set_y(base.get_y() - 0.4)
            first = text("415 TWh", 26, B_COLOR, BOLD).next_to(now, UP, buff=0.2)
            second = text("945 TWh", 26, B_COLOR, BOLD)
            tall = 2.0 * 945 / 415
            second.move_to([soon.get_x(), base.get_y() + tall + 0.32, 0])
            times = pill("×2.3", LINK_COLOR, size=30).move_to([AXIS - 1.15, base.get_y() + tall - 0.15, 0])
            with self.alignment_loop("B8 labels") as align:
                align.inside_safe(VGroup(header, base, now, soon, years, first, second, times), padding=0.14)

            self.add(header)
            self.play(Create(base), GrowFromEdge(now, DOWN), FadeIn(soon), FadeIn(years), FadeIn(first),
                      run_time=0.22 * b.duration)
            self.sfx("power-up.wav", -14)
            self.play(soon.animate.stretch_to_fit_height(tall, about_edge=DOWN), FadeIn(second, shift=0.3 * UP),
                      run_time=0.46 * b.duration)
            self.play(GrowFromCenter(times), run_time=0.20 * b.duration)
            self.hold(b)
        self.clear_stage(0.2)

        # B9: this episode's Connection Map; its plates are B1's, so the loop closes.
        with self.beat("B9") as b:
            header = beat_header(9, "JEVONS CONNECTION", LINK_COLOR)
            self.end_card(
                run_time=0.88 * b.duration,
                title=False,
                both_ways=True,
                tagline=("SAME TRICK", "TWO WORLDS"),
                sound="ping.wav",
                intro=[header],
                icons=(self.plate(self.engine_icon(), A_COLOR), self.plate(self.answer_icon(), B_COLOR)),
            )
            self.hold(b)

        self.wait(0.25)
