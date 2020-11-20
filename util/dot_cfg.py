"""This module provides Read/Write utilities for .cfg files."""
import os

from context_free.grammar import ContextFreeGrammar

CFGS_DIR = os.path.join(os.path.dirname(__file__), '../cfgs')

def write_grammar(grammar: ContextFreeGrammar, filename: str):
    filepath = os.path.join(CFGS_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(str(grammar))
