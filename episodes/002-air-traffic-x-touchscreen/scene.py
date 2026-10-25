"""002-air-traffic-x-touchscreen: a 1965 radar lab and the phone in your hand.

The approved words live only in script.md. B3 and B6 run one mechanism, `Episode.trick()`:
the same panel, finger path, charge lines, meter and timing, in two skins. Every label and
header here is written for this episode. Read AGENTS.md and STYLE_GUIDE.md before changing
it; check with `vid lint 002` and `vid align 002`.
"""

from dataclasses import dataclass

from kit import *

AXIS = float(STAGE_CENTER[0])
SCREEN_DARK = "#0D1A26"
FLIGHTS = ("FLT 12", "FLT 27", "FLT 33", "FLT 41")  # made-up labels, not real flights

# B3 and B6 share these: the same panel, wires, touch point and phase timing.
PANEL_W, PANEL_H = 4.3, 3.3
ROWS = (1.05, 0.35, -0.35, -1.05)   # wire heights, from the panel center
COLS = (-1.35, -0.45, 0.45, 1.35)   # the phone grid's columns
TOUCH_ROW, TOUCH_X = 2, 0.45        # the third wire, where the third column crosses it
TRICK_Y = 1.55
TRICK_PHASES = (0.22, 0.22, 0.22, 0.20, 0.14)  # show, touch, charge, find, settle
TRICK_MAX_TIME = 5.0


@dataclass(frozen=True)
class TouchSkin:
    """Everything that changes between B3 and B6. Geometry and timing do not."""

    color: str
    tag: str
    grid: bool                    # False: rows of wires (1965); True: rows and columns (phone)
    labels: tuple[str, ...] = ()  # one per wire, drawn above it


RADAR_SKIN = TouchSkin(A_COLOR, "WIRES ON A RADAR SCREEN", False, FLIGHTS)
PHONE_SKIN = TouchSkin(B_COLOR, "CLEAR WIRES UNDER GLASS", True)


def finger(color=INK):
    """A fingertip pointing up and left. The tip is at ORIGIN: shift(point) places a touch."""
    body = RoundedRectangle(corner_radius=0.3, width=0.6, height=2.3,
                            fill_color="#1B2130", fill_opacity=1, stroke_color=color, stroke_width=4)
    body.move_to(ORIGIN, aligned_edge=UP)
    nail = RoundedRectangle(corner_radius=0.13, width=0.36, height=0.46,
                            fill_color=color, fill_opacity=0.12, stroke_color=color, stroke_width=2)
    nail.move_to(0.42 * DOWN)
    return VGroup(body, nail).rotate(PI / 6, about_point=ORIGIN)


def radar_scope(radius, color=A_COLOR):
    """Face, range rings, cross and a sweep (index 3) that turns about the face center."""
    face = Circle(radius=radius, stroke_color=color, stroke_width=5, fill_color=SCREEN_DARK, fill_opacity=1)
    rings = VGroup(*[Circle(radius=radius * k, stroke_color=color, stroke_width=1.5, stroke_opacity=0.35)
                     for k in (1 / 3, 2 / 3)])
    cross = VGroup(Line(radius * LEFT, radius * RIGHT), Line(radius * UP, radius * DOWN))
    cross.set_stroke(color, 1.5, opacity=0.25)
    sweep = VGroup(
        AnnularSector(inner_radius=0, outer_radius=radius, angle=PI / 4, start_angle=PI / 2,
                      fill_color=color, fill_opacity=0.18, stroke_width=0),
        Line(ORIGIN, radius * UP, color=color, stroke_width=4),
    )
    return VGroup(face, rings, cross, sweep)


def blip(point, label, color=A_COLOR, size=16):
    dot = Dot(point, radius=0.08, color=INK)
    return VGroup(dot, text(label, size, color, BOLD).next_to(dot, UR, buff=0.05))


def step_card(label, icon, color):
    box = RoundedRectangle(corner_radius=0.23, width=1.72, height=2.08,
                           fill_color=color, fill_opacity=0.09, stroke_color=color, stroke_width=3)
    icon.move_to(box.get_center() + 0.28 * UP)
    return VGroup(box, icon, title(label, 24, color).move_to(box.get_center() + 0.64 * DOWN))


def charge_icon(color=LINK_COLOR):
    waves = VGroup(*[Arc(radius=r, start_angle=PI / 4, angle=PI / 2, color=color, stroke_width=4)
                     for r in (0.2, 0.36, 0.52)])
    return VGroup(waves, Dot(ORIGIN, radius=0.07, color=color)).move_to(ORIGIN)


def target_icon(color=INK):
    ring = Circle(radius=0.32, color=color, stroke_width=4)
    ticks = VGroup(*[Line(0.42 * d, 0.22 * d, color=color, stroke_width=4) for d in (UP, DOWN, LEFT, RIGHT)])
    return VGroup(ring, ticks, Dot(ORIGIN, radius=0.06, color=color))


def steps(scale=1.0, color=LINK_COLOR):
    """The TOUCH · CHARGE · FIND cards, as in B4."""
    return VGroup(
        step_card("TOUCH", finger().scale(0.4, about_point=ORIGIN), color),
        step_card("CHARGE", charge_icon(), color),
        step_card("FIND", target_icon(), color),
    ).arrange(RIGHT, buff=0.30).scale(scale)


def flight_strip(label, color=B_COLOR):
    strip = RoundedRectangle(corner_radius=0.06, width=2.1, height=0.42,
                             fill_color=FAINT, fill_opacity=1, stroke_color=color, stroke_width=2)
    bar = Rectangle(width=0.12, height=0.42, fill_color=color, fill_opacity=1, stroke_width=0)
    bar.align_to(strip, LEFT)
    words = text(label, 16, INK, BOLD).next_to(bar, RIGHT, buff=0.16)
    return VGroup(strip, bar, words)


class Episode(ShortScene):
    """Final nine-beat infographic, timed entirely from the unchanged script."""

    def trick(self, beat_id, skin, run_time, intro=(), badge=None):
        """Touch, charge, find. B3 plays it on a 1965 radar screen; B6 replays it on phone glass.

        Same panel, wires, finger path, charge lines, meter and phase timing every time.
        `intro` fades in with the first phase; `badge` cards (B6) appear one per step.
        """
        panel = RoundedRectangle(corner_radius=0.22, width=PANEL_W, height=PANEL_H,
                                 fill_color=SCREEN_DARK, fill_opacity=1, stroke_color=skin.color, stroke_width=5)
        frame = RoundedRectangle(corner_radius=0.14, width=1.22, height=PANEL_H,
                                 stroke_color=FAINT, stroke_width=2)
        bars = VGroup(*[Rectangle(width=0.2, height=0.25, fill_color=MUTED, fill_opacity=0.8, stroke_width=0)
                        for _ in ROWS]).arrange(RIGHT, buff=0.14, aligned_edge=DOWN)
        bars.move_to(frame.get_bottom() + 0.7 * UP, aligned_edge=DOWN)
        meter = VGroup(frame, bars, text("CIRCUIT", 17, MUTED, BOLD).next_to(bars, DOWN, buff=0.18))
        VGroup(meter, panel).arrange(RIGHT, buff=0.4).move_to([AXIS, TRICK_Y, 0])
        with self.alignment_loop(f"{beat_id} touch mechanism") as align:
            align.even_row([meter, panel], y=TRICK_Y, gap=0.4)
            align.inside_safe(VGroup(meter, panel))
        c = panel.get_center()
        wire_alpha = 0.55 if skin.grid else 1.0
        wires = VGroup(*[Line(c + [-PANEL_W / 2 + 0.25, y, 0], c + [PANEL_W / 2 - 0.25, y, 0],
                              color=skin.color, stroke_width=4, stroke_opacity=wire_alpha) for y in ROWS])
        cols = VGroup(*[Line(c + [x, PANEL_H / 2 - 0.25, 0], c + [x, -PANEL_H / 2 + 0.25, 0],
                             color=skin.color, stroke_width=4, stroke_opacity=wire_alpha) for x in COLS])
        labels = VGroup(*[text(name, 16, skin.color, BOLD).move_to(c + [-PANEL_W / 2 + 0.3, y + 0.19, 0], aligned_edge=LEFT)
                          for name, y in zip(skin.labels, ROWS)])
        tag = pill(skin.tag, skin.color).next_to(panel, UP, buff=0.3)
        touch = c + [TOUCH_X, ROWS[TOUCH_ROW], 0]
        tip = finger().shift(touch + 0.06 * UP)
        start = 2.6 * RIGHT + 1.6 * DOWN
        tip.shift(start)
        arcs = VGroup(*[ArcBetweenPoints(touch + [dx, 0, 0], touch + 0.06 * UP, angle=0.9 if dx < 0 else -0.9,
                                         color=LINK_COLOR, stroke_width=3) for dx in (-0.85, -0.45, 0.45, 0.85)])
        ring = Circle(radius=0.3, color=INK, stroke_width=4).move_to(touch)
        node = Dot(touch, radius=0.09, color=INK)
        cards = list(badge) if badge is not None else []

        def step(k):
            return [FadeIn(cards[k], scale=0.8)] if k < len(cards) else []

        t = [run_time * share for share in TRICK_PHASES]
        shown = [wires, *([cols] if skin.grid else []), *([labels] if skin.labels else [])]
        self.play(*[FadeIn(m) for m in intro], DrawBorderThenFill(panel), FadeIn(meter), FadeIn(tag),
                  *[Create(m) for m in shown], run_time=t[0])
        self.play(tip.animate.shift(-start), *step(0), run_time=t[1])
        self.sfx("tap.wav", -10)
        self.sfx("spark.wav", -15)
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.15),
                  bars[TOUCH_ROW].animate.stretch_to_fit_height(1.7, about_edge=DOWN).set_fill(LINK_COLOR, 1),
                  *step(1), run_time=t[2])
        found = [wires[TOUCH_ROW].animate.set_stroke(INK, width=6, opacity=1)]
        if skin.grid:
            found += [cols[2].animate.set_stroke(INK, width=6, opacity=1), GrowFromCenter(node)]
        if skin.labels:
            found += [labels[TOUCH_ROW].animate.set_color(INK).scale(1.15)]
        self.sfx("ping.wav", -16)
        self.play(*found, GrowFromCenter(ring), Flash(touch, color=LINK_COLOR, flash_radius=0.6), *step(2), run_time=t[3])
        self.play(ring.animate.scale(1.4).set_stroke(opacity=0), tip.animate.shift(0.3 * RIGHT + 0.25 * DOWN),
                  run_time=t[4])

    def construct(self):
        # B1: the cover is on screen at frame 0: the pair's title over a phone that holds a radar.
        with self.beat("B1") as b:
            hook = VGroup(
                title("AIR TRAFFIC", 46, A_COLOR),
                VGroup(title("×", 38, LINK_COLOR), title("TOUCHSCREEN", 46, B_COLOR)).arrange(RIGHT, buff=0.2),
            ).arrange(DOWN, buff=0.12).move_to([AXIS, 4.45, 0])
            device = phone(5.4)
            device.next_to(hook, DOWN, buff=0.30).set_x(AXIS)
            with self.alignment_loop("B1 opening composition") as align:
                align.even_column([hook, device], gap=0.30)
                align.inside_safe(VGroup(hook, device), padding=0.08)
            screen = device[1]
            scope = radar_scope(1.05).move_to(screen.get_center() + 0.35 * UP)
            centre = scope[0].get_center()
            blips = VGroup(*[blip(centre + offset, name, size=13) for offset, name in
                             zip(([-0.55, 0.42, 0], [0.38, 0.18, 0], [-0.15, -0.55, 0]), FLIGHTS)])
            target = blips[1][0].get_center()
            tip = finger().scale(0.8, about_point=ORIGIN).shift(target + 0.05 * UP)
            start = 2.4 * RIGHT + 1.4 * DOWN
            tip.shift(start)
            self.add(device, scope, blips, hook)
            self.sfx("power-up.wav", -16)
            self.play(Rotate(scope[3], -PI, about_point=centre, rate_func=linear), run_time=b.duration * 0.30)
            self.play(Rotate(scope[3], -PI / 2, about_point=centre, rate_func=linear),
                      tip.animate.shift(-start), run_time=b.duration * 0.22)
            self.sfx("tap.wav", -9)
            ripples = VGroup(*[Circle(radius=0.12, color=LINK_COLOR, stroke_width=4).move_to(target) for _ in range(2)])
            pick = Circle(radius=0.22, color=INK, stroke_width=4).move_to(target)
            self.play(LaggedStart(*[r.animate.scale(4.5).set_stroke(opacity=0) for r in ripples], lag_ratio=0.3),
                      GrowFromCenter(pick), run_time=b.duration * 0.18)
            self.play(hook.animate.scale(1.06), run_time=b.duration * 0.10)
            self.play(hook.animate.scale(1 / 1.06), run_time=b.duration * 0.10)
            self.hold(b)
        self.clear_stage(0.22)

        # B2: 1965, a British radar lab. Blips drift on a turning scope; one touch picks a flight.
        with self.beat("B2") as b:
            header = beat_header(2, "A radar lab", A_COLOR)
            date = date_badge("1965", A_COLOR)
            place = pill("BRITISH RADAR LAB", A_COLOR)
            VGroup(date, place).arrange(RIGHT, buff=0.30).move_to([AXIS, 3.95, 0])
            scope = radar_scope(1.75).move_to([AXIS, 1.15, 0])
            with self.alignment_loop("B2 date and place") as align:
                align.balanced_pair(date, place, y=3.95, gap=0.30)
                align.inside_safe(VGroup(date, place))
            with self.alignment_loop("B2 radar scope") as align:
                align.centered(scope, axis_y=1.15, vertical=True)
                align.inside_safe(scope)
            centre = scope[0].get_center()
            offsets = ([-0.95, 0.75, 0], [0.55, 0.95, 0], [-0.35, -0.65, 0], [0.85, -0.35, 0])
            blips = VGroup(*[blip(centre + o, name) for o, name in zip(offsets, FLIGHTS)])
            drift = ([0.25, -0.12, 0], [-0.2, -0.15, 0], [0.22, 0.1, 0], [-0.1, 0.22, 0])
            self.play(FadeIn(header), FadeIn(date, scale=0.8), FadeIn(place), DrawBorderThenFill(scope[0]),
                      FadeIn(scope[1:]), run_time=b.duration * 0.18)
            self.sfx("ping.wav", -18)
            self.play(Rotate(scope[3], -TAU, about_point=centre, rate_func=linear),
                      LaggedStart(*[FadeIn(x) for x in blips], lag_ratio=0.2), run_time=b.duration * 0.30)
            target = blips[2][0].get_center() + drift[2]
            tip = finger().shift(target + 0.05 * UP)
            start = 2.6 * RIGHT + 1.5 * DOWN
            tip.shift(start)
            self.play(Rotate(scope[3], -PI, about_point=centre, rate_func=linear),
                      *[x.animate.shift(d) for x, d in zip(blips, drift)],
                      tip.animate.shift(-start), run_time=b.duration * 0.24)
            self.sfx("tap.wav", -10)
            pick = Circle(radius=0.26, color=INK, stroke_width=4).move_to(target)
            self.play(GrowFromCenter(pick), blips[2][1].animate.set_color(INK).scale(1.2),
                      Flash(target, color=LINK_COLOR, flash_radius=0.5), run_time=b.duration * 0.13)
            self.hold(b)
        self.clear_stage(0.22)

        # B3: the trick on a 1965 radar screen. B6 replays it exactly.
        with self.beat("B3") as b:
            header = beat_header(3, "Wires that feel", LINK_COLOR)
            self.trick_time = min(TRICK_MAX_TIME, 0.8 * b.duration)
            self.trick("B3", RADAR_SKIN, self.trick_time, intro=[header])
            self.hold(b)
        self.clear_stage(0.22)

        # B4: the three steps become a mnemonic.
        with self.beat("B4") as b:
            header = beat_header(4, "How a touch is found", LINK_COLOR)
            cards = steps().move_to([AXIS, 1.3, 0])
            with self.alignment_loop("B4 step cards") as align:
                align.even_row(cards, y=1.3, gap=0.30)
                align.inside_safe(cards)
            arrows = VGroup(*[Arrow(cards[i].get_right(), cards[i + 1].get_left(), buff=0.06,
                                    color=LINK_COLOR, stroke_width=3, max_tip_length_to_length_ratio=0.3)
                              for i in range(2)])
            self.play(FadeIn(header), run_time=b.duration * 0.12)
            self.sfx("ticks.wav", -15)
            self.play(LaggedStart(*[FadeIn(card, shift=0.45 * UP, scale=0.8) for card in cards], lag_ratio=0.25),
                      run_time=b.duration * 0.48)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2), run_time=b.duration * 0.18)
            self.play(cards.animate.scale(0.68).move_to([AXIS, 2.5, 0]), FadeOut(arrows), run_time=b.duration * 0.16)
            self.hold(b)
        self.clear_stage(0.22)

        # B5: about forty years later the keys fall away and the screen takes the whole front.
        with self.beat("B5") as b:
            header = beat_header(5, "No more keys", B_COLOR)
            date = date_badge("2007", B_COLOR).move_to([-2.25, 3.95, 0])
            body = RoundedRectangle(corner_radius=0.36, width=2.7, height=5.0, fill_color="#131722",
                                    fill_opacity=1, stroke_color=FAINT, stroke_width=5).move_to([AXIS, 0.85, 0])
            with self.alignment_loop("B5 keypad phone") as align:
                align.centered(body, axis_y=0.85, vertical=True)
                align.inside_safe(VGroup(body, date))
            small = RoundedRectangle(corner_radius=0.12, width=2.2, height=1.9, fill_color="#0B0E14",
                                     fill_opacity=1, stroke_color=B_COLOR, stroke_width=3)
            small.move_to(body.get_top() + 1.25 * DOWN)
            keys = VGroup(*[RoundedRectangle(corner_radius=0.08, width=0.56, height=0.36, fill_color=FAINT,
                                             fill_opacity=1, stroke_color=MUTED, stroke_width=2) for _ in range(12)])
            keys.arrange_in_grid(4, 3, buff=(0.16, 0.14)).next_to(small, DOWN, buff=0.3)
            full = RoundedRectangle(corner_radius=0.26, width=2.44, height=4.38, fill_color=B_COLOR,
                                    fill_opacity=0.10, stroke_color=B_COLOR, stroke_width=3).move_to(body).shift(0.05 * DOWN)
            self.play(FadeIn(header), FadeIn(date, scale=0.8), DrawBorderThenFill(body), FadeIn(small),
                      LaggedStart(*[FadeIn(k) for k in keys], lag_ratio=0.04), run_time=b.duration * 0.20)
            self.sfx("whoosh.wav", -16)
            self.play(LaggedStart(*[k.animate.shift(0.7 * DOWN).set_opacity(0) for k in keys], lag_ratio=0.06),
                      run_time=b.duration * 0.30)
            self.play(Transform(small, full), run_time=b.duration * 0.28)
            glint = Line(full.get_corner(UL) + [0.3, -0.4, 0], full.get_corner(UL) + [1.1, -1.2, 0],
                         color=INK, stroke_width=4, stroke_opacity=0.6)
            self.play(Create(glint), small.animate.set_fill(B_COLOR, 0.18), run_time=b.duration * 0.12)
            self.hold(b)
        self.clear_stage(0.22)

        # B6: the same trick on phone glass, same geometry and timing; the B4 badge lights step by step.
        with self.beat("B6") as b:
            header = beat_header(6, "Under the glass", B_COLOR)
            badge = steps(0.55).move_to([AXIS, -1.65, 0])
            with self.alignment_loop("B6 step badge") as align:
                align.even_row(badge, y=-1.65, gap=0.30 * 0.55)
                align.inside_safe(badge)
            self.trick("B6", PHONE_SKIN, self.trick_time, intro=[header], badge=badge)
            self.hold(b)
        self.clear_stage(0.22)

        # B7: the arrow reverses, and touch returns to the tower: strips on glass, not paper.
        with self.beat("B7") as b:
            header = beat_header(7, "Back to the tower", A_COLOR)
            mini_scope = radar_scope(0.62).move_to([AXIS - 1.21, 3.45, 0])
            mini_phone = phone(1.6, B_COLOR).move_to([AXIS + 1.21, 3.45, 0])
            with self.alignment_loop("B7 return pair") as align:
                align.mirror_pair(mini_scope, mini_phone, y=3.45, min_gap=1.4)
                align.inside_safe(VGroup(mini_scope, mini_phone))
            back = CurvedArrow(mini_phone.get_left() + 0.1 * LEFT, mini_scope.get_right() + 0.1 * RIGHT,
                               angle=0.5, color=LINK_COLOR, stroke_width=5)
            self.play(FadeIn(header), GrowFromCenter(mini_scope), GrowFromCenter(mini_phone), run_time=b.duration * 0.12)
            self.sfx("whoosh.wav", -15)
            self.play(Create(back), run_time=b.duration * 0.13)
            board = RoundedRectangle(corner_radius=0.22, width=5.6, height=3.0, fill_color=SCREEN_DARK,
                                     fill_opacity=1, stroke_color=A_COLOR, stroke_width=5).move_to([AXIS, 1.25, 0])
            with self.alignment_loop("B7 strip board") as align:
                align.centered(board, axis_y=1.25, vertical=True)
                align.inside_safe(board)
            heads = VGroup(text("TAXI", 18, MUTED, BOLD), text("RUNWAY", 18, MUTED, BOLD))
            lanes = [board.get_center() + [-1.35, 0, 0], board.get_center() + [1.35, 0, 0]]
            for head, lane in zip(heads, lanes):
                head.move_to(lane + [0, 1.15, 0])
            strips = VGroup(*[flight_strip(name) for name in FLIGHTS[:3]])
            strips.arrange(DOWN, buff=0.16).move_to(lanes[0] + [0, -0.05, 0])
            paper = VGroup(RoundedRectangle(corner_radius=0.04, width=2.1, height=0.42, fill_color=MUTED,
                                            fill_opacity=0.35, stroke_color=MUTED, stroke_width=2),
                           text("PAPER STRIP", 16, INK, BOLD))
            paper[1].move_to(paper[0])
            paper.next_to(board, DOWN, buff=0.35)
            self.play(FadeOut(mini_scope), FadeOut(mini_phone), FadeOut(back),
                      DrawBorderThenFill(board), FadeIn(heads), FadeIn(paper), run_time=b.duration * 0.12)
            self.play(LaggedStart(*[FadeIn(s, shift=0.2 * RIGHT) for s in strips], lag_ratio=0.2),
                      run_time=b.duration * 0.14)
            grab = strips[0]
            tip = finger().shift(grab.get_center() + 0.4 * RIGHT + 0.05 * UP)
            start = 2.2 * RIGHT + 1.6 * DOWN
            tip.shift(start)
            self.play(tip.animate.shift(-start), run_time=b.duration * 0.12)
            self.sfx("whoosh.wav", -15)
            move = lanes[1] + [0, 0.62, 0] - grab.get_center()
            self.play(grab.animate.shift(move), tip.animate.shift(move), run_time=b.duration * 0.15)
            strike = Line(paper.get_left() + 0.1 * RIGHT, paper.get_right() + 0.1 * LEFT, color=INK, stroke_width=4)
            self.play(Create(strike), paper.animate.set_opacity(0.35), run_time=b.duration * 0.10)
            self.hold(b)
        self.clear_stage(0.22)

        # B8: most phones and tablets feel a finger this way: a wave of touches across devices.
        with self.beat("B8") as b:
            header = beat_header(8, "Today", B_COLOR)
            rows = VGroup()
            for r in range(3):
                row = VGroup()
                for i in range(4):
                    if (i + r) % 2:
                        device = RoundedRectangle(corner_radius=0.12, width=0.95, height=1.25, fill_color="#131722",
                                                  fill_opacity=1, stroke_color=B_COLOR, stroke_width=3)
                    else:
                        device = phone(1.25, B_COLOR)
                    row.add(device)
                rows.add(row.arrange(RIGHT, buff=0.45))
            rows.arrange(DOWN, buff=0.40).move_to([AXIS, 1.35, 0])
            with self.alignment_loop("B8 device grid") as align:
                for row in rows:
                    align.even_row(row, gap=0.45, name="device row")
                align.even_column(rows, gap=0.40, center_y=1.35)
                align.inside_safe(rows)
            devices = [d for row in rows for d in row]
            self.play(FadeIn(header), LaggedStart(*[FadeIn(d, scale=0.8) for d in devices], lag_ratio=0.05),
                      run_time=b.duration * 0.30)
            self.sfx("ticks.wav", -15)
            touches = [Circle(radius=0.1, color=LINK_COLOR, stroke_width=4).move_to(d.get_center()) for d in devices]
            self.play(LaggedStart(*[t.animate.scale(4).set_stroke(opacity=0) for t in touches], lag_ratio=0.08),
                      run_time=b.duration * 0.50)
            self.hold(b)
        self.clear_stage(0.22)

        # B9: the Connection Map grows: both directions resolve into this episode's link.
        with self.beat("B9") as b:
            header = beat_header(9, "Connection map", LINK_COLOR)
            self.end_card(run_time=b.duration * 0.90, title=False, both_ways=True,
                          tagline=("SAME TRICK", "TWO WORLDS"), sound="spark.wav", intro=[header],
                          icons=(radar_scope(0.6), phone(1.4, B_COLOR)))
            self.hold(b)

        self.wait(0.35)
