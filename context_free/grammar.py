"""This module provides a context-free grammar implementation.

Grammars should be of the form seen in the .cfg files. Furthermore,
terminals should be non-upper case unicode characters, and variables should be either:
    - length 1 and upper case unicode characters, as in "A" and "Æ"; or
    - length > 1 unicode strings inside square brackets, as in "❬variable❭".
      Note that "❭" may not be present in 'variable'. The brackets are "\u276c" and "\u276d".

# FIXME: Are there any restrictions to terminals/variables?

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
from oset.ordered_set import OrderedSet

class ContextFreeGrammar():
    def __init__(self, variables: OrderedSet, terminals: OrderedSet, rules: dict, start = 'S'):
        """

        Pre-conditions
        --------------
            1. variables is an OrderedSet with len > 0
            2. terminals is an OrderedSet
            3. rules is a dict where each variable has productions.
            4. start is a valid variable

        Post-conditions
        ---------------
            1. rules is properly tokenized using the three categories cited above: terminal,
               uppercase-variable, and brackets-variable.
        """

        # Asserting pre-conditions
        assert type(variables) == OrderedSet and len(variables) > 0
        assert type(terminals) == OrderedSet
        assert type(rules) == dict and rules.keys() == variables and all([type(val) == OrderedSet for val in rules.values()])
        assert (start.isupper() and len(start) == 1) or (start[0] == '❬' and start[-1] == '❭' and len(start) > 2)

        self.variables = variables
        self.terminals = terminals
        self.rules = {v: OrderedSet() for v in variables}
        self.start = start

        def tokenize(raw):
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

                    i = j + 1

                else: # uppercase-cariable or terminal
                    tokenized.append(c)
                    i += 1

            return tuple(tokenized)

        for v, v_rules in rules.items():
            for rule in v_rules:
                self.rules[v].add(tokenize(rule))

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
