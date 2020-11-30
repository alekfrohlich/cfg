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
        3. The default dict implementation already preserves order.
"""
import os
from collections import deque

from oset.ordered_set import OrderedSet

from .parser import PredictiveParser


CFGS_DIR = os.path.join(os.path.dirname(__file__), '../cfgs')


class Graph:
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges

    def bfs(self, s) -> list:
        visited = {v:False for v in self.vertices}
        visited[s] = True
        q = deque()
        q.append(s)
        while len(q) > 0:
            v = q.pop()
            for u in self.edges[v]:
                if not visited[u]:
                    visited[u] = True
                    q.append(u)
        return visited

    def has_loop(self, s) -> bool:
        """Test whether a vertex can reach itself."""
        visited = {v:False for v in self.vertices}
        visited[s] = True
        q = deque()
        q.append(s)
        while len(q) > 0:
            v = q.pop()
            for u in self.edges[v]:
                if u == s:
                    return True
                if not visited[u]:
                    visited[u] = True
                    q.append(u)
        return False


class ContextFreeGrammar:
    def __init__(self, filename: str):
        """
        Pre-conditions
        --------------
            1. filename doesn't name a .cfg file inside cfgs/
            2. The file is an invalid grammar according to our context-free grammar specification (see spec.cfg)
            3. Assumes the grammar has no vars without productions # FIXME: really?

        Post-conditions
        ---------------
            1. rules is properly tokenized using the three categories: terminal,
               uppercase-variable, and brackets-variable.
            2. variables is an OrderedSet with len > 0, where each entry is valid var
            3. terminals is an OrderedSet, where each entry is a valid term (lower-case, len = 1)
            4. rules is a dict where each variable has an OrderedSet entry
            5. start is in variables
            6. & is not in term

        Notes
        -----
            The first grammar that is read, spec.cfg, is assumed to be valid; to confirm this,
            you may run the unit tests.
        """

        filepath = os.path.join(CFGS_DIR, filename)
        assert filepath[-4:] == '.cfg', "Invalid extension"

        self.variables = OrderedSet()
        self.terminals = OrderedSet()
        self.rules = dict()
        self.start = None

        with open(filepath, 'r') as f:
            file_read = f.read()
            ContextFreeGrammar.validate_cfg_word(file_read)
            lines = file_read.split("\n")

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
        self.CHECK_GRAMMAR()

    def __str__(self) -> str: # CONST
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

    def save_to_file(self, filename: str): # CONST
        filepath = os.path.join(CFGS_DIR, filename)
        with open(filepath, 'w') as f:
            f.write(str(self))

    def CHECK_GRAMMAR(self): # CONST
        """Temporary method for forcing structure into python."""
        # Assert post-conditions: 2-6.
        # NOTE: Nicolas, eu decidi testar tudo sempre pq tem algoritmo que cria producao
        #       Alem disso, tb assumi que (1) já é bem testado pelos testes
        assert type(self.variables) == OrderedSet and len(self.variables) > 0 \
            and all([(v.isupper() and len(v) == 1) or (v[0] == '❬' and v[-1] == '❭' and len(v) > 2) for v in self.variables])
        assert type(self.terminals) == OrderedSet and all([(t != '&') and (len(t) == 1) and not (t.isupper()) for t in self.terminals])
        assert type(self.rules) == dict and self.rules.keys() == self.variables and all([type(val) == OrderedSet for val in self.rules.values()])
        assert self.start in self.variables

    @staticmethod
    def validate_cfg_word(word: str) -> bool:
        if VERIFY_GRAMMAR:
            print("SPECS ALREADY ON")

    def has_e(self): # CONST
        """Tests if the grammar has &-rules that are not in the start symbol."""
        for v in self.variables:
            for prod in self.rules[v]:
                if v != self.start and prod == ("&",):
                    return True
        return False

    def has_cycle(self): # CONST
        # (A, B) is an edge iff A => B is a rule
        edges = {var: OrderedSet() for var in self.variables}
        for head in self.rules.keys(): # FIXME: Tem var sem entrada em rules?
            for body in self.rules[head]:
                if len(body) == 1 and body[0] in self.variables:
                    edges[head].add(body[0])

        graph = Graph(self.variables, edges)

        # Check if some V appears in B = > V, where B was visited by bfs(V)
        for var in self.variables:
            visited = graph.bfs(var)
            for contender in self.variables:
                if visited[contender]:
                    for prod in self.rules[contender]:
                        if prod == (var,):
                            return True
        return False

    def remove_left_recursion(self): # NOT CONST
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
            raise RuntimeError("A grammar must be &-free in order to remove left recursions.")

        if self.has_cycle():
            raise RuntimeError("A grammar must be cycle-free in order to remove left recursions.")

        # Remove indirect
        for i in range(len(self.variables)): # FIXME: now over var insead of rules.keys()?
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
        self.CHECK_GRAMMAR()

    def remove_unit(self): # NOT CONST
        """
        Post-conditions: may return variable with no production

        Note:
        In this algorithm cyclic productions will be eliminated.
        A -> B                          A ->
        B -> C         -------->        B ->
        C -> A                          C ->

        Our algorithm takes care of cyclic productions
        """
        def not_unit(production):
            return len(production) > 1 or production[0] not in self.variables

        # (A, B) is an edge iff A => B is a rule
        edges = {var:OrderedSet() for var in self.variables}
        for head in self.rules.keys(): # FIXME: same trouble as before
            for body in self.rules[head]:
                if len(body) == 1 and body[0] in self.variables:
                    edges[head].add(body[0])

        graph = Graph(self.variables, edges)

        # Expand all reacheable unit productions
        # NOTE: Each variable visits itself in bfs
        new_rules = {var:OrderedSet() for var in self.variables}
        for var in self.variables:
            visited = graph.bfs(var)
            for contender in self.variables:
                if visited[contender]:
                    for prod in self.rules[contender]:
                        if not_unit(prod):
                            new_rules[var].add(prod)
        self.rules = new_rules
        self.CHECK_GRAMMAR()

    def remove_epsilon(self): # NOT CONST
        def power_set(i, cuts):
            """Return the all possible cuts obtained by striking out a subset
               of the nullable variables in the given production.
            """
            if i == len(cuts[0]):
                new_ps = OrderedSet()
                for c in cuts:
                    new_c = tuple()
                    for c2 in c:
                        if c2 != "ε":
                            new_c += (c2,)
                    if len(new_c) > 0:
                        new_ps.add(new_c)
                return new_ps

            if cuts[0][i] in nullables:
                to_add = OrderedSet()
                for s in cuts:
                    to_add.add(s[:i] + ("ε",) + s[i+1:])
                cuts.update(to_add)
            return power_set(i+1, cuts)

        nullables = OrderedSet()
        nullables.add("&")

        # Find nullables through Hopcroft's algorithm
        changed = True
        while changed:
            changed = False
            for var, prods in self.rules.items():
                for prod in prods:
                    if all([p in nullables for p in prod]) and var not in nullables:
                        nullables.add(var)
                        changed = True

        # Strike out nullables
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
        self.CHECK_GRAMMAR()

    def remove_unproductives(self): # NOT CONST
        """
        Notes
        -----
            If the grammar generates no words (empty language), then the grammar returned will be
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

        # if empty language S -> S
        if self.start not in self.rules.keys():
            self.variables = OrderedSet()
            self.rules = dict()
            self.variables.add(self.start)
            self.rules[self.start] = OrderedSet()
            self.rules[self.start].add(self.start)
        self.CHECK_GRAMMAR()

    def remove_unreachables(self): # NOT CONST
        """
        Pre_conditions: None
        """
        # (A, B) is an edge iff A => alfa and B is in alfa
        # NOTE: doesn't take care of terminals
        edges = {var:OrderedSet() for var in self.variables}
        for head in self.rules.keys(): # FIXME: Same
            for body in self.rules[head]:
                for symbol in body:
                    if symbol in self.variables:
                        edges[head].add(symbol)

        graph = Graph(self.variables, edges)

        # Remove both the variables that were not visited and their rules
        new_rules = {var:OrderedSet() for var in self.variables}
        visited = graph.bfs(self.start)
        for rem in OrderedSet( [v for v in self.variables if not visited[v]] ):
            del self.rules[rem]
            self.variables.discard(rem)
        self.CHECK_GRAMMAR()

    def replace_terminals(self): # NOT CONST, nao li ainda
        """
        Pre_conditions: None
        """
        new_v_id = 0

        # var_to_terminal checks if variable already exists or if variable has already been created
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
                if (len(old_prod) >= 2):
                    for i in range(len(old_prod)):
                        symbol = old_prod[i]
                        if symbol in self.terminals:
                            new_v = var_to_terminal(symbol)
                            if new_v is None:
                                new_v = create_new_v(symbol)
                            for j in range(i, len(old_prod)):
                                if old_prod[j] == symbol:
                                    old_prod[j] = new_v
                to_add.add(tuple(old_prod))
            new_rules[v] = to_add

        self.rules = new_rules
        for v in to_add_var:
            self.variables.add(v)
        self.CHECK_GRAMMAR()

    def reduce_size(self): # NOT CONST, nao li ainda
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
        self.CHECK_GRAMMAR()

    def convert_to_cnf(self): # NOT CONST
        self.remove_epsilon()
        self.remove_unit()
        self.remove_unproductives()
        self.remove_unreachables()
        self.replace_terminals()
        self.reduce_size()

    def has_left_recursion(self): # CONST
        # (A, B) is an edge iff A => B𝛼 is a rule in rules
        edges = {v:OrderedSet() for v in self.variables}
        for v in self.variables:
            for prod in self.rules[v]:
                if prod[0] in self.variables:
                    edges[v].add(prod[0])

        graph = Graph(self.variables, edges)
        return any([graph.has_loop(v) for v in self.variables])

    def firsts(self): # CONST
        """
        Exceptions
        --------------
            1. The grammar has left recursion.
        """
        def first_var(v):
            """Calculate the first of a variable using Dynamic Programming."""
            if len(first[v]) != 0:
                return first[v]

            for prod in self.rules[v]:
                for p in prod:
                    to_add = first_var(p)
                    first[v].update(to_add)
                    # Stop when Xi doesn't have epsilon in its first
                    if "&" not in to_add:
                        first[v].discard("&")
                        break
            return first[v]

        if self.has_left_recursion():
            raise RuntimeError("A grammar can't contain left recursion in ordered to calculate FIRSTS.")

        first = {t:OrderedSet([t]) for t in OrderedSet(['&']) | self.terminals}
        first.update({v:OrderedSet() for v in self.variables})

        for v in self.variables:
            first_var(v)
        return first

    def first_body(self, body, first=None): # CONST
        """Calculate the first of a syntactical form."""
        lb = len(body)
        if first is None:
            first = self.firsts()

        total = OrderedSet()
        for body in body:
            to_add = first[body]
            total.update(to_add)
            if "&" not in to_add:
                total.discard("&")
                break
        return total

    def follows(self): # CONST
        """Compute the follows."""
        first = self.firsts()
        follow = {v:OrderedSet() for v in self.variables}

        follow[self.start].add("$")
        add = True
        while(add):
            add = False
            for head, bodies in self.rules.items():
                for body in bodies:
                    # Add FIRSTS
                    lb = len(body)
                    for i in range(lb-1):
                        if body[i] in self.variables:
                            to_add = self.first_body(body[i+1:], first)
                            to_add.discard("&")
                            if not (to_add <= follow[body[i]]):
                                add = True
                                follow[body[i]].update(to_add)
                    # Add FOLLOWS
                    to_add = follow[head]
                    to_add.discard("&")
                    for i in range(lb-1, -1, -1):
                        if body[i] in self.variables:
                            if not to_add.issubset(follow[body[i]]):
                                add = True
                                follow[body[i]].update(to_add)
                            if "&" not in first[body[i]]:
                                break
                        else:
                            break
        return follow

    def make_LL1_table(self) -> dict(): # CONST
        """Compute LL(1) parsing table.

        Pre-conditions
        --------------
            1. The grammar does not have left recursion.

        Exceptions
        --------------
            1. The grammar has Fi/Fi or Fi/Fo conflict.
        """
        firsts = self.firsts()
        follows = self.follows()
        table = dict()

        for v in self.variables:
            for alpha in self.rules[v]:
                first_alpha = self.first_body(alpha, firsts)
                # If alpha = &, then skip the loop
                for f in first_alpha - {'&'}:
                    if (v, f) in table.keys():
                        raise RuntimeError("First/First conflict at {}".format((v, f)))
                    else:
                        table[(v, f)] = alpha
                if "&" in first_alpha:
                    for f in follows[v]:
                        if (v, f) in table.keys():
                            raise RuntimeError("First/Follow conflict at {}".format(v, f))
                        else:
                            table[(v, f)] = alpha
        return table

    def make_LL1_parser(self) -> PredictiveParser: # CONST
        """Build LL(1) Predictive Parser for this grammar."""
        return PredictiveParser(self.make_LL1_table())

    def left_factoring(self): # NOT CONST
        """
        Exceptions
        --------------
            1. self has left recursion.
        """

        if self.has_left_recursion():
            raise RuntimeError("A grammar can't have left recursion in ordered to be factored")

        cached_first = self.firsts()
        firsts_v = dict()
        new_var_id = 0

        def sub_var(prod):
            to_add = OrderedSet()
            for prod_var in self.rules[prod[0]]:
                if prod_var == ("&",):
                    if len(prod[1:]) == 0:
                        to_add.add(("&", ))
                    else:
                        to_add.add(prod[1:])
                else:
                    to_add.add(prod_var+prod[1:])
            return to_add

        def substitute_ndet_var(ndet_term):
            anyV = True
            while(anyV):
                anyV = False
                new_rules_v = OrderedSet()
                to_add = OrderedSet()
                for prod in self.rules[v]:
                    if prod[0] in self.variables and ndet_term in self.first_body(prod): # NOTE: CANT CACHE
                        to_add.update(sub_var(prod))
                        anyV = True
                    else:
                        to_add.add(prod)
                self.rules[v] = to_add

        def get_largest_common_prefix_2(str1, str2):
            if len(str1) > len(str2):
                str_t = str2
                str2 = str1
                str1 = str_t
            l1 = len(str1)
            for i in range(l1):
                if str1[i] != str2[i]:
                    return str1[:i]
            return str1

        def get_largest_common_prefix():
            for prod in self.rules[v]:
                if prod[0] == ndet_term:
                    lcp = prod
                    break

            for prod in self.rules[v]:
                if prod[0] == ndet_term:
                    lcp = get_largest_common_prefix_2(lcp, prod)
            # print("lcp::{}".format(lcp))
            return lcp

        def create_new_var_lcp(lcp):
            nonlocal new_var_id
            new_rules_old_v = OrderedSet()
            new_var_id = new_var_id+ 1
            if len(v) == 1:
                new_var = "❬{},{}❭".format(v, new_var_id)
            else:
                new_var = "❬{},{}❭".format(v[1], new_var_id)
            self.rules[new_var] = OrderedSet()
            self.variables.add(new_var)

            ll = len(lcp)
            new_rules_old_v.add(lcp+(new_var,))
            for prod in self.rules[v]:
                if prod[0] == ndet_term:
                    if len(prod[ll:]) != 0:
                        self.rules[new_var].add(prod[ll:])
                    else:
                        self.rules[new_var].add(("&",))
                else:
                    new_rules_old_v.add(prod)

            self.rules[v] = new_rules_old_v

        def first_follow():
            new_rules_old_v = OrderedSet()
            to_disc = None
            for prod in self.rules[v]:
                lp = len(prod)
                for i in range(lp-1):
                    intersection = self.firsts()[prod[i]] & self.first_body(prod[i+1:])
                    intersection.discard("&")
                    if "&" in self.firsts()[prod[i]] and len(intersection) != 0:
                        to_disc = prod
                        print("prod==={}".format(prod))
                        for prod_sub in self.rules[prod[i]]:
                            if prod_sub == ("&", ):
                                new_rules_old_v.add(prod[:i]+prod[i+1:])
                            else:
                                new_rules_old_v.add(prod[:i]+prod_sub+prod[i+1:])
                        print(new_rules_old_v)
                        print("\n\n\n===================================\n\n\n")
                        break
                if not to_disc is None:
                    break
            self.rules[v].discard(to_disc)
            self.rules[v].update(new_rules_old_v)
            # print()
            if not to_disc is None:
                return True
            return False

        def first_first():
            nonlocal ndet_term
            for prod in self.rules[v]: #choose ndet_term
                # print(prod)
                firsts_v[prod] = self.first_body(prod)
                # print(firsts_v[prod])

                for ter in firsts_v[prod]:
                    if ter != "&":
                        if ter in total and ndet_term is None:
                            print("ndet_ter")
                            print(ter)
                            ndet_term = ter
                    total.add(ter)

            if not ndet_term is None:
                # print("SUb")
                anynd = True
                print("\n\nGRAMMAR Normal")
                print(self)
                # indirect
                substitute_ndet_var(ndet_term)
                print("\n\nGRAMMAR Ind")
                print(self)
                # direct
                lcp = get_largest_common_prefix()
                create_new_var_lcp(lcp)
                print("\n\nGRAMMAR Dir")
                print(self)
                return True
            return False

        for i in range(20):
            anynd = False

            for v in self.variables:
                firsts_v.clear()
                ndet_term = None
                total = OrderedSet()

                fi_fo = first_follow()
                if fi_fo:
                    anynd = True
                    break

                fi_fi = first_first()
                if fi_fi:
                    anynd = True
                    break

            if not anynd:
                print("Finished in {} step(s)".format(i))
                return True
        self.CHECK_GRAMMAR()
        return False

VERIFY_GRAMMAR = False
SPEC_GRAMMAR = ContextFreeGrammar("spec.cfg")
SPEC_PARSER = SPEC_GRAMMAR.make_LL1_parser()
print(SPEC_PARSER)
VERIFY_GRAMMAR = True
