"""This module provides parsers implementations. """
from oset.ordered_set import OrderedSet


class PredictiveParser:
    def __init__(self, table: dict):
        """
        Pre-conditions
        --------------
            1. table is a valid LL(1) table. That is, it has no conflicts and it's
               not left recursive.
        """
        self.variables = OrderedSet([e[0] for e in table.keys()])
        self.terminals = OrderedSet([e[1] for e in table.keys()]) # Contains $
        self.table = table

    def __str__(self):
        """Nicely formatted transition table."""
        def format_string(raw):
            """Format string to fit in cell."""
            return " {}".format(raw.ljust(col_size)[:col_size-1])
        col_size = 10

        # var | terminals (with &)
        columns = 1 + len(self.terminals)
        # there are columns+1 vertical separators (|)
        row_size = col_size * columns + columns + 1
        string = "=" * row_size
        string += "\n|{}|".format(format_string("Var \ Term"))

        for t in self.terminals:
            string += "{}|".format(format_string(t))

        for v in self.variables:
            # horizontal separator (-----)
            string += "\n|{}|".format("-" * (row_size - 2))
            string += "\n|{}|".format(format_string(v))

            for t in self.terminals:
                try:
                    string += "{}|".format(format_string(''.join(self.table[(v, t)])))
                except KeyError:
                    string += "{}|".format(format_string("None"))
        string += "\n{}".format("=" * row_size)
        return string


    def parse(self, string: str) -> bool:
        """
        Pre-conditions
        --------------
            1. string consists only of terminals.
        """
        string += "$"
        start = self.variables[0] # NOTE: variables is ordered
        stack = ["$", start]
        i = 0
        while i < len(string):
            s = string[i]
            # print("S={}, STACK={}".format(s, stack))
            if stack[-1] == s:
                # print("SHIFTING INPUT")
                if s == "$":
                    assert len(stack) == 1
                    return True
                else:
                    stack.pop()
                    i += 1
                    continue
            else: # expand variable
                state = (stack[-1], s)
                # print("EXPANDING STACK")
                if state not in self.table.keys(): # No action from this state
                    return False
                else:
                    action = self.table[(stack[-1], s)]
                    stack.pop()
                    if action != ("&",):
                        for c in reversed(action):
                            stack.append(c)
