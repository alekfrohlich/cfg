"""This module provides a context-free grammar implementation.

Grammars should follow the dotcfg specification found in cfgs/grammar.cfg. Furthermore,
terminals should be non-upper case unicode characters, and variables should be either:
    - upper case unicode characters, as in "A" and "Æ"; or
    - length > 1 unicode strings inside square brackets, as in "❬variable❭".
      Note that "❭" may not be present in 'variable'. The brackets are "\u276c" and "\u276d".

The restrictions to these are:
    - escape chars

Notes
-----
    Python's str.isupper is assumed to consider all unicode's cased characters.

        The list can be found here: https://www.compart.com/en/unicode/category

    As for data structures,

        1. Tuples are used to represent frozen lists, as lists can't be set elements.
           Be aware, though, that (x) is not a tuple, but (x,) is.
        2. OrderedSet is used to preserve the order that the productions originally appeared
           on.
        3. The default dict implementation already preserver order.
"""
import os

from oset.ordered_set import OrderedSet


CFGS_DIR = os.path.join(os.path.dirname(__file__), '../cfgs')


class ContextFreeGrammar():
    def __init__(self, filename: str):
        """

        Pre-conditions
        --------------
            1. filename names a .cfg file inside cfgs/
            2. The file is a valid grammar according to our context-free grammar specification;
               c.f., grammar.cfg
            3. The file contains no white spaces inside syntactical forms # FIXME: wouldn't the grammar capture this already?
            4. Assumes the grammar has no vars without productions

        Post-conditions
        ---------------
            1. rules is properly tokenized using the three categories: terminal,
            uppercase-variable, and brackets-variable.
            2. variables is an OrderedSet with len > 0, where each entry is valid var
            3. terminals is an OrderedSet, where each entry is a valid term
            4. rules is a dict where each variable has an OrderedSet entry
            5. start is in variables

        Notes
        -----
            The first grammar that is read, grammar.cfg, is assumed to be valid; to confirm this, you may run the unit tests.
        """

        filepath = os.path.join(CFGS_DIR, filename)
        assert filepath[-4:] == '.cfg', "Invalid extension"

        self.variables = OrderedSet()
        self.terminals = OrderedSet()
        self.rules = dict()
        self.start = None

        with open(filepath, 'r') as f:
            # FIXME: Syntax Analysis
            lines = f.read().split("\n")

            for line in lines:
                if line == lines[-1]:
                    assert len(line) == 0
                    continue

                items = line.split()
                var = items[0]
                self.rules[var] = OrderedSet()
                self.variables.add(var)

                # First iteration
                if self.start is None:
                    self.start = var

                k = 2
                while k < len(items):
                    raw = items[k]

                    # NOTE: is not a method since the pre-conds are not worth testing
                    # Tokenize rule
                    tokenized = []
                    i = 0
                    while i < len(raw):
                        c = raw[i]

                        if c == '❬': # brackets-variable
                            j = i + 1
                            while raw[j] != '❭':
                                j += 1

                            assert len(raw[i:j+1]) > 3
                            tokenized.append(raw[i:j+1])
                            # self.variables.add(raw[i:j+1])
                            i = j + 1
                        else: # uppercase-cariable or terminal
                            tokenized.append(c)
                            if c.isupper():
                                pass
                                # self.variables.add(c)
                            else:
                                self.terminals.add(c)
                            i += 1
                    self.rules[var].add(tuple(tokenized))
                    k += 2

        # Assert post-conditions: 2-5; see test_constructor for 1.
        assert type(self.variables) == OrderedSet and len(self.variables) > 0 \
            and all([(v.isupper() and len(v) == 1) or (v[0] == '❬' and v[-1] == '❭' and len(v) > 2) for v in self.variables])
        assert type(self.terminals) == OrderedSet and all([type(t) == str and not (t.isupper()) for t in self.terminals])
        assert type(self.rules) == dict and self.rules.keys() == self.variables and all([type(val) == OrderedSet for val in self.rules.values()])
        assert self.start in self.variables

    def __str__(self) -> str:
        string = ""

        first = True
        for rule in self.rules[self.start]:
            if first:
                string += "{} -> {} ".format(self.start, "".join(rule))
                first = False
            else:
                string += "| {} ".format("".join(rule))
        string = string[:-1] + "\n"

        for var in self.variables:
            if var == self.start:
                continue
            first = True
            for rule in self.rules[var]:
                if first:
                    string += "{} -> {} ".format(var, "".join(rule))
                    first = False
                else:
                    string += "| {} ".format("".join(rule))
            string = string[:-1] + "\n"
        return string

    def save_to_file(self, filename: str):
        filepath = os.path.join(CFGS_DIR, filename)
        with open(filepath, 'w') as f:
            f.write(str(self))

    # def remove_left_recursion(self):

    #     for i in range(len(self.variables)):
    #         direct = False
    #         for j in range(i):
    #             to_remove = set()
    #             for production in self.rules[self.variables[i]]:
    #                 print("i:{}   j:{}   prod:{}".format(self.variables[i],self.variables[j],production))
    #                 if self.variables[j] == production[0]:
    #                     alpha = production[1:]
    #                     to_remove.add(production)
    #                     for beta in self.rules[self.variables[j]]:
    #                         self.rules[self.variables[i]].add(beta + alpha)
    #                         if self.variables[i] == beta[0]:
    #                             direct = True
    #                     print("alpha:{}".format(alpha))

    #             for rem in to_remove: #cuidar para nao remover todos!!!!!!!!!!1
    #                 print("rem:: {}".format(rem))
    #                 self.rules[self.variables[i]].discard(rem)
    #         if direct:
    #             new_var = "❬{}´❭".format(self.variables[i])
    #             self.variables.add(new_var)
    #             self.rules[new_var] = OrderedSet()
    #             new_ord_i = OrderedSet()
    #             for production in self.rules[self.variables[i]]:
    #                 if production[0] == self.variables[i]:
    #                     self.rules[new_var].add(production[1:]+(new_var, ))
    #                 else:
    #                     new_ord_i.add(production+(new_var, ))
    #             if len(new_ord_i) == 0:
    #                 new_ord_i.add((new_var,))
    #             self.rules[self.variables[i]] = new_ord_i
    #             self.rules[new_var].add(('&',))
