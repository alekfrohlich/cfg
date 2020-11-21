"""ContextFreeGrammar unit tests."""
import filecmp
import unittest

from context_free.grammar import ContextFreeGrammar, OrderedSet

from util import dot_cfg

class TestContextFreeGrammar(unittest.TestCase):

    def test_constructor(self):
        cfg = ContextFreeGrammar(
            OrderedSet(["S", "B", "❬B'❭", "A", "❬A'❭"]),
            OrderedSet(["a", "b", "c", "d"]),
            {
                "S":    OrderedSet(["Bd", "&"]),
                "B":    OrderedSet(["Ab❬B'❭"]),
                "❬B'❭": OrderedSet(["c❬B'❭", "&"]),
                "A":    OrderedSet(["a❬A'❭", "❬A'❭"]),
                "❬A'❭": OrderedSet(["b❬B'❭da❬A'❭", "&"]),
            },
            "S")

        # Test post-conditions: type and values
        self.assertEqual(cfg.rules["S"]   , OrderedSet([("B", "d"), ("&",)]))
        self.assertEqual(cfg.rules["B"]   , OrderedSet([("A", "b", "❬B'❭")]))
        self.assertEqual(cfg.rules["❬B'❭"], OrderedSet([("c", "❬B'❭"), ("&",)]))
        self.assertEqual(cfg.rules["A"]   , OrderedSet([("a", "❬A'❭"), ("❬A'❭",)]))
        self.assertEqual(cfg.rules["❬A'❭"], OrderedSet([("b", "❬B'❭", "d", "a", "❬A'❭"), ("&",)]))

        dot_cfg.write_grammar(cfg, "test.cfg")
        test_path = dot_cfg.os.path.join(dot_cfg.CFGS_DIR, "test.cfg")
        ref_path = dot_cfg.os.path.join(dot_cfg.CFGS_DIR, "test_constructor.cfg")

        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg2 = dot_cfg.read_grammar("test.cfg")
        self.assertEqual(cfg2.rules["S"]   , OrderedSet([("B", "d"), ("&",)]))
        self.assertEqual(cfg2.rules["B"]   , OrderedSet([("A", "b", "❬B'❭")]))
        self.assertEqual(cfg2.rules["❬B'❭"], OrderedSet([("c", "❬B'❭"), ("&",)]))
        self.assertEqual(cfg2.rules["A"]   , OrderedSet([("a", "❬A'❭"), ("❬A'❭",)]))
        self.assertEqual(cfg2.rules["❬A'❭"], OrderedSet([("b", "❬B'❭", "d", "a", "❬A'❭"), ("&",)]))

        print(cfg)
        print(cfg2)

    def test_rlr(self):

        cfg = dot_cfg.read_grammar("test_rlr_1.cfg")
        print(cfg)
        cfg.remove_left_recursion()
        print(cfg)

        cfg = dot_cfg.read_grammar("test_rlr_2.cfg")
        print(cfg)
        cfg.remove_left_recursion()
        print(cfg)
