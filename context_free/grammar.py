"""This module provides a context-free grammar implementation.

Grammars should follow the dotcfg specification found in cfgs/grammar.cfg. Furthermore,
terminals should be non-upper case unicode characters, and variables should be either:
    - upper case unicode characters, as in "A" and "Æ"; or
    - length > 1 unicode strings inside square brackets, as in "❬variable❭".
      Note that "❭" may not be present in 'variable'. The brackets are "\u276c" and "\u276d".

The restrictions to these are:
    - escape chars
    - $: bottom of stack

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
from collections import deque

from oset.ordered_set import OrderedSet


CFGS_DIR = os.path.join(os.path.dirname(__file__), '../cfgs')


class ContextFreeGrammar:
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

        self.first = dict()
        self.follow = dict()
        self.prod_to_id = dict()
        self.id_to_prod = dict()
        self.table = dict()

        with open(filepath, 'r') as f:
            # ContextFreeGrammar.validate_cfg_word(f.read())
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
                                if c != "&":
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
            string += "{} -> ".format(var)
            for rule in self.rules[var]:
                if first:
                    string += "{} ".format("".join(rule))
                    first = False
                else:
                    string += "| {} ".format("".join(rule))
            string = string[:-1] + "\n"
        return string

    def save_to_file(self, filename: str):
        filepath = os.path.join(CFGS_DIR, filename)
        with open(filepath, 'w') as f:
            f.write(str(self))

    @staticmethod
    def validate_cfg_word(word: str) -> bool:
        if BOOTSTRAPPING:
            print("BOOOT")
        else:
            print("SPECS ALREADY ON")

    def has_e(self): #ok
        for v in self.variables:
            for prod in self.rules[v]:
                if v != self.start and prod == ("&", ):
                    return True
        return False

    def has_cycle(self): #ok
        """
        Notes
        -----
            has_cycle is very similar to remove_unti. The only diffetence is that
            has_cycle does not change the grammar.
        """
        def bfs(s):
            visited[s] = True
            q = deque()
            q.append(s)
            v = s
            while len(q) > 0:
                v = q.pop()
                for u in edges[v]:
                    if not visited[u]:
                        visited[u] = True
                        q.append(u)

        edges = dict()
        for var in self.variables:
            edges[var] = OrderedSet()

        for h in self.variables:
            if h in self.rules.keys():
                for b in self.rules[h]:
                    if len(b) == 1 and b[0] in self.variables:
                        edges[h].add(b[0])
        new_rules = dict()
        for var in self.variables:
            new_rules[var] = OrderedSet()

        for var in self.variables:
            visited = dict()
            for va in self.variables:
                visited[va] = False
            bfs(var)
            for contender in self.variables:
                if visited[contender]:
                    for prod in self.rules[contender]:
                        if prod == (var,):
                            return True
        return False

    def remove_left_recursion(self): #ok
        """
        Exceptions
        --------------
            1. self is not e-free.
            2. self is not cycle-free.

        Notes
        -----
            Be aware when Aj has no productions.
            While removing direct recursion, one may end up with len(prods_i) == 0, since
            there may be S => Sbeta, where beta has no productions.

        """
        if self.has_e():
            print("\n\nGRAMMAR IS NOT &-free\n& has not been removed")
            print("You need to call remove_epsilon\n\n")
            return False

        if self.has_cycle():
            print("\n\nGRAMMAR IS NOT cycle-free\nCyclical productions have not been removed")
            print("You need to call remove_unit")
            print("Note that remove_unit will remove cyclical productions and unit productions\n\n")
            return False

        # Remove indirect
        for i in range(len(self.variables)):
            direct = False
            for j in range(i):
                to_remove = set()
                for production in self.rules[self.variables[i]]:
                    if self.variables[j] == production[0]:
                        alpha = production[1:]
                        to_remove.add(production)
                        for beta in self.rules[self.variables[j]]:
                            self.rules[self.variables[i]].add(beta + alpha)

                for rem in to_remove:
                    self.rules[self.variables[i]].discard(rem)

            for production in self.rules[self.variables[i]]:
                if production[0] == self.variables[i]:
                    direct = True

            if direct:
                new_var = "❬{}'❭".format(self.variables[i])
                self.variables.add(new_var)
                self.rules[new_var] = OrderedSet()
                new_prods_i = OrderedSet()
                for production in self.rules[self.variables[i]]:
                    if production[0] == self.variables[i]:
                        self.rules[new_var].add(production[1:]+(new_var, ))
                    else:
                        new_prods_i.add(production+(new_var, ))

                self.rules[self.variables[i]] = new_prods_i
                self.rules[new_var].add(('&',))

    def remove_unit(self): #ok
        """
        Post-conditions: may return variable with no production

        Note:
        In this algorithm cyclical productions will be eliminated.
        A -> B                          A ->
        B -> C         -------->        B ->
        C -> A                          C ->

        Our algorithm takes care of cyclical productions
        """
        def bfs(s):
            visited[s] = True
            q = deque()
            q.append(s)
            v = s
            while len(q) > 0:
                v = q.pop()
                for u in edges[v]:
                    if not visited[u]:
                        visited[u] = True
                        q.append(u)

        edges = dict()
        for var in self.variables:
            edges[var] = OrderedSet()

        for h in self.variables:
            if h in self.rules.keys():
                for b in self.rules[h]:
                    if len(b) == 1 and b[0] in self.variables:
                        edges[h].add(b[0])
        new_rules = dict()
        for var in self.variables:
            new_rules[var] = OrderedSet()

        for var in self.variables:
            visited = dict()
            for va in self.variables:
                visited[va] = False
            bfs(var)
            for contender in self.variables:
                if visited[contender]:
                    for prod in self.rules[contender]:
                        if len(prod) > 1 or prod[0] not in self.variables:
                            new_rules[var].add(prod)
        self.rules = new_rules

    def remove_epsilon(self): #ok

        def power_set(i, cuts):
            if i == len(cuts[0]):
                new_ps = OrderedSet()
                for c in cuts:
                    new_c = tuple()
                    for c2 in c:
                        if c2 != "$":
                            new_c += (c2,)
                    if len(new_c) > 0:
                        new_ps.add(new_c)
                return new_ps

            if cuts[0][i] in nullables:
                to_add = OrderedSet()
                for s in cuts:
                    to_add.add(s[:i] + ("$",) + s[i+1:])
                cuts.update(to_add)
            return power_set(i+1, cuts)

        nullables = OrderedSet()
        nullables.add("&")

        changed = True
        while changed:
            changed = False
            for var, prods in self.rules.items():
                for prod in prods:
                    if all([p in nullables for p in prod]) and var not in nullables:
                        nullables.add(var)
                        changed = True

        for var in self.variables:
            to_add = OrderedSet()
            for prod in self.rules[var]:
                to_add.update(power_set(0, OrderedSet([prod])))
            self.rules[var].update(to_add)
            if ("&", ) in self.rules[var]:
                self.rules[var].discard(("&", ))

        if self.start in nullables:
            self.variables.add("❬'{}❭".format(self.start))
            self.rules["❬'{}❭".format(self.start)] = OrderedSet([(self.start, ), ("&", )])
            self.start = "❬'{}❭".format(self.start)

    def remove_unproductives(self): #ok
        """
        Notes:

        If the grammar generates no words (empty language) then the grammar returned will be
            start_symbol -> start_symbol
        and it will keep its terminals.
        """
        productives = OrderedSet()
        for t in self.terminals:
            productives.add(t)
        productives.add("&")

        changed = True
        while changed:
            changed = False
            for var, prods in self.rules.items():
                for prod in prods:
                    if all([p in productives for p in prod]) and var not in productives:
                        productives.add(var)
                        changed = True

        new_rules = dict()
        for v in self.variables:
            new_production = OrderedSet()
            for production in self.rules[v]:
                if all([p in productives for p in production]):
                    new_production.add(production)
            new_rules[v] = new_production

        self.rules = new_rules

        to_remove = OrderedSet()
        for v in self.variables:
            if len(self.rules[v]) == 0:
                to_remove.add(v)

        for rem in to_remove:
            del self.rules[rem]
            self.variables.discard(rem)

        # if empty language
        if self.start not in self.rules.keys():
            self.variables = OrderedSet()
            self.rules = dict()
            self.variables.add(self.start)
            self.rules[self.start] = OrderedSet()
            self.rules[self.start].add(self.start)

    def remove_unreachables(self): #ok
        """
        Pre_conditions: None
        """
        def bfs(s):
            visited[s] = True
            q = deque()
            q.append(s)
            v = s
            while len(q) > 0:
                v = q.pop()
                for u in edges[v]:
                    if not visited[u]:
                        visited[u] = True
                        q.append(u)

        edges = dict()
        for var in self.variables:
            edges[var] = OrderedSet()

        for h in self.variables:
            if h in self.rules.keys():
                for b in self.rules[h]:
                    for symbol in b:
                        if symbol in self.variables:
                            edges[h].add(symbol)
        new_rules = dict()
        for var in self.variables:
            new_rules[var] = OrderedSet()

        visited = dict()
        for va in self.variables:
                visited[va] = False
        bfs(self.start)


        to_remove = OrderedSet()
        for v in self.variables:
            if not visited[v]:
                to_remove.add(v)

        for rem in to_remove:
            del self.rules[rem]
            self.variables.discard(rem)

    def replace_terminals(self): #ok
        """
        Pre_conditions: None
        """
        new_v_id = 0

        #var_to_terminal checks if variable already exists or if variable has already been created
        # var_to_terminal does not consider already duplicated variables
        def var_to_terminal(sym):
            var = None
            for v in self.variables:
                if len(self.rules[v]) == 1 and self.rules[v][0] == (sym, ):
                    var = v
                    return var
            for v in to_add_var:
                if len(self.rules[v]) == 1 and self.rules[v][0] == (sym, ):
                    var = v
                    return var
            return var

        # create_new_v creates new variable
        def create_new_v(sym):
            nonlocal new_v_id
            new_v_id += 1
            new_v = "❬R{}❭".format(new_v_id)
            to_add_var.add(new_v)
            self.rules[new_v] = OrderedSet([(sym, )])
            new_rules[new_v] = OrderedSet([(sym, )])
            return new_v

        to_add_var = OrderedSet()
        new_rules = dict()
        for v in self.variables:
            to_add = OrderedSet()
            for prod in self.rules[v]:
                old_prod = list(prod)
                if(len(old_prod) >= 2):
                    for i in range(len(old_prod)):
                        symbol = old_prod[i]
                        if symbol in self.terminals:
                            new_v = var_to_terminal(symbol)
                            if new_v is None:
                                # print("oi")
                                new_v = create_new_v(symbol)
                            for j in range(i, len(old_prod)):
                                if old_prod[j] == symbol:
                                    old_prod[j] = new_v
                to_add.add(tuple(old_prod))
            new_rules[v] = to_add

        self.rules = new_rules
        for v in to_add_var:
            # print(v)
            self.variables.add(v)

        # print(self.variables)

    def reduce_size(self): #ok
        # reduce_size does not check if new_v was already in the grammar

        new_rules = dict()
        to_add_var = OrderedSet()
        number_v = -1
        new_v_id = 0

        for v in self.variables:
            number_v += 1
            new_v_id = 0
            new_rules[v] = OrderedSet()
            for prod in self.rules[v]:
                lp = len(prod)
                if lp > 2:
                    new_v = "❬C({},{})❭".format(number_v, new_v_id)
                    to_add_var.add(new_v)
                    new_v_id += 1
                    new_rules[new_v] = OrderedSet([(prod[lp-2],prod[lp-1])])

                    for i in range(lp - 3, 0, -1):
                        old_v = new_v
                        new_v = "❬C({},{})❭".format(number_v, new_v_id)
                        to_add_var.add(new_v)
                        new_rules[new_v] = OrderedSet([(prod[i],old_v)])
                        new_v_id += 1

                    new_rules[v].update(OrderedSet([(prod[0],new_v)]))
                else:
                    new_rules[v].add(prod)

        self.rules = new_rules
        for v in to_add_var:
            self.variables.add(v)

    def fnc(self): #ok
        self.remove_epsilon()
        self.remove_unit()
        self.remove_unproductives()
        self.remove_unreachables()
        self.replace_terminals()
        self.reduce_size()

    def first_var(self, v): #ok
        # first_var calculates first(v) using DP
        # DP is not used to calculate the first of a sentence
        if len(self.first[v]) != 0:
            return self.first[v]

        for prod in self.rules[v]:
            for p in prod:
                to_add = self.first_var(p)
                self.first[v].update(to_add)
                if "&" not in to_add:
                    self.first[v].discard("&")
                    break
        return self.first[v]

    def has_left_recursion(self): #ok
        def bfs(s):
            visited[s] = True
            q = deque()
            q.append(s)
            v = s
            while len(q) > 0:
                v = q.pop()
                for u in edges[v]:
                    if u == s:
                        return True
                    if not visited[u]:
                        visited[u] = True
                        q.append(u)
            return False

        edges = dict()
        for v in self.variables:
            edges[v] = OrderedSet()
        for v in self.variables:
            for prod in self.rules[v]:
                if prod[0] in self.variables:
                    edges[v].add(prod[0])


        for v in self.variables:
            visited = dict()
            for var in self.variables:
                visited[var] = False
            if bfs(v):
                return True

        return False

    def firsts(self): #ok
        """
        Exceptions
        --------------
            1. self has left recursion.
        """
        if self.has_left_recursion():
            print("\n\nGRAMMAR HAS LEFT RECURSION\nNone first has been calculated")
            print("You need to call remove_left_recursion\n\n")
            return False

        self.first["&"] = OrderedSet()
        self.first["&"].add("&")
        for t in self.terminals:
            self.first[t] = OrderedSet()
            self.first[t].add(t)
        for v in self.variables:
            self.first[v] = OrderedSet()

        for v in self.variables:
            self.first_var(v)

    def first_body(self, body): #ok
        """
        Pre-conditions
        --------------
            1. self.first() has already been called.

        NOTES
        -------------
        first_body calculates the first of a sentence
        """
        lb = len(body)

        total = OrderedSet()
        for b in body:
            to_add = self.first[b]
            total.update(to_add)
            if "&" not in to_add:
                total.discard("&")
                break
        return total

    def follows(self): #ok
        """
        Pre-conditions
        --------------
            1. self.first() has already been called.
        """
        for v in self.variables:
            self.follow[v] = OrderedSet()

        self.follow[self.start].add("$")
        add = True
        while(add):
            add = False
            for head, bodies in self.rules.items():
                for body in bodies:
                    lb = len(body)
                    for i in range(lb-1):
                        if body[i] in self.variables:
                            to_add = self.first_body(body[i+1:])
                            to_add.discard("&")
                            if not to_add.issubset(self.follow[body[i]]):
                                add = True
                                self.follow[body[i]].update(to_add)
                    to_add = self.follow[head]
                    to_add.discard("&")
                    for i in range(lb-1, -1, -1):
                        if body[i] in self.variables:
                            if not to_add.issubset(self.follow[body[i]]):
                                add = True
                                self.follow[body[i]].update(to_add)
                            if "&" not in self.first[body[i]]:
                                break
                        else:
                            break

    def make_table(self): #ok
        """
        Pre-conditions
        --------------
            1. self does not have left recursion.
            2. self.firsts() has already been called.
            3. self.follows() has already been called.

        Exceptions
        --------------
            1. self is not left-factored.
        """

        id = 0
        for head, bodies in self.rules.items():
            for body in bodies:
                id+=1
                self.prod_to_id[(head, body)] = id
                self.id_to_prod[id] = (head, body)

        for v in self.variables:
            for t in self.terminals:
                self.table[(v, t)] = -1
        for v in self.variables:
            self.table[(v, "$")] = -1

        for v in self.variables:
            for alpha in self.rules[v]:
                first = self.first_body(alpha)
                for f in first:
                    if f != "&":
                        if self.table[(v, f)] != -1:
                            print("\n\n\nNOT LEFT-FACTORED\nYou need to use the method remove_left_recursion\n\n\n")
                        self.table[(v, f)] = self.prod_to_id[(v, alpha)]
                if "&" in first:
                    for f in self.follow[v]:
                        if self.table[(v, f)] != -1:
                            print("\n\n\nNOT LEFT-FACTORED\nYou need to use the method remove_left_recursion\n\n\n")
                        self.table[(v, f)] = self.prod_to_id[(v, alpha)]

        # for t in self.terminals:
        #     print("{} ".format(t), end="")
        # print("$")

        # for head, bodies in self.rules.items():
        #     for body in bodies:
        #         print("head:{}   body:{}     id:{}", head, body, self.prod_to_id[(head,body)])

        # for v in self.variables:
        #     print("{}:: ".format(v), end="")
        #     for t in self.terminals:
        #         print("{} ".format(self.table[(v, t)]), end="")
        #     print("{}".format(self.table[(v, "$")]))

    def word(self, w): #ok
        """
        Pre-conditions
        --------------
            1. make_table has already been called and printed no error messages.
        """
        w+="$"
        lw = len(w)
        head = 0
        stack = ["$", self.start]
        while(True):
            print("{} {}".format(w[head], stack))
            if stack[-1] in self.terminals or stack[-1] == "$":
                if stack[-1] == w[head]:
                    if w[head] == "$":
                        return True
                    else:
                        stack.pop()
                        head+=1
                else:
                    return False
            else:
                id_table = self.table[(stack[-1], w[head])]
                if id_table != -1:
                    stack.pop()
                    var, prod = self.id_to_prod[id_table]
                    lp = len(prod)
                    if prod == ("&",):
                        continue
                    for i in range(lp-1, -1, -1):
                        stack.append(prod[i])
                else:
                    return False


    def left_factoring(self):
        pass


BOOTSTRAPPING = True
SPEC_GRAMMAR = ContextFreeGrammar("spec.cfg")
BOOTSTRAPPING = False
