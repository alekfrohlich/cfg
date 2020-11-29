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

        cfg = ContextFreeGrammar("test_ru_4.cfg")
        cfg.remove_unit()
        cfg.save_to_file("test_ru_4T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_ru_4T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_ru_4A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_ru_5.cfg")
        cfg.remove_unit()
        cfg.save_to_file("test_ru_5T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_ru_5T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_ru_5A.cfg")
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

        cfg = ContextFreeGrammar("test_re_3.cfg")
        cfg.remove_epsilon()
        cfg.save_to_file("test_re_3T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_re_3T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_re_3A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

    def test_rup(self):
        cfg = ContextFreeGrammar("test_rup_1.cfg")
        cfg.remove_unproductives()
        cfg.save_to_file("test_rup_1T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_rup_1T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_rup_1A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        # FIXME: empty language
        cfg = ContextFreeGrammar("test_rup_2.cfg")
        cfg.remove_unproductives()
        cfg.save_to_file("test_rup_2T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_rup_2T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_rup_2A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

    def test_rur(self):
        cfg = ContextFreeGrammar("test_rur_1.cfg")
        cfg.remove_unreachables()
        cfg.save_to_file("test_rur_1T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_rur_1T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_rur_1A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

    def test_rt(self):
        cfg = ContextFreeGrammar("test_rt_1.cfg")
        cfg.replace_terminals()
        cfg.save_to_file("test_rt_1T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_rt_1T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_rt_1A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

    def test_rs(self):
        cfg = ContextFreeGrammar("test_rs_1.cfg")
        cfg.reduce_size()
        cfg.save_to_file("test_rs_1T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_rs_1T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_rs_1A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_rs_2.cfg")
        cfg.reduce_size()
        cfg.save_to_file("test_rs_2T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_rs_2T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_rs_2A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

    def test_fnc(self):
        cfg = ContextFreeGrammar("test_fnc_1.cfg")
        cfg.convert_to_cnf()
        cfg.save_to_file("test_fnc_1T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_fnc_1T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_fnc_1A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

    def test_hlr(self):
        cfg = ContextFreeGrammar("test_rlr_1.cfg")
        self.assertTrue(cfg.has_left_recursion())

        cfg = ContextFreeGrammar("test_rlr_2.cfg")
        self.assertTrue(cfg.has_left_recursion())

        cfg = ContextFreeGrammar("test_rlr_exs_3a.cfg")
        self.assertTrue(cfg.has_left_recursion())

        cfg = ContextFreeGrammar("test_rlr_exs_3b.cfg")
        self.assertTrue(cfg.has_left_recursion())

        cfg = ContextFreeGrammar("test_rlr_1A.cfg")
        self.assertFalse(cfg.has_left_recursion())

        cfg = ContextFreeGrammar("test_rlr_2A.cfg")
        self.assertFalse(cfg.has_left_recursion())

        cfg = ContextFreeGrammar("test_rlr_exs_3aA.cfg")
        self.assertFalse(cfg.has_left_recursion())

        cfg = ContextFreeGrammar("test_rlr_exs_3bA.cfg")
        self.assertFalse(cfg.has_left_recursion())

        cfg = ContextFreeGrammar("test_firsts_1.cfg")
        self.assertFalse(cfg.has_left_recursion())

        cfg = ContextFreeGrammar("test_firsts_2.cfg")
        self.assertFalse(cfg.has_left_recursion())

    def test_he(self):
        cfg = ContextFreeGrammar("test_re_1.cfg")
        self.assertTrue(cfg.has_e())

        cfg = ContextFreeGrammar("test_re_2.cfg")
        self.assertTrue(cfg.has_e())

        cfg = ContextFreeGrammar("test_re_3.cfg")
        self.assertTrue(cfg.has_e())

        cfg = ContextFreeGrammar("test_re_1A.cfg")
        self.assertFalse(cfg.has_e())

        cfg = ContextFreeGrammar("test_re_2A.cfg")
        self.assertFalse(cfg.has_e())

        cfg = ContextFreeGrammar("test_re_3A.cfg")
        self.assertFalse(cfg.has_e())

        cfg = ContextFreeGrammar("test_rlr_exs_3aA.cfg")
        self.assertTrue(cfg.has_e())

        cfg = ContextFreeGrammar("test_rlr_exs_3bA.cfg")
        self.assertTrue(cfg.has_e())

        cfg = ContextFreeGrammar("test_rlr_exs_3aA.cfg")
        cfg.remove_epsilon()
        self.assertFalse(cfg.has_e())

        cfg = ContextFreeGrammar("test_rlr_exs_3bA.cfg")
        cfg.remove_epsilon()
        self.assertFalse(cfg.has_e())

    def test_hc(self):
        cfg = ContextFreeGrammar("test_hc_1.cfg")
        self.assertTrue(cfg.has_cycle())

        cfg = ContextFreeGrammar("test_hc_2.cfg")
        self.assertTrue(cfg.has_cycle())

        cfg = ContextFreeGrammar("test_hc_3.cfg")
        self.assertTrue(cfg.has_cycle())

        cfg = ContextFreeGrammar("test_hc_4.cfg")
        self.assertTrue(cfg.has_cycle())

        cfg = ContextFreeGrammar("test_hc_1.cfg")
        cfg.remove_unit()
        self.assertFalse(cfg.has_cycle())

        cfg = ContextFreeGrammar("test_hc_2.cfg")
        cfg.remove_unit()
        self.assertFalse(cfg.has_cycle())

        cfg = ContextFreeGrammar("test_hc_3.cfg")
        cfg.remove_unit()
        self.assertFalse(cfg.has_cycle())

        cfg = ContextFreeGrammar("test_hc_4.cfg")
        cfg.remove_unit()
        self.assertFalse(cfg.has_cycle())

        cfg = ContextFreeGrammar("test_fnc_1.cfg")
        self.assertFalse(cfg.has_cycle())


    def test_lf(self):
        cfg = ContextFreeGrammar("test_lf_1.cfg")
        cfg.left_factoring()
        cfg.save_to_file("test_lf_1T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_lf_1T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_lf_1A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_lf_2.cfg")
        cfg.left_factoring()
        cfg.save_to_file("test_lf_2T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_lf_2T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_lf_2A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_lf_3.cfg")
        cfg.left_factoring()
        cfg.save_to_file("test_lf_3T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_lf_3T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_lf_3A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_lf_4.cfg")
        self.assertFalse(cfg.left_factoring())

        cfg = ContextFreeGrammar("test_lf_5.cfg")
        self.assertFalse(cfg.left_factoring())

        cfg = ContextFreeGrammar("test_lf_6.cfg")
        cfg.left_factoring()
        cfg.save_to_file("test_lf_6T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_lf_6T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_lf_6A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_lf_exs_4c.cfg")
        cfg.left_factoring()
        cfg.save_to_file("test_lf_exs_4cT.cfg")
        test_path = os.path.join(CFGS_DIR, "test_lf_exs_4cT.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_lf_exs_4cA.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))

        cfg = ContextFreeGrammar("test_lf_follow_1.cfg")
        cfg.left_factoring()
        cfg.save_to_file("test_lf_follow_1T.cfg")
        test_path = os.path.join(CFGS_DIR, "test_lf_follow_1T.cfg")
        ref_path = os.path.join(CFGS_DIR, "test_lf_follow_1A.cfg")
        self.assertTrue(filecmp.cmp(test_path, ref_path))


    # def test_firsts(self):
    #     cfg = ContextFreeGrammar("test_firsts_1.cfg")
    #     cfg.firsts()
    #     # cfg.save_to_file("test_firsts_1T.cfg")
    #     # test_path = os.path.join(CFGS_DIR, "test_firsts_1T.cfg")
    #     # ref_path = os.path.join(CFGS_DIR, "test_firsts_1A.cfg")
    #     # self.assertTrue(filecmp.cmp(test_path, ref_path))

    #     cfg = ContextFreeGrammar("test_firsts_2.cfg")
    #     cfg.firsts()

    # def test_follows(self):
    #     cfg = ContextFreeGrammar("test_firsts_1.cfg")
    #     cfg.firsts()
    #     cfg.follows()
    #     # cfg.save_to_file("test_firsts_1T.cfg")
    #     # test_path = os.path.join(CFGS_DIR, "test_firsts_1T.cfg")
    #     # ref_path = os.path.join(CFGS_DIR, "test_firsts_1A.cfg")
    #     # self.assertTrue(filecmp.cmp(test_path, ref_path))

    #     cfg = ContextFreeGrammar("test_firsts_2.cfg")
    #     cfg.firsts()
    #     cfg.follows()

    # def test_make_table(self):
    #     cfg = ContextFreeGrammar("test_mt_1.cfg")
    #     cfg.firsts()
    #     cfg.follows()
    #     cfg.make_table()

    # def test_word(self):
    #     cfg = ContextFreeGrammar("test_mt_1.cfg")
    #     cfg.firsts()
    #     cfg.follows()
    #     cfg.make_table()
    #     print(cfg.word("ioiai"))
    #     print(cfg.word("ooi"))
    #     print(cfg.word(""))
    #     print(cfg.word("i"))
    #     print(cfg.word("ia"))

    #     cfg = ContextFreeGrammar("test_mt_2.cfg")
    #     cfg.firsts()
    #     cfg.follows()
    #     cfg.make_table()
    #     print(cfg.word("cvfbe;"))

