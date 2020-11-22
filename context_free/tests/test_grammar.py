"""ContextFreeGrammar unit tests."""
import os
import filecmp
import unittest

from context_free.grammar import CFGS_DIR, ContextFreeGrammar, OrderedSet

class TestContextFreeGrammar(unittest.TestCase):

    def test_constructor(self): #FIXME: rename to read/write
        cfg = ContextFreeGrammar("test_constructorA.cfg")

        # Test post-conditions: 1
        self.assertEqual(cfg.rules["S"]   , OrderedSet([("B", "d"), ("&",)]))
        self.assertEqual(cfg.rules["B"]   , OrderedSet([("A", "b", "❬B'❭")]))
        self.assertEqual(cfg.rules["❬B'❭"], OrderedSet([("c", "❬B'❭"), ("&",)]))
        self.assertEqual(cfg.rules["A"]   , OrderedSet([("a", "❬A'❭"), ("❬A'❭",)]))
        self.assertEqual(cfg.rules["❬A'❭"], OrderedSet([("b", "❬B'❭", "d", "a", "❬A'❭"), ("&",)]))

        cfg.save_to_file("test_constructorT.cfg")
        test_path = os.path.join(CFGS_DIR, "test_constructorT.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_constructorA.cfg")

        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg2 = ContextFreeGrammar("test_constructorA.cfg")
        self.assertEqual(cfg2.rules["S"]   , OrderedSet([("B", "d"), ("&",)]))
        self.assertEqual(cfg2.rules["B"]   , OrderedSet([("A", "b", "❬B'❭")]))
        self.assertEqual(cfg2.rules["❬B'❭"], OrderedSet([("c", "❬B'❭"), ("&",)]))
        self.assertEqual(cfg2.rules["A"]   , OrderedSet([("a", "❬A'❭"), ("❬A'❭",)]))
        self.assertEqual(cfg2.rules["❬A'❭"], OrderedSet([("b", "❬B'❭", "d", "a", "❬A'❭"), ("&",)]))

        # print(cfg)
        # print(cfg2)

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

        cfg = ContextFreeGrammar("spec.cfg")

        # Test post-conditions: 1
        self.assertEqual(cfg.rules["❬GrammarRecursion❭"] , OrderedSet([("❬Line❭", "n", "❬GrammarRecursion❭"), ("&",)]))
        self.assertEqual(cfg.rules["❬Line❭"]             , OrderedSet([("❬Var❭", "s", "❬LineFactored❭")]))
        self.assertEqual(cfg.rules["❬LineFactored❭"]     , OrderedSet([("e",), ("❬ProdRecursion❭",)]))
        self.assertEqual(cfg.rules["❬ProdRecursion❭"]    , OrderedSet([("❬SyntFormRecursion❭", "b", "❬ProdRecursion❭"), ("&",)]))
        self.assertEqual(cfg.rules["❬SyntFormRecursion❭"], OrderedSet([("t", "❬SyntFormRecursion❭"), ("❬Var❭", "❬SyntFormRecursion❭"), ("t",), ("❬Var❭",)]))
        self.assertEqual(cfg.rules["❬Var❭"]              , OrderedSet([("u",), ("<", "❬SyntFormRecursion❭", ">")]))

        # print(cfg)

    def test_escape_chars(self):
        """
        Notes
        -----
            read().split('\n')[i].split() produces \\n and \\t, which are
            considered two distinct symbols.

        """
        cfg = ContextFreeGrammar("test_escape_chars.cfg")
        self.assertNotEqual(cfg.rules["S"], OrderedSet([("\n",), ("\t",)]))
        # print(cfg)

    def test_rlr(self):
        cfg = ContextFreeGrammar("test_rlr_1.cfg")
        cfg.remove_left_recursion()
        cfg.save_to_file("test_rlr_1T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_rlr_1T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_rlr_1A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_rlr_2.cfg")
        cfg.remove_left_recursion()
        cfg.save_to_file("test_rlr_2T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_rlr_2T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_rlr_2A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_rlr_exs_3a.cfg")
        cfg.remove_left_recursion()
        cfg.save_to_file("test_rlr_exs_3aT.cfg")
        test_path = os.path.join(CFGS_DIR, "test_rlr_exs_3aT.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_rlr_exs_3aA.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        # FIXME: Remove e-prods first!
        # cfg = ContextFreeGrammar("test_rlr_exs_3b.cfg")
        # cfg.remove_left_recursion()
        # cfg.save_to_file("test_rlr_exs_3bT.cfg")
        # test_path = os.path.join(CFGS_DIR, "test_rlr_exs_3bT.cfg")
        # ref_path = os.path.join(CFGS_DIR, "test_rlr_exs_3bA.cfg")
        # self.assertTrue(filecmp.cmp(test_path, ref_path))

    def test_ru(self):
        cfg = ContextFreeGrammar("test_ru_1.cfg")
        cfg.remove_unit()
        cfg.save_to_file("test_ru_1T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_ru_1T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_ru_1A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_ru_2.cfg")
        cfg.remove_unit()
        cfg.save_to_file("test_ru_2T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_ru_2T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_ru_2A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_ru_3.cfg")
        cfg.remove_unit()
        cfg.save_to_file("test_ru_3T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_ru_3T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_ru_3A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

    def test_re(self):
        cfg = ContextFreeGrammar("test_re_1.cfg")
        cfg.remove_epsilon()
        cfg.save_to_file("test_re_1T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_re_1T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_re_1A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_re_2.cfg")
        cfg.remove_epsilon()
        cfg.save_to_file("test_re_2T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_re_2T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_re_2A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))