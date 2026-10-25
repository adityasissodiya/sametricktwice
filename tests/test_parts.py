"""Regression tests for recurring kit parts and the Connection Map layout."""

from __future__ import annotations

import unittest

try:
    import manim  # noqa: F401
except ImportError:  # e.g. the CI runner, which has no render stack
    raise unittest.SkipTest("needs the render stack (manim)")

import numpy as np

from kit.parts import pill
from kit.short import map_layout


class PartsTests(unittest.TestCase):
    def test_pill_box_always_contains_its_label(self):
        for words in ("ASPHALT", "KODAK COATING", "A MUCH LONGER MATERIAL LABEL"):
            box, label = pill(words, "#FF9F45")
            self.assertGreater(box.width, label.width + 0.3, words)
            self.assertGreater(box.height, label.height, words)
            self.assertAlmostEqual(box.get_center()[0], label.get_center()[0])


PAIRS = [("Camera", "Chip"), ("Air traffic", "Touchscreen"), ("Film", "Explosives"),
         ("Dye", "Medicine"), ("Radar", "Microwave"), ("Beer", "Statistics")]


def _crosses(p1, p2, q1, q2) -> bool:
    """True if segments p1-p2 and q1-q2 properly intersect (2D)."""
    def side(a, b, c):
        return np.sign((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
    return side(p1, p2, q1) * side(p1, p2, q2) < 0 and side(q1, q2, p1) * side(q1, q2, p2) < 0


class ConnectionMapLayoutTests(unittest.TestCase):
    def test_first_pair_is_mirrored_on_one_baseline(self):
        layout = map_layout(PAIRS[:1])
        self.assertAlmostEqual(layout["Camera"][1], layout["Chip"][1])
        self.assertAlmostEqual(layout["Camera"][0], -layout["Chip"][0])
        self.assertLess(layout["Camera"][0], layout["Chip"][0])

    def test_existing_nodes_never_move_when_the_map_grows(self):
        first = map_layout(PAIRS[:1])
        grown = map_layout(PAIRS)
        for name, position in first.items():
            np.testing.assert_allclose(grown[name], position)
        points = np.array(list(grown.values()))
        distances = np.linalg.norm(points[:, None] - points[None, :], axis=-1)
        self.assertGreater(distances[np.triu_indices(len(points), 1)].min(), 0.5)

    def test_episode_links_never_cross(self):
        layout = map_layout(PAIRS)
        edges = [(layout[a], layout[b]) for a, b in PAIRS]
        for i in range(len(edges)):
            for j in range(i + 1, len(edges)):
                self.assertFalse(_crosses(*edges[i], *edges[j]), f"{PAIRS[i]} crosses {PAIRS[j]}")


if __name__ == "__main__":
    unittest.main()
