"""ContextFreeGrammar unit tests."""
import os
import filecmp
import unittest

from context_free.grammar import CFGS_DIR, ContextFreeGrammar, OrderedSet

class TestContextFreeGrammar(unittest.TestCase):

    def test_constructor(self):
        cfg = ContextFreeGrammar("test_constructor.cfg")

        # Test post-conditions: 1
        self.assertEqual(cfg.rules["S"]   , OrderedSet([("B", "d"), ("&",)]))
        self.assertEqual(cfg.rules["B"]   , OrderedSet([("A", "b", "❬B'❭")]))
        self.assertEqual(cfg.rules["❬B'❭"], OrderedSet([("c", "❬B'❭"), ("&",)]))
        self.assertEqual(cfg.rules["A"]   , OrderedSet([("a", "❬A'❭"), ("❬A'❭",)]))
        self.assertEqual(cfg.rules["❬A'❭"], OrderedSet([("b", "❬B'❭", "d", "a", "❬A'❭"), ("&",)]))

        cfg.save_to_file("test_write.cfg")
        test_path = os.path.join(CFGS_DIR, "test_write.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_constructor.cfg")

        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg2 = ContextFreeGrammar("test_write.cfg")
        self.assertEqual(cfg2.rules["S"]   , OrderedSet([("B", "d"), ("&",)]))
        self.assertEqual(cfg2.rules["B"]   , OrderedSet([("A", "b", "❬B'❭")]))
        self.assertEqual(cfg2.rules["❬B'❭"], OrderedSet([("c", "❬B'❭"), ("&",)]))
        self.assertEqual(cfg2.rules["A"]   , OrderedSet([("a", "❬A'❭"), ("❬A'❭",)]))
        self.assertEqual(cfg2.rules["❬A'❭"], OrderedSet([("b", "❬B'❭", "d", "a", "❬A'❭"), ("&",)]))

        print(cfg)
        print(cfg2)

    def test_cfg_grammar_spec(self):
        """
        Labels
        ------
            b: |
            e: epsilon
            n: newline
            s: ->
            t: terminal
            u: uppercase variable
        """

        cfg = ContextFreeGrammar("grammar.cfg")

        # Test post-conditions: 1
        self.assertEqual(cfg.rules["❬GrammarRecursion❭"] , OrderedSet([("❬Line❭", "n", "❬GrammarRecursion❭"), ("&",)]))
        self.assertEqual(cfg.rules["❬Line❭"]             , OrderedSet([("❬Var❭", "s", "❬LineFactored❭")]))
        self.assertEqual(cfg.rules["❬LineFactored❭"]     , OrderedSet([("e",), ("❬ProdRecursion❭",)]))
        self.assertEqual(cfg.rules["❬ProdRecursion❭"]    , OrderedSet([("❬SyntFormRecursion❭", "b", "❬ProdRecursion❭"), ("&",)]))
        self.assertEqual(cfg.rules["❬SyntFormRecursion❭"], OrderedSet([("t", "❬SyntFormRecursion❭"), ("❬Var❭", "❬SyntFormRecursion❭"), ("t",), ("❬Var❭",)]))
        self.assertEqual(cfg.rules["❬Var❭"]              , OrderedSet([("u",), ("<", "❬SyntFormRecursion❭", ">")]))

        print(cfg)

    def test_escape_chars(self):
        # read().split('\n')[i].split() produces \\n and \\t, which are
        # considered two distinct symbols.
        cfg = ContextFreeGrammar("test_escape_chars.cfg")
        self.assertNotEqual(cfg.rules["S"], OrderedSet([("\n",), ("\t",)]))
        print(cfg)

    # def test_rlr(self):

    #     cfg = dot_cfg.read_grammar("test_rlr_1.cfg")
    #     print(cfg)
    #     cfg.remove_left_recursion()
    #     print(cfg)

    #     cfg = dot_cfg.read_grammar("test_rlr_2.cfg")
    #     print(cfg)
    #     cfg.remove_left_recursion()
    #     print(cfg)
