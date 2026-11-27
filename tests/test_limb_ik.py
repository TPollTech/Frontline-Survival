"""Analytic IK math only; not Godot animation or visual validation."""
import math
import random
import unittest
from tools.asset_pipeline.parametric.limb_ik import solve_limb


class LimbIKTests(unittest.TestCase):
    def assert_lengths(self, result, root, upper, lower):
        self.assertAlmostEqual(math.dist(root, result.elbow), upper, places=9)
        self.assertAlmostEqual(math.dist(result.elbow, result.wrist), lower, places=9)

    def test_reachable_target(self):
        s = solve_limb((0,0,0), (.5,0,0), (0,1,0), .4, .3)
        self.assert_lengths(s, (0,0,0), .4, .3)
        self.assertFalse(s.clamped)
        self.assertAlmostEqual(s.target_error, 0.)
        self.assertGreater(s.elbow[1], 0.)

    def test_limits_and_unreachable_targets(self):
        for target, expected in [((2,0,0), .2), ((.01,0,0), 2.2)]:
            s = solve_limb((0,0,0), target, (0,1,0), .4, .3, min_flexion=.2, max_flexion=2.2)
            self.assert_lengths(s, (0,0,0), .4, .3)
            self.assertTrue(s.clamped)
            self.assertAlmostEqual(s.flexion, expected)
            self.assertGreater(s.target_error, 0.)

    def test_pole_and_mirror(self):
        a,b = [solve_limb((0,0,0), (.5,0,0), (0,y,0), .4,.3) for y in (1,-1)]
        self.assertEqual(a.wrist,b.wrist)
        self.assertEqual(a.elbow,(b.elbow[0],-b.elbow[1],b.elbow[2]))

    def test_explicit_singular_fallbacks(self):
        s = solve_limb((0,0,0), (0,0,0), (1,0,0), .4,.3,
                       fallback_axis=(1,0,0), previous_bend=(0,1,0))
        self.assert_lengths(s, (0,0,0), .4,.3)
        self.assertTrue(s.clamped)
        self.assertEqual(s.bend_direction, (0.,1.,0.))
        with self.assertRaises(ValueError):
            solve_limb((0,0,0), (0,0,0), (0,1,0), .4,.3)
        with self.assertRaises(ValueError):
            solve_limb((0,0,0), (.5,0,0), (1,0,0), .4,.3)

    def test_transition_samples(self):
        last = None
        for i in range(101):
            t = i/100
            s = solve_limb((0,0,0), (.48+.12*t,.07*t,.10*t), (0,1,0), .4,.3)
            self.assert_lengths(s, (0,0,0), .4,.3)
            if last is not None:
                self.assertLess(math.dist(last.elbow,s.elbow), .01)
            last = s

    def test_random_invariants(self):
        rng = random.Random(207)
        for _ in range(500):
            root,target,pole = [tuple(rng.uniform(-1,1) for _ in range(3)) for _ in range(3)]
            a,b = rng.uniform(.15,.55),rng.uniform(.15,.55)
            s = solve_limb(root,target,pole,a,b)
            self.assert_lengths(s, root,a,b)
            self.assertGreaterEqual(s.flexion,.02-1e-9)
            self.assertLessEqual(s.flexion,2.5+1e-9)
            self.assertAlmostEqual(math.dist(target,s.wrist),s.target_error)

    def test_invalid_inputs(self):
        for a,b in [(0,.3),(.4,-1),(math.inf,.3)]:
            with self.assertRaises(ValueError):
                solve_limb((0,0,0),(.5,0,0),(0,1,0),a,b)
        with self.assertRaises(ValueError):
            solve_limb((0,0,0),(.5,0,0),(0,1,0),.4,.3,max_flexion=math.pi)
        with self.assertRaises(ValueError):
            solve_limb((0,0,0),(math.nan,0,0),(0,1,0),.4,.3)
