"""001-camera-x-chip: finished reference for the series infographic house style.

The approved words live only in script.md. ``Episode`` is the final animated scene;
``AnimaticEpisode`` is retained as a draft/reference and must never be selected for export.
Future episodes should follow STYLE_GUIDE.md and the alignment loop in AGENTS.md.
"""

from dataclasses import dataclass

from kit import *


class AnimaticEpisode(ShortScene):
    def construct(self):
        with self.beat("B1") as b:  # Hook
            # VIS: Start mid-motion: macro of a phone chip. A camera iris snaps shut over it,
            # flash, and the frame splits: CAMERA in blue on top, CHIP in orange below.
            self.placeholder(b)

        with self.beat("B2") as b:  # World A: the first photograph
            # VIS: Date stamp 1827. A pewter plate gets a brown coat (small label: bitumen of
            # Judea). A box camera at a window; rooftops project upside down onto the plate.
            self.placeholder(b)

        with self.beat("B3") as b:  # The trick
            # VIS: Cross-section: gray plate, brown asphalt. Violet rays hit the bright areas and
            # those patches lock hard. Oil flows over; soft patches dissolve; the pattern stays.
            # Cut to the real 1827 image.
            self.placeholder(b)

        with self.beat("B4") as b:  # Name the trick
            # VIS: The three steps shrink into three violet icons and park at the top of the
            # screen as a badge.
            self.placeholder(b)

        with self.beat("B5") as b:  # World B: tiny transistors
            # VIS: Date stamp 1957. A transistor too big for its slot. A microscope flips 180
            # degrees; rays now converge, and a big pattern above becomes a tiny one below.
            self.placeholder(b)

        with self.beat("B6") as b:  # Same trick, other world
            # VIS: Replay the B3 animation, re-skinned: germanium instead of the plate, orange
            # Kodak coating instead of asphalt, a transistor pattern instead of rooftops. The
            # badge lights up step by step. Then PHOTO · LITHO · GRAPHY splits into light, stone,
            # writing.
            self.placeholder(b)

        with self.beat("B7") as b:  # Payback: chips help cameras
            # VIS: The arrow reverses: orange flows back into blue. Date stamp 1975. A toaster-
            # sized camera; inside it, a 100 × 100 grid chip fills pixel by pixel.
            self.placeholder(b)

        with self.beat("B8") as b:  # Today
            # VIS: A modern lithography machine drawn as a camera: light source, mask, lens stack,
            # wafer. Three text labels: Nikon, Canon, Zeiss (no logos).
            self.placeholder(b)

        with self.beat("B9") as b:  # Kicker + map
            # VIS: Connection map: Camera (blue) and Chip (orange) join with a blue-to-orange
            # line.
            self.end_card()

        self.wait(1)


# Finished infographic scene -------------------------------------------------

BROWN = "#A66A3F"
METAL = "#8A93A5"
OIL = "#D9B45B"
AXIS = float(STAGE_CENTER[0])

# B3 and B6 run one mechanism: the same positions and the same phase timing.
TRICK_LIGHT_Y = 3.65
TRICK_STACK_Y = 0.70
TRICK_OIL_Y = 2.0
TRICK_PHASES = (0.20, 0.25, 0.14, 0.18, 0.23)  # coat, light, harden, oil, wash
TRICK_MAX_TIME = 4.4


@dataclass(frozen=True)
class TrickSkin:
    """Everything that changes between B3 and B6. Geometry and timing do not."""

    coat_color: str
    base_label: str
    coat_label: str
    mask: tuple[int, ...]  # 1 = the light reaches this block and hardens it


ASPHALT_SKIN = TrickSkin(BROWN, "METAL PLATE", "ASPHALT", (1, 1, 0, 1, 0, 0, 1, 1, 0))
KODAK_SKIN = TrickSkin(B_COLOR, "GERMANIUM", "KODAK COATING", (1, 0, 1, 1, 0, 1, 0, 1, 1))


def chip_icon(size=2.2, color=B_COLOR, grid=True):
    body = RoundedRectangle(
        corner_radius=0.18, width=size, height=size,
        fill_color="#171B24", fill_opacity=1, stroke_color=color, stroke_width=5,
    )
    core = RoundedRectangle(
        corner_radius=0.10, width=size * 0.62, height=size * 0.62,
        fill_color=color, fill_opacity=0.14, stroke_color=color, stroke_width=2,
    )
    pins = VGroup()
    for u in (-0.72, -0.24, 0.24, 0.72):
        for a, b in (
            ([u, size / 2, 0], [u, size / 2 + 0.22, 0]),
            ([u, -size / 2, 0], [u, -size / 2 - 0.22, 0]),
            ([size / 2, u, 0], [size / 2 + 0.22, u, 0]),
            ([-size / 2, u, 0], [-size / 2 - 0.22, u, 0]),
        ):
            pins.add(Line(a, b, color=color, stroke_width=4))
    details = VGroup()
    if grid:
        for u in (-0.42, 0, 0.42):
            details.add(Line([-0.62, u, 0], [0.62, u, 0], color=color, stroke_opacity=0.42, stroke_width=2))
            details.add(Line([u, -0.62, 0], [u, 0.62, 0], color=color, stroke_opacity=0.42, stroke_width=2))
    return VGroup(pins, body, core, details)


def camera_icon(width=3.0, color=A_COLOR):
    body = RoundedRectangle(
        corner_radius=0.26, width=width, height=width * 0.68,
        fill_color="#171B24", fill_opacity=1, stroke_color=color, stroke_width=5,
    )
    grip = RoundedRectangle(
        corner_radius=0.12, width=width * 0.34, height=0.32,
        fill_color=color, fill_opacity=0.2, stroke_color=color, stroke_width=3,
    ).next_to(body, UP, buff=-0.02).shift(0.58 * LEFT)
    lens = Circle(radius=width * 0.23, color=color, stroke_width=5).move_to(body)
    glass = Circle(
        radius=width * 0.14, color=LINK_COLOR,
        fill_color=LINK_COLOR, fill_opacity=0.16, stroke_width=3,
    ).move_to(lens)
    glint = Dot(glass.get_center() + 0.08 * UL, radius=0.04, color=INK)
    return VGroup(body, grip, lens, glass, glint)


def circuit_background():
    paths = VGroup()
    starts = [(-3.6, 4.1), (-3.5, 2.7), (-3.4, 1.0), (2.7, 4.0), (2.7, 2.2), (2.7, 0.4)]
    for i, (x, y) in enumerate(starts):
        direction = 1 if x < 0 else -1
        points = [[x, y, 0], [x + 0.65 * direction, y, 0],
                  [x + direction, y - 0.35, 0], [x + 1.5 * direction, y - 0.35, 0]]
        color = B_COLOR if i % 2 else A_COLOR
        path = VMobject(stroke_color=color, stroke_width=2, stroke_opacity=0.23)
        path.set_points_as_corners(points)
        paths.add(path, Dot(points[0], radius=0.035, color=color).set_opacity(0.45))
    return paths


def process_stack(skin):
    base = RoundedRectangle(
        corner_radius=0.1, width=5.5, height=0.70,
        fill_color=METAL, fill_opacity=0.8, stroke_color=INK, stroke_width=2,
    )
    base_text = text(skin.base_label, 19, BG, BOLD).move_to(base)
    blocks = VGroup()
    for i in range(9):
        block = Rectangle(width=0.57, height=0.54, fill_color=skin.coat_color, fill_opacity=0.86, stroke_width=0)
        block.move_to([-2.28 + i * 0.57, 0.62, 0])
        blocks.add(block)
    return VGroup(base, base_text, blocks), blocks


def sun_icon(color=LINK_COLOR):
    core = Circle(radius=0.22, fill_color=color, fill_opacity=1, stroke_width=0)
    rays = VGroup(*[
        Line(0.32 * RIGHT, 0.54 * RIGHT, color=color, stroke_width=4).rotate(k * TAU / 8, about_point=ORIGIN)
        for k in range(8)
    ])
    return VGroup(core, rays)


def drop_icon(color=OIL):
    drop = VMobject(fill_color=color, fill_opacity=1, stroke_color=color, stroke_width=2)
    drop.set_points_smoothly([
        [0, 0.55, 0], [-0.35, 0.05, 0], [-0.28, -0.38, 0],
        [0, -0.52, 0], [0.28, -0.38, 0], [0.35, 0.05, 0], [0, 0.55, 0],
    ])
    return drop


def process_card(label, icon, color):
    box = RoundedRectangle(
        corner_radius=0.23, width=1.72, height=2.08,
        fill_color=color, fill_opacity=0.09, stroke_color=color, stroke_width=3,
    )
    icon.move_to(box.get_center() + 0.28 * UP)
    name = title(label, 24, color).move_to(box.get_center() + 0.64 * DOWN)
    return VGroup(box, icon, name)


class Episode(ShortScene):
    """Final nine-beat infographic, timed entirely from the unchanged script."""

    def trick(self, beat_id, skin, run_time, intro=(), badge=None):
        """The coat-light-wash cross-section. B3 plays it; B6 replays it in B's skin.

        Same geometry and the same phase timing every time, so viewers recognise it.
        `intro` fades in with the first phase; `badge` cards (B6) appear one per step.
        Returns what is left on stage, so the beat can clear it for its own ending.
        """
        stack, coating = process_stack(skin)
        stack.move_to([AXIS, TRICK_STACK_Y, 0])
        tag = pill(skin.coat_label, skin.coat_color).next_to(stack, DOWN, buff=0.25)
        light = sun_icon().move_to([AXIS, TRICK_LIGHT_Y, 0])
        hard = [i for i, on in enumerate(skin.mask) if on]
        rays = VGroup(*[
            Arrow(light.get_bottom(), coating[i].get_top(), buff=0.12, color=LINK_COLOR,
                  stroke_width=3, max_tip_length_to_length_ratio=0.08)
            for i in hard
        ])
        locks = VGroup(*[text("●", 25, LINK_COLOR).move_to(coating[i]) for i in hard])
        oil = VGroup(*[
            drop_icon().scale(0.28).move_to([AXIS + (i - 3) * 0.75, TRICK_OIL_Y + (i % 2) * 0.18, 0])
            for i in range(7)
        ])
        with self.alignment_loop(f"{beat_id} mechanism") as align:
            align.centered(light)
            align.centered(stack)
            align.centered(tag)
            align.centered(oil)
            align.inside_safe(VGroup(light, stack, tag, oil))
        t = [run_time * share for share in TRICK_PHASES]
        cards = list(badge) if badge is not None else []

        def step(k):
            return [FadeIn(cards[k], scale=0.8)] if k < len(cards) else []

        self.play(*[FadeIn(m) for m in intro], FadeIn(stack, shift=0.3 * UP), FadeIn(tag),
                  GrowFromCenter(light), *step(0), run_time=t[0])
        self.sfx("spark.wav", -14)
        self.play(LaggedStart(*[GrowArrow(r) for r in rays], lag_ratio=0.07), *step(1), run_time=t[1])
        self.play(LaggedStart(*[FadeIn(m, scale=1.8) for m in locks], lag_ratio=0.06), run_time=t[2])
        self.sfx("wash.wav", -18)
        self.play(LaggedStart(*[FadeIn(d, shift=0.25 * DOWN) for d in oil], lag_ratio=0.07), *step(2), run_time=t[3])
        soft = [coating[i] for i, on in enumerate(skin.mask) if not on]
        self.play(*[m.animate.shift(0.45 * DOWN).set_opacity(0) for m in soft],
                  *[d.animate.shift(DOWN).set_opacity(0) for d in oil], run_time=t[4])
        return VGroup(light, rays, locks, stack, tag)

    def construct(self):
        # B1: the claim, the phone and its chip are on screen from frame 0 (the cover),
        # then the circuit traces in and a camera aperture snaps over the chip.
        with self.beat("B1") as b:
            self.sfx("power-up.wav", -14)
            bg = circuit_background()
            phone = RoundedRectangle(
                corner_radius=0.42, width=4.15, height=6.3,
                fill_color="#131722", fill_opacity=1, stroke_color=FAINT, stroke_width=5,
            )
            speaker = RoundedRectangle(
                corner_radius=0.06, width=0.75, height=0.10,
                fill_color=FAINT, fill_opacity=1, stroke_width=0,
            ).next_to(phone.get_top(), DOWN, buff=0.25)
            chip = chip_icon(2.35).move_to(phone.get_center() + 0.35 * UP)
            pulse = Circle(radius=1.35, color=B_COLOR, stroke_width=5).move_to(chip).set_opacity(0.7)
            device = VGroup(phone, speaker, chip, pulse)
            hook = VGroup(title("CAMERA", 48, A_COLOR), title("×", 40, LINK_COLOR), title("CHIP", 48, B_COLOR))
            hook.arrange(RIGHT, buff=0.20).move_to([AXIS, 4.55, 0])
            device.next_to(hook, DOWN, buff=0.30).set_x(AXIS)
            with self.alignment_loop("B1 opening composition") as align:
                align.even_column([hook, device], gap=0.30)
                align.inside_safe(VGroup(hook, device), padding=0.08)
            self.add(phone, speaker, chip, hook)
            self.play(
                LaggedStart(*[Create(p) for p in bg], lag_ratio=0.05),
                FadeIn(pulse, scale=0.5), chip.animate.scale(1.08), run_time=b.duration * 0.28,
            )
            self.play(pulse.animate.scale(1.7).set_opacity(0), chip.animate.scale(1 / 1.08), run_time=b.duration * 0.18)
            self.play(hook.animate.scale(1.08), run_time=b.duration * 0.10)
            self.play(hook.animate.scale(1 / 1.08), run_time=b.duration * 0.10)
            self.sfx("shutter.wav", -9)
            aperture = VGroup(*[
                Arc(radius=1.52 - i * 0.12, start_angle=i * PI / 3, angle=PI * 0.82,
                    color=A_COLOR, stroke_width=5) for i in range(6)
            ]).move_to(chip)
            flash = Circle(radius=0.1, fill_color=INK, fill_opacity=1, stroke_width=0).move_to(chip)
            self.play(Create(aperture), Rotate(aperture, PI / 2), run_time=b.duration * 0.16)
            self.play(FadeIn(flash, scale=0.1), Flash(chip.get_center(), color=INK, flash_radius=2.4), run_time=b.duration * 0.10)
            self.play(FadeOut(flash), FadeOut(aperture), run_time=b.duration * 0.05)
            self.hold(b)
        self.clear_stage(0.22)

        # B2: a pewter plate is coated, then exposed in a camera at a window.
        with self.beat("B2") as b:
            header = beat_header(2, "The first photograph", A_COLOR)
            date = date_badge("c. 1827", A_COLOR).move_to([-1.95, 3.82, 0])
            plate = RoundedRectangle(
                corner_radius=0.14, width=4.8, height=2.9,
                fill_color=METAL, fill_opacity=0.42, stroke_color=INK, stroke_width=3,
            ).move_to([-0.4, 1.1, 0])
            coating = Rectangle(width=0.08, height=2.65, fill_color=BROWN, fill_opacity=0.92, stroke_width=0)
            coating.move_to(plate).align_to(plate, LEFT).shift(0.13 * RIGHT)
            coat_label = text("BITUMEN OF JUDEA", 20, BROWN, BOLD).next_to(plate, DOWN, buff=0.20)
            with self.alignment_loop("B2 coated plate") as align:
                align.centered(VGroup(plate, coating, coat_label))
                align.inside_safe(VGroup(plate, coating, coat_label))
            self.play(FadeIn(header, shift=0.15 * DOWN), FadeIn(date, scale=0.8), DrawBorderThenFill(plate), run_time=b.duration * 0.18)
            self.sfx("whoosh.wav", -17)
            self.play(coating.animate.stretch_to_fit_width(4.55).align_to(plate, LEFT).shift(0.13 * RIGHT),
                      FadeIn(coat_label), run_time=b.duration * 0.18)
            camera = camera_icon(3.6).move_to([-1.55, 1.0, 0])
            window = VGroup(
                Rectangle(width=2.2, height=3.3, color=A_COLOR, stroke_width=4),
                Line(1.65 * UP, 1.65 * DOWN, color=A_COLOR, stroke_width=3),
                Line(1.1 * LEFT, 1.1 * RIGHT, color=A_COLOR, stroke_width=3),
            ).move_to([1.45, 1.35, 0])
            roofs = VGroup(
                Polygon([-2.9, 0.3, 0], [-2.0, 1.1, 0], [-1.1, 0.3, 0],
                        color=MUTED, fill_color=MUTED, fill_opacity=0.18),
                Polygon([0.0, 0.3, 0], [0.8, 1.0, 0], [1.7, 0.3, 0],
                        color=MUTED, fill_color=MUTED, fill_opacity=0.18),
            ).scale_to_fit_width(1.8).move_to(window.get_center() + 0.85 * DOWN)
            camera_window = VGroup(camera, window, roofs)
            with self.alignment_loop("B2 camera and window") as align:
                align.centered(camera_window)
                align.inside_safe(camera_window)
            self.play(FadeOut(plate), FadeOut(coating), FadeOut(coat_label), FadeIn(camera), FadeIn(window), run_time=b.duration * 0.18)
            rays = VGroup(*[
                Line(roofs.get_center() + (k - 1) * 0.35 * UP, camera[3].get_center(),
                     color=LINK_COLOR, stroke_width=3, stroke_opacity=0.65) for k in range(3)
            ])
            inverted = roofs.copy().rotate(PI).scale(0.45).move_to(camera[3])
            self.play(FadeIn(roofs, shift=0.2 * UP), LaggedStart(*[Create(r) for r in rays], lag_ratio=0.1), run_time=b.duration * 0.18)
            self.play(TransformFromCopy(roofs, inverted), Flash(camera[3].get_center(), color=A_COLOR, flash_radius=1.0), run_time=b.duration * 0.14)
            self.hold(b)
        self.clear_stage(0.22)

        # B3: the coat-light-wash mechanism as a cross-section. B6 replays it exactly.
        with self.beat("B3") as b:
            header = beat_header(3, "The trick", LINK_COLOR)
            self.trick_time = min(TRICK_MAX_TIME, 0.74 * b.duration)
            mechanism = self.trick("B3", ASPHALT_SKIN, self.trick_time, intro=[header])
            picture = VGroup(
                Polygon([-2.3, 0, 0], [-1.45, 0.95, 0], [-0.65, 0, 0], color=INK, fill_color=INK, fill_opacity=0.58),
                Polygon([-0.6, 0, 0], [0.2, 0.65, 0], [1.0, 0, 0], color=INK, fill_color=INK, fill_opacity=0.42),
                Circle(radius=0.22, color=LINK_COLOR, fill_color=LINK_COLOR, fill_opacity=0.8).move_to([1.7, 0.85, 0]),
            ).move_to([AXIS, 0.55, 0])
            frame = RoundedRectangle(corner_radius=0.15, width=5.4, height=2.65, color=INK, stroke_width=3).move_to(picture)
            with self.alignment_loop("B3 picture") as align:
                align.centered(VGroup(frame, picture))
                align.inside_safe(VGroup(frame, picture))
            self.play(FadeOut(mechanism), FadeIn(frame), FadeIn(picture), run_time=max(0.3, min(0.8, b.remaining - 0.2)))
            self.hold(b)
        self.clear_stage(0.22)

        # B4: the three steps become a compact mnemonic.
        with self.beat("B4") as b:
            header = beat_header(4, "Remember this", LINK_COLOR)
            coat_icon = VGroup(
                Rectangle(width=0.95, height=0.18, fill_color=METAL, fill_opacity=0.8, stroke_width=0),
                Rectangle(width=0.95, height=0.16, fill_color=BROWN, fill_opacity=1, stroke_width=0).shift(0.18 * UP),
            )
            wash_icon = VGroup(drop_icon().scale(0.55), Arc(radius=0.58, start_angle=PI * 1.10,
                               angle=PI * 0.80, color=LINK_COLOR, stroke_width=4).shift(0.38 * DOWN))
            cards = VGroup(
                process_card("COAT", coat_icon, BROWN),
                process_card("LIGHT", sun_icon().scale(0.72), LINK_COLOR),
                process_card("WASH", wash_icon, OIL),
            ).arrange(RIGHT, buff=0.30).move_to([-0.4, 1.3, 0])
            with self.alignment_loop("B4 process cards") as align:
                align.even_row(cards, y=1.3, gap=0.30)
                align.inside_safe(cards)
            arrows = VGroup(*[
                Arrow(cards[i].get_right(), cards[i + 1].get_left(), buff=0.10,
                      color=LINK_COLOR, stroke_width=3, max_tip_length_to_length_ratio=0.2) for i in range(2)
            ])
            self.play(FadeIn(header), run_time=b.duration * 0.12)
            self.sfx("ticks.wav", -15)
            self.play(LaggedStart(*[FadeIn(c, shift=0.45 * UP, scale=0.8) for c in cards], lag_ratio=0.25), run_time=b.duration * 0.48)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2), run_time=b.duration * 0.18)
            self.play(cards.animate.scale(0.68).move_to([-0.4, 2.5, 0]), FadeOut(arrows), run_time=b.duration * 0.16)
            self.hold(b)
        self.clear_stage(0.22)

        # B5: the microscope visibly flips and shrinks a pattern.
        with self.beat("B5") as b:
            header = beat_header(5, "Tiny transistors", B_COLOR)
            date = date_badge("1957", B_COLOR).move_to([-2.25, 3.85, 0])
            target = RoundedRectangle(corner_radius=0.18, width=1.15, height=1.15,
                                      color=B_COLOR, stroke_width=4).move_to([1.7, 3.0, 0])
            too_big = chip_icon(1.55, B_COLOR, False).move_to(target).scale(1.18)
            cross = VGroup(Line(0.38 * UL, 0.38 * DR, color="#FF5C5C", stroke_width=8),
                           Line(0.38 * UR, 0.38 * DL, color="#FF5C5C", stroke_width=8)).move_to(target)
            microscope = VGroup(
                Arc(radius=0.8, start_angle=-PI / 2, angle=PI, color=INK, stroke_width=8),
                Line([0, 0.78, 0], [0.55, 1.62, 0], color=INK, stroke_width=11),
                RoundedRectangle(corner_radius=0.08, width=0.65, height=1.15,
                                 color=A_COLOR, fill_color=A_COLOR, fill_opacity=0.14, stroke_width=5).rotate(-0.58).shift([0.82, 1.48, 0]),
                Line([-1.0, -0.82, 0], [1.25, -0.82, 0], color=INK, stroke_width=9),
            ).scale(0.82).move_to([AXIS, 1.05, 0])
            with self.alignment_loop("B5 microscope") as align:
                align.centered(microscope)
                align.inside_safe(microscope)
            self.play(FadeIn(header), FadeIn(date), DrawBorderThenFill(target), GrowFromCenter(too_big), run_time=b.duration * 0.16)
            self.play(Create(cross), too_big.animate.set_color("#FF5C5C"), run_time=b.duration * 0.10)
            self.play(FadeOut(target), FadeOut(cross), FadeOut(too_big), Create(microscope), run_time=b.duration * 0.18)
            flip = text("TURN IT UPSIDE DOWN", 24, LINK_COLOR, BOLD).next_to(microscope, DOWN, buff=0.38)
            self.sfx("whoosh.wav", -14)
            self.play(Rotate(microscope, PI), FadeIn(flip, shift=0.2 * UP), run_time=b.duration * 0.18)
            # Pattern above, upside-down microscope in the middle, wafer below: one even column.
            pattern = VGroup(*[
                Rectangle(width=0.52, height=0.52, color=B_COLOR, fill_color=B_COLOR, fill_opacity=0.14, stroke_width=2)
                for _ in range(9)
            ]).arrange_in_grid(3, 3, buff=0.07)
            pattern.next_to(microscope, UP, buff=0.35).set_x(AXIS)
            wafer = Circle(radius=0.75, color=B_COLOR, fill_color=B_COLOR, fill_opacity=0.08, stroke_width=4)
            wafer.next_to(microscope, DOWN, buff=0.35).set_x(AXIS)
            with self.alignment_loop("B5 projected pattern") as align:
                align.even_column([pattern, microscope, wafer], gap=0.35)
                align.inside_safe(VGroup(pattern, microscope, wafer))
            rays = VGroup(Line(pattern.get_corner(DL), wafer.get_center(), color=LINK_COLOR, stroke_width=3),
                          Line(pattern.get_corner(DR), wafer.get_center(), color=LINK_COLOR, stroke_width=3))
            tiny = pattern.copy().scale(0.22).move_to(wafer)
            self.play(FadeOut(flip), FadeOut(date), FadeIn(pattern), FadeIn(wafer),
                      LaggedStart(*[Create(r) for r in rays], lag_ratio=0.2), run_time=b.duration * 0.16)
            self.play(TransformFromCopy(pattern, tiny), Circumscribe(tiny, color=B_COLOR), run_time=b.duration * 0.14)
            self.hold(b)
        self.clear_stage(0.22)

        # B6: the B3 mechanism again, same geometry and timing, in chip colors. The B4 badge
        # lights up one step at a time; then the technical name splits into its roots.
        with self.beat("B6") as b:
            header = beat_header(6, "Same trick, new world", B_COLOR)
            badge = VGroup(
                process_card("COAT", Rectangle(width=0.8, height=0.22, fill_color=B_COLOR, fill_opacity=1, stroke_width=0), B_COLOR),
                process_card("LIGHT", sun_icon().scale(0.62), LINK_COLOR),
                process_card("WASH", drop_icon().scale(0.46), OIL),
            ).arrange(RIGHT, buff=0.25).scale(0.55).move_to([AXIS, -1.75, 0])
            with self.alignment_loop("B6 step badge") as align:
                align.even_row(badge, y=-1.75, gap=0.25 * 0.55)
                align.inside_safe(badge)
            mechanism = self.trick("B6", KODAK_SKIN, self.trick_time, intro=[header], badge=badge)
            word_y = TRICK_STACK_Y + 0.25
            parts = VGroup(title("PHOTO", 39, LINK_COLOR), title("LITHO", 39, LINK_COLOR),
                           title("GRAPHY", 39, LINK_COLOR)).arrange(RIGHT, buff=0).move_to([AXIS, word_y, 0])
            roots = parts.copy().arrange(RIGHT, buff=0.32).move_to([AXIS, word_y, 0])
            with self.alignment_loop("B6 word roots") as align:
                align.centered(parts)
                align.even_row(roots, y=word_y, gap=0.32)
            meanings = VGroup(*[
                text(word, 21, MUTED, BOLD).next_to(root, DOWN, buff=0.16)
                for word, root in zip(("LIGHT", "STONE", "WRITING"), roots)
            ])
            with self.alignment_loop("B6 root meanings") as align:
                align.inside_safe(VGroup(roots, meanings))
            rest = b.remaining
            self.play(FadeOut(mechanism), FadeIn(parts, scale=1.08), run_time=max(0.25, 0.18 * rest))
            self.play(Transform(parts, roots), run_time=max(0.25, 0.18 * rest))
            self.play(LaggedStart(*[FadeIn(m, shift=0.15 * UP) for m in meanings], lag_ratio=0.3),
                      run_time=max(0.3, 0.32 * rest))
            self.hold(b)
        self.clear_stage(0.22)

        # B7: reverse the arrow, then fill the 100-pixel CCD eye.
        with self.beat("B7") as b:
            header = beat_header(7, "Chips pay cameras back", A_COLOR)
            chip = chip_icon(1.45, B_COLOR).move_to([-2.45, 3.2, 0])
            cam = camera_icon(1.95, A_COLOR).move_to([1.65, 3.2, 0])
            with self.alignment_loop("B7 return pair") as align:
                align.mirror_pair(chip, cam, y=3.2, min_gap=0.35)
                align.inside_safe(VGroup(chip, cam))
            arrow = CurvedArrow(chip.get_right(), cam.get_left(), angle=-0.4, color=LINK_COLOR, stroke_width=5)
            arrow_label = text("RETURN", 20, LINK_COLOR, BOLD).next_to(arrow, UP, buff=0.08)
            self.play(FadeIn(header), GrowFromCenter(chip), GrowFromCenter(cam), run_time=b.duration * 0.14)
            self.sfx("whoosh.wav", -15)
            self.play(Create(arrow), FadeIn(arrow_label), run_time=b.duration * 0.14)
            year = date_badge("1975", A_COLOR).move_to([-2.35, 3.45, 0])
            self.play(FadeOut(chip), FadeOut(cam), FadeOut(arrow), FadeOut(arrow_label), FadeIn(year), run_time=b.duration * 0.11)
            old_cam = camera_icon(4.6, A_COLOR).move_to([-0.4, 1.0, 0])
            old_cam[0].stretch(1.18, 1)
            tape = RoundedRectangle(corner_radius=0.06, width=0.9, height=0.48,
                                    color=MUTED, fill_color=MUTED, fill_opacity=0.2, stroke_width=2)
            tape.move_to(old_cam[0].get_corner(DR) + 0.5 * UL)
            with self.alignment_loop("B7 portable camera") as align:
                align.centered(old_cam)
                align.inside_safe(VGroup(old_cam, tape))
            self.play(DrawBorderThenFill(old_cam), FadeIn(tape), run_time=b.duration * 0.16)
            sensor_box = RoundedRectangle(corner_radius=0.10, width=2.4, height=2.4,
                                          fill_color="#141A22", fill_opacity=1,
                                          stroke_color=B_COLOR, stroke_width=4).move_to(old_cam[3])
            pixels = VGroup()
            for row in range(10):
                for col in range(10):
                    pixel = Square(side_length=0.17, stroke_width=1, stroke_color=FAINT,
                                   fill_color=A_COLOR, fill_opacity=0.10)
                    pixel.move_to(sensor_box.get_corner(UL) + [0.30 + col * 0.20, -0.30 - row * 0.20, 0])
                    pixels.add(pixel)
            with self.alignment_loop("B7 sensor grid") as align:
                align.centered(sensor_box)
                align.centered(pixels)
                align.inside_safe(VGroup(sensor_box, pixels))
            self.play(FadeOut(old_cam[3:]), FadeIn(sensor_box, scale=0.35), FadeIn(pixels), run_time=b.duration * 0.12)
            self.sfx("pixels.wav", -18)
            fills = [p.animate.set_fill(A_COLOR if i % 3 else B_COLOR, opacity=0.78) for i, p in enumerate(pixels)]
            self.play(LaggedStart(*fills, lag_ratio=0.012), run_time=b.duration * 0.17)
            eye = VGroup(Circle(radius=1.45, color=A_COLOR, stroke_width=5),
                         Circle(radius=0.62, color=B_COLOR, fill_color=B_COLOR, fill_opacity=0.22, stroke_width=4)).move_to(sensor_box)
            self.play(FadeIn(eye), Flash(sensor_box.get_center(), color=INK, flash_radius=1.7), run_time=b.duration * 0.09)
            self.hold(b)
        self.clear_stage(0.22)

        # B8: diagram a lithography machine as a building-sized camera.
        with self.beat("B8") as b:
            header = beat_header(8, "A giant camera", B_COLOR)
            machine = RoundedRectangle(corner_radius=0.30, width=6.0, height=5.35,
                                       fill_color="#151923", fill_opacity=1,
                                       stroke_color=FAINT, stroke_width=4).move_to([-0.4, 1.25, 0])
            source = sun_icon().scale(0.55).move_to([-0.4, 3.25, 0])
            mask = VGroup(*[Square(side_length=0.22, fill_color=INK, fill_opacity=0.75, stroke_width=0) for _ in range(16)])
            mask.arrange_in_grid(4, 4, buff=0.07).move_to([-0.4, 2.2, 0])
            lens1 = Ellipse(width=3.25, height=0.55, color=A_COLOR, fill_color=A_COLOR, fill_opacity=0.10, stroke_width=4).move_to([-0.4, 1.10, 0])
            lens2 = Ellipse(width=2.35, height=0.45, color=A_COLOR, fill_color=A_COLOR, fill_opacity=0.10, stroke_width=4).move_to([-0.4, 0.32, 0])
            wafer = Ellipse(width=3.0, height=0.62, color=B_COLOR, fill_color=B_COLOR, fill_opacity=0.14, stroke_width=4).move_to([-0.4, -0.72, 0])
            labels = VGroup(
                text("LIGHT", 18, LINK_COLOR, BOLD).next_to(source, LEFT, buff=0.35),
                text("MASK", 18, MUTED, BOLD).next_to(mask, RIGHT, buff=0.35),
                text("LENS STACK", 18, A_COLOR, BOLD).next_to(lens2, RIGHT, buff=0.35),
                text("WAFER", 18, B_COLOR, BOLD).next_to(wafer, LEFT, buff=0.35),
            )
            with self.alignment_loop("B8 lithography stack") as align:
                for item in (machine, source, mask, lens1, lens2, wafer):
                    align.centered(item)
                align.inside_safe(machine)
            self.play(FadeIn(header), DrawBorderThenFill(machine), run_time=b.duration * 0.16)
            self.play(LaggedStart(FadeIn(source), FadeIn(mask), FadeIn(lens1), FadeIn(lens2), FadeIn(wafer), lag_ratio=0.14), run_time=b.duration * 0.20)
            beams = VGroup(
                Polygon(source.get_bottom() + 0.18 * LEFT, lens1.get_left(), lens2.get_left(),
                        wafer.get_center() + 0.35 * LEFT, color=LINK_COLOR,
                        fill_color=LINK_COLOR, fill_opacity=0.12, stroke_width=2),
                Polygon(source.get_bottom() + 0.18 * RIGHT, lens1.get_right(), lens2.get_right(),
                        wafer.get_center() + 0.35 * RIGHT, color=LINK_COLOR,
                        fill_color=LINK_COLOR, fill_opacity=0.12, stroke_width=2),
            )
            self.sfx("power-up.wav", -17)
            self.play(LaggedStart(*[Create(beam) for beam in beams], lag_ratio=0.12), FadeIn(labels), run_time=b.duration * 0.20)
            pattern = mask.copy().scale(0.34).move_to(wafer)
            self.play(TransformFromCopy(mask, pattern), Flash(wafer.get_center(), color=B_COLOR, flash_radius=1.25), run_time=b.duration * 0.14)
            brands = VGroup(title("NIKON", 27, A_COLOR), title("CANON", 27, A_COLOR), title("ZEISS", 27, A_COLOR))
            brands.arrange(RIGHT, buff=0.38).move_to([-0.4, -1.72, 0])
            with self.alignment_loop("B8 maker labels") as align:
                align.even_row(brands, y=-1.72, gap=0.38)
                align.inside_safe(brands)
            self.play(LaggedStart(*[FadeIn(x, shift=0.2 * UP) for x in brands], lag_ratio=0.25), run_time=b.duration * 0.16)
            self.hold(b)
        self.clear_stage(0.22)

        # B9: the Connection Map. Episode 001 seeds it with its first link: both directions
        # resolve into one blue-to-orange edge. Camera left and chip right echo the B1 title,
        # so the last pose loops back to the opening.
        with self.beat("B9") as b:
            header = beat_header(9, "Connection map", LINK_COLOR)
            cam_mark = camera_icon(2.15, A_COLOR).move_to([AXIS - 1.9, 1.25, 0])
            chip_mark = chip_icon(1.72, B_COLOR).move_to([AXIS + 1.9, 1.25, 0])
            with self.alignment_loop("B9 map nodes") as align:
                align.mirror_pair(cam_mark, chip_mark, y=1.25, min_gap=1.6)
                align.inside_safe(VGroup(cam_mark, chip_mark))
            label_y = min(cam_mark.get_bottom()[1], chip_mark.get_bottom()[1]) - 0.42
            cam_label = title("CAMERA", 30, A_COLOR).move_to([cam_mark.get_x(), label_y, 0])
            chip_label = title("CHIP", 30, B_COLOR).move_to([chip_mark.get_x(), label_y, 0])
            tagline = VGroup(title("SAME TRICK", 44, LINK_COLOR), title("TWO WORLDS", 44, INK))
            tagline.arrange(DOWN, buff=0.10).move_to([AXIS, 3.45, 0])
            with self.alignment_loop("B9 labels and tagline") as align:
                align.mirror_pair(cam_label, chip_label, y=label_y)
                align.centered(tagline)
                align.inside_safe(VGroup(tagline, cam_label, chip_label))
            camera = VGroup(cam_mark, cam_label)
            chip = VGroup(chip_mark, chip_label)
            forward = Arrow(cam_mark.get_right() + 0.22 * UP, chip_mark.get_left() + 0.22 * UP,
                            buff=0.15, color=A_COLOR, stroke_width=5)
            backward = Arrow(chip_mark.get_left() + 0.22 * DOWN, cam_mark.get_right() + 0.22 * DOWN,
                             buff=0.15, color=B_COLOR, stroke_width=5)
            link = Line(cam_mark.get_right(), chip_mark.get_left(), stroke_width=8).set_color([A_COLOR, LINK_COLOR, B_COLOR])
            link.set_sheen_direction(RIGHT)  # Manim's default runs gradients from the right end; keep blue at the camera
            self.play(FadeIn(header), GrowFromCenter(camera), GrowFromCenter(chip), run_time=b.duration * 0.18)
            self.play(GrowArrow(forward), run_time=b.duration * 0.16)
            self.play(GrowArrow(backward), run_time=b.duration * 0.16)
            self.sfx("spark.wav", -12)
            self.play(FadeOut(forward), FadeOut(backward), Create(link),
                      Flash(link.get_center(), color=LINK_COLOR, flash_radius=1.0), run_time=b.duration * 0.16)
            self.play(FadeIn(tagline, shift=0.28 * UP), run_time=b.duration * 0.20)
            self.play(VGroup(camera, chip, link).animate.scale(0.96), run_time=b.duration * 0.10)
            self.hold(b)

        self.wait(0.35)
