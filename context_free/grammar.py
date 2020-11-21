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
            3. rules is a dict where each variable has an entry
            4. start is a valid variable

        Post-conditions
        ---------------
            1. rules is properly tokenized using the three categories cited above: terminal,
               uppercase-variable, and brackets-variable.
        """

        # Asserting pre-conditions
        assert type(variables) == OrderedSet and len(variables) > 0 \
            and all([(v.isupper() and len(v) == 1) or (v[0] == '❬' and v[-1] == '❭' and len(v) > 2) for v in variables]) # This will become obsolete
        assert type(terminals) == OrderedSet and all([type(t) == str for t in terminals])
        assert type(rules) == dict and rules.keys() == variables and all([type(val) == OrderedSet for val in rules.values()])
        assert start in variables

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


    def remove_left_recursion(self):

        for i in range(len(self.variables)):
            direct = False
            for j in range(i):
                to_remove = set()
                for production in self.rules[self.variables[i]]:
                    print("i:{}   j:{}   prod:{}".format(self.variables[i],self.variables[j],production))
                    if self.variables[j] == production[0]:
                        alpha = production[1:]
                        to_remove.add(production)
                        for beta in self.rules[self.variables[j]]:
                            self.rules[self.variables[i]].add(beta + alpha)
                            if self.variables[i] == beta[0]:
                                direct = True
                        print("alpha:{}".format(alpha))

                for rem in to_remove: #cuidar para nao remover todos!!!!!!!!!!1
                    print("rem:: {}".format(rem))
                    self.rules[self.variables[i]].discard(rem)
            if direct:
                new_var = "❬{}´❭".format(self.variables[i])
                self.variables.add(new_var)
                self.rules[new_var] = OrderedSet()
                new_ord_i = OrderedSet()
                for production in self.rules[self.variables[i]]:
                    if production[0] == self.variables[i]:
                        self.rules[new_var].add(production[1:]+(new_var, ))
                    else:
                        new_ord_i.add(production+(new_var, ))
                if len(new_ord_i) == 0:
                    new_ord_i.add((new_var,))
                self.rules[self.variables[i]] = new_ord_i
                self.rules[new_var].add(('&',))


