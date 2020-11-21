"""This module provides Read/Write utilities for .cfg files."""
import os

from context_free.grammar import ContextFreeGrammar, OrderedSet

CFGS_DIR = os.path.join(os.path.dirname(__file__), '../cfgs')

def read_grammar(filename: str) -> ContextFreeGrammar:
    filepath = os.path.join(CFGS_DIR, filename)

    with open(filepath, 'r') as f:
        # FIXME: Syntax Analysis
        lines = f.read().split("\n")

        variables = OrderedSet()
        terminals = OrderedSet()
        rules = dict()
        start = None
        _prods = ""

        # Assumed to be a valid .cfg file (See grammar.bnf)
        for line in lines:
            if line == lines[-1]:
                assert len(line) == 0
                continue

            items = line.split()
            var = items[0]
            rules[var] = OrderedSet()
            variables.add(var)

            # First iteration
            if start is None:
                start = var

            i = 2
            while i < len(items):
                syntactic_form = items[i]
                rules[var].add(syntactic_form)
                _prods += syntactic_form
                i += 2

        # Add terminals and dead variables
        i = 0
        while i < len(_prods):
            c = _prods[i]
            if c == '❬': # brackets-variable
                j = i + 1
                while _prods[j] != '❭':
                    j += 1

                assert len(_prods[i:j+1]) > 3

                variables.append(_prods[i:j+1])

                i = j + 1
            else: # Upper-case or terminal
                if c.isupper():
                    variables.add(c)
                else:
                    terminals.add(c)
                i += 1
        return ContextFreeGrammar(variables, terminals, rules, start)


def write_grammar(grammar: ContextFreeGrammar, filename: str):
    filepath = os.path.join(CFGS_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(str(grammar))
