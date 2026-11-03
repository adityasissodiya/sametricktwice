"""A complete landscape scene that passes the source gates. Read it for its shape, then write your
own: never copy it into a video. It tells the test suite's made-up story (tests/episode_fixture.py),
and tests/test_resources.py runs `vid check`'s rules on it, so it cannot go stale.

What to notice:
- Each beat times every self.play as a share of b.duration, and the shares add up to at least 0.65.
- trick() is a method of Episode, because the gates give only those methods credit. B3 sets its
  clock once and B6 passes the same clock, so the same motion plays twice in two skins.
- Every on-screen word and every causal name (MoveAlongPath, Transform, .animate.shift) is here in
  scene.py, where the gates read them. The resources only draw.
- Each layout registers its alignment intent before it moves.
- The first play is linear, because easing starts too slowly for opening-quality.
- B9 rebuilds B1's cover, so the last pose flows into the first.
"""

from types import SimpleNamespace

from kit.landscape import *
from resources import *

TRICK_CAP = 5.0        # seconds; short enough for the shorter of B3 and B6
COVER_X = 3.3          # the two plates sit this far from the axis
PLATE_SIDE = 3.0
CHAMBER_W, CHAMBER_H = 3.6, 2.5
CHAMBER_Y = -0.42
RISE = 0.85            # how far the push lifts the cap
SIDE_X = 3.35          # the two small chambers of B8
SIDE_SCALE = 0.72

# A skin is a SimpleNamespace, not a dict: lint reads dict keys as on-screen words.
KETTLE = SimpleNamespace(color=A_COLOR, load="LID")
ROCKET = SimpleNamespace(color=B_COLOR, load="ROCKET")


def kettle(color):
    """Body (0), lid and knob (1), spout (2)."""
    body = RoundedRectangle(corner_radius=0.3, width=1.5, height=1.05, fill_color=color, fill_opacity=0.25,
                            stroke_color=color, stroke_width=5)
    lid = RoundedRectangle(corner_radius=0.05, width=0.95, height=0.13, fill_color=color, fill_opacity=0.9,
                           stroke_width=0).next_to(body, UP, buff=0.04)
    knob = Dot(radius=0.07, color=color).next_to(lid, UP, buff=0)
    edge = body.get_right()
    spout = Polygon(edge + 0.25 * UP + 0.06 * LEFT, edge + 0.55 * RIGHT + 0.42 * UP, edge + 0.5 * RIGHT + 0.5 * UP,
                    edge + 0.1 * DOWN + 0.06 * LEFT, fill_color=color, fill_opacity=0.6, stroke_color=color, stroke_width=4)
    return VGroup(body, VGroup(lid, knob), spout).move_to(ORIGIN)


def rocket(color):
    """Body (0), nose (1), fins (2), window (3)."""
    body = RoundedRectangle(corner_radius=0.1, width=0.66, height=1.3, fill_color=color, fill_opacity=0.25,
                            stroke_color=color, stroke_width=5)
    top = body.get_top()
    nose = Polygon(top + 0.33 * LEFT, top + 0.33 * RIGHT, top + 0.5 * UP, fill_color=color, fill_opacity=0.8,
                   stroke_color=color, stroke_width=4)
    foot = body.get_bottom()
    fins = VGroup(*[Polygon(foot + 0.33 * side, foot + 0.33 * side + 0.45 * UP, foot + 0.62 * side + 0.1 * DOWN,
                            fill_color=color, fill_opacity=0.8, stroke_width=0) for side in (LEFT, RIGHT)])
    window = Circle(radius=0.14, fill_color=BG, fill_opacity=1, stroke_color=color, stroke_width=4).shift(0.25 * UP)
    return VGroup(body, nose, fins, window).move_to(ORIGIN)


def cover():
    """B1's first frame and B9's last: the two worlds on matched plates, with the sign between."""
    left = icons.plate(kettle(A_COLOR), A_COLOR, PLATE_SIDE).move_to([-COVER_X, -0.1, 0])
    right = icons.plate(rocket(B_COLOR), B_COLOR, PLATE_SIDE).move_to([COVER_X, -0.1, 0])
    sign = title("×", 90, LINK_COLOR).move_to([0, -0.1, 0])
    return SimpleNamespace(left=left, right=right, sign=sign)


def chamber(skin, filled=False):
    """The mechanism's one geometry. Only the color and the word on the cap change between worlds."""
    wall = RoundedRectangle(corner_radius=0.18, width=CHAMBER_W, height=CHAMBER_H, fill_color=skin.color, fill_opacity=0.08,
                            stroke_color=skin.color, stroke_width=6).move_to([0, CHAMBER_Y, 0])
    liquid = RoundedRectangle(corner_radius=0.12, width=CHAMBER_W - 0.24, height=0.42, fill_color=skin.color,
                              fill_opacity=0.5, stroke_width=0).align_to(wall, DOWN).shift(0.12 * UP)
    cap = RoundedRectangle(corner_radius=0.08, width=CHAMBER_W - 0.12, height=0.24, fill_color=skin.color, fill_opacity=0.95,
                           stroke_width=0).next_to(wall, UP, buff=0.03)
    word = title(skin.load, 30, skin.color).next_to(cap, UP, buff=0.12)
    burner = icons.flame(skin.color, 0.5).next_to(wall, DOWN, buff=0.06)
    slots = [[x, y, 0] for y in (-0.3, 0.3) for x in (-1.2, -0.72, -0.24, 0.24, 0.72, 1.2)]
    rest = [slot if filled else [slot[0], liquid.get_top()[1], 0] for slot in slots]
    dots = VGroup(*[Dot(radius=0.1, color=LINK_COLOR).move_to(point) for point in rest])
    return SimpleNamespace(wall=wall, liquid=liquid, cap=cap, word=word, burner=burner, dots=dots, slots=slots)


def machine(rig):
    return VGroup(rig.wall, rig.liquid, rig.cap, rig.word, rig.burner, rig.dots)


class Episode(StageTools, LandscapeScene):
    def trick(self, skin, run_time):
        """The mechanism. Heat turns liquid into dots that need more room, and they push the cap."""
        heat, fill, push = 0.22, 0.43, 0.35
        rig = chamber(skin)
        raised = rig.word.copy().shift(RISE * UP)
        with self.alignment_loop(f"{skin.load} chamber") as align:
            align.centered(rig.wall, name="chamber")
        self.fits(f"{skin.load} stage", machine(rig), raised)
        self.add(backdrop(skin.color), rig.wall, rig.liquid, rig.cap, rig.word)
        self.sfx("spark.wav", gain=-13)
        self.play(GrowFromEdge(rig.burner, DOWN), run_time=heat * run_time)
        self.add(rig.dots)
        self.sfx("pixels.wav", gain=-14)
        self.play(LaggedStart(*[MoveAlongPath(dot, route(dot, slot)) for dot, slot in zip(rig.dots, rig.slots)],
                              lag_ratio=0.08), run_time=fill * run_time)
        self.sfx("whoosh.wav", gain=-13)
        self.play(rig.cap.animate.shift(RISE * UP), rig.word.animate.shift(RISE * UP), rig.dots.animate.shift(RISE * UP),
                  run_time=push * run_time)
        self.sfx("tap.wav", gain=-12)
        return rig

    def construct(self):
        with self.beat("B1") as b:
            first = cover()
            self.header(1, "Unlikely relatives", LINK_COLOR)
            with self.alignment_loop("B1 cover") as align:
                align.mirror_pair(first.left, first.right, name="plates", axis_x=0.0)
                align.centered(first.sign, name="sign", axis_x=0.0)
            self.fits("B1 stage", first.left, first.right)
            self.add(first.left, first.right, first.sign)
            self.sfx("whoosh.wav", gain=-13)
            self.play(first.left.animate.shift(0.5 * LEFT), first.right.animate.shift(0.5 * RIGHT), rate_func=linear,
                      run_time=0.85 * b.duration)
            self.hold(b)

        with self.beat("B2") as b:
            pot = kettle(A_COLOR).scale(2.3).move_to([0, -0.5, 0])
            badge = date_badge("1900", A_COLOR).move_to([-4.7, 2.0, 0])
            self.fits("B2 stage", pot, badge, pot[1].copy().shift(0.9 * UP))
            self.cut()
            self.header(2, "One curious cook", A_COLOR)
            self.add(backdrop(A_COLOR))
            self.sfx("tap.wav", gain=-14)
            self.play(FadeIn(pot, shift=0.4 * UP), FadeIn(badge), run_time=0.16 * b.duration)
            # One play per jump: a play inside a for loop counts once for motion-coverage.
            self.sfx("tap.wav", gain=-15)
            self.play(pot[1].animate(rate_func=there_and_back).shift(0.4 * UP), run_time=0.2 * b.duration)
            self.sfx("tap.wav", gain=-14)
            self.play(pot[1].animate(rate_func=there_and_back).shift(0.65 * UP), run_time=0.2 * b.duration)
            self.sfx("tap.wav", gain=-13)
            self.play(pot[1].animate(rate_func=there_and_back).shift(0.9 * UP), run_time=0.24 * b.duration)
            self.hold(b)

        with self.beat("B3") as b:
            self.cut()
            self.header(3, "How it works", A_COLOR)
            self.trick_time = min(TRICK_CAP, 0.8 * b.duration)
            rig = self.trick(KETTLE, self.trick_time)
            self.hold(b)

        with self.beat("B4") as b:
            self.header(4, "The whole trick", LINK_COLOR)
            steps = phase_pills(("HEAT", "STEAM", "PUSH"), direction=DOWN, buff=0.36)
            with self.alignment_loop("B4 steps") as align:
                align.even_column(list(steps), name="steps", x=3.2, center_y=0.2)
            self.fits("B4 stage", steps)
            self.sfx("swipe.wav", gain=-14)
            self.play(machine(rig).animate.shift(2.6 * LEFT), FadeIn(steps, shift=0.3 * LEFT), run_time=0.22 * b.duration)
            # Taps, then one ping: a ping rings for a second, and at most two cues may overlap.
            self.sfx("tap.wav", gain=-14)
            self.play(light(steps[0], LINK_COLOR), run_time=0.18 * b.duration)
            self.sfx("tap.wav", gain=-13)
            self.play(dim(steps[0]), light(steps[1], LINK_COLOR), run_time=0.18 * b.duration)
            self.sfx("ping.wav", gain=-13)
            self.play(dim(steps[1]), light(steps[2], LINK_COLOR), run_time=0.18 * b.duration)
            self.hold(b)

        with self.beat("B5") as b:
            self.cut()
            self.header(5, "A bigger job", B_COLOR)
            self.add(backdrop(B_COLOR))
            ground = Line([-5.6, -1.9, 0], [5.6, -1.9, 0], color=MUTED, stroke_width=6)
            load = RoundedRectangle(corner_radius=0.1, width=2.0, height=1.1, fill_color=B_COLOR, fill_opacity=0.35,
                                    stroke_color=B_COLOR, stroke_width=5).next_to(ground, UP, buff=0.04)
            goal = icons.star(B_COLOR, 1.6).move_to([0, 2.1, 0])
            climb = DashedLine(load.get_top() + 0.15 * UP, goal.get_bottom() + 0.15 * DOWN, color=MUTED, stroke_width=4)
            self.fits("B5 stage", ground, load, goal)
            self.sfx("tap.wav", gain=-14)
            self.play(FadeIn(ground), FadeIn(load, shift=0.5 * DOWN), run_time=0.2 * b.duration)
            self.sfx("swipe.wav", gain=-14)
            self.play(Create(climb), GrowFromCenter(goal), run_time=0.3 * b.duration)
            self.sfx("spark.wav", gain=-13)
            self.play(load.animate(rate_func=there_and_back).shift(0.7 * UP).set_color(ALERT), run_time=0.3 * b.duration)
            self.hold(b)

        with self.beat("B6") as b:
            self.cut()
            self.header(6, "The same motion", B_COLOR)
            self.trick(ROCKET, self.trick_time)
            self.hold(b)

        with self.beat("B7") as b:
            self.cut()
            self.header(7, "The return gift", LINK_COLOR)
            self.add(backdrop(LINK_COLOR))  # after a cut, the stage is never empty and dark
            home = icons.plate(kettle(A_COLOR), A_COLOR, PLATE_SIDE).move_to([-COVER_X, 0.2, 0])
            away = icons.plate(rocket(B_COLOR), B_COLOR, PLATE_SIDE).move_to([COVER_X, 0.2, 0])
            with self.alignment_loop("B7 plates") as align:
                align.mirror_pair(home, away, name="plates", axis_x=0.0)
            self.fits("B7 stage", home, away)
            sheet = Rectangle(width=0.9, height=0.5, fill_color=B_COLOR, fill_opacity=0.9, stroke_width=0).move_to(away)
            stronger = kettle(A_COLOR).scale_to_fit_height(home[1].height).move_to(home)
            stronger[0].set_fill(opacity=0.7)
            good = VGroup(icons.ring(A_COLOR), icons.tick(A_COLOR)).next_to(home, DOWN, buff=-0.3)
            self.sfx("tap.wav", gain=-14)
            self.play(FadeIn(home), FadeIn(away), run_time=0.15 * b.duration)
            self.add(sheet)
            self.sfx("whoosh.wav", gain=-13)
            self.play(MoveAlongPath(sheet, route(away, home, angle=-PI / 3)), run_time=0.4 * b.duration)
            self.sfx("shutter.wav", gain=-13)
            self.play(Transform(home[1], stronger), FadeOut(sheet), FadeIn(good, scale=0.6), run_time=0.25 * b.duration)
            self.hold(b)

        with self.beat("B8") as b:
            self.cut()
            self.header(8, "Both, today", LINK_COLOR)
            shade = backdrop(LINK_COLOR)
            self.add(shade)
            near = chamber(KETTLE, filled=True)
            far = chamber(ROCKET, filled=True)
            near_machine = machine(near).scale(SIDE_SCALE).move_to([-SIDE_X, -0.2, 0])
            far_machine = machine(far).scale(SIDE_SCALE).move_to([SIDE_X, -0.2, 0])
            with self.alignment_loop("B8 chambers") as align:
                align.mirror_pair(near_machine, far_machine, name="chambers", axis_x=0.0)
            lift = RISE * SIDE_SCALE * UP
            self.fits("B8 stage", near_machine, far_machine, near.word.copy().shift(lift))
            link = Flow(near.wall.get_right() + 0.2 * RIGHT, far.wall.get_left() + 0.2 * LEFT)
            self.sfx("tap.wav", gain=-14)
            self.play(FadeIn(near_machine), FadeIn(far_machine), run_time=0.2 * b.duration)
            self.add(link)
            self.sfx("whoosh.wav", gain=-14)
            self.play(near.cap.animate.shift(lift), near.word.animate.shift(lift), near.dots.animate.shift(lift),
                      far.cap.animate.shift(lift), far.word.animate.shift(lift), far.dots.animate.shift(lift),
                      run_time=0.5 * b.duration)
            self.hold(b)
            link.stop()

        with self.beat("B9") as b:
            self.remove(link, shade)
            self.header(9, "Connection map", LINK_COLOR)
            last = cover()
            words = VGroup(title("SAME TRICK", 34, LINK_COLOR), title("TWO WORLDS", 34, LINK_COLOR)).arrange(DOWN, buff=0.14)
            words.move_to([0, 1.95, 0])
            with self.alignment_loop("B9 cover") as align:
                align.mirror_pair(last.left, last.right, name="plates", axis_x=0.0)
                align.centered(last.sign, name="sign", axis_x=0.0)
                align.centered(words, name="words", axis_x=0.0)
            self.fits("B9 stage", last.left, last.right, words)
            self.sfx("power-up.wav", gain=-15)
            self.play(ReplacementTransform(near_machine, last.left), ReplacementTransform(far_machine, last.right),
                      FadeIn(last.sign, scale=0.4), run_time=0.45 * b.duration)
            self.sfx("ping.wav", gain=-13)
            self.play(FadeIn(words, shift=0.2 * DOWN), pop(last.sign), run_time=0.25 * b.duration)
            self.hold(b)

        self.wait(1)
