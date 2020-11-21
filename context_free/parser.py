"""This module provides parsers implementations. """


class PredictiveParser:
    def __init__(self, table: dict):
        # FIXME: pre-conds
        self.table = table

    def parse(string: str) -> bool:
        """
        Pre-conditions
        --------------
            1.
        """
        stack = ["$"]
        for s in string:
            if stack[-1] == s:
                if s == "$":
                    assert len(stack) == 1
                    return True
                else:
                    stack.pop()
                    continue
            else: # expand terminal
                state = (stack[-1], s)
                if state not in table.keys(): # No action from this state
                    return False
                else:
                    action = table[(stack[-1], s)]
                    for c in reversed(action):
                        stack.append(c)
