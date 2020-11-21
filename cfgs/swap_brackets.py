"""Swap <> for ❬❭"""
import sys


if __name__ == '__main__':
    assert len(sys.argv) == 2, "Incorrect number of parameters"
    assert sys.argv[1][-4:] == '.cfg', "Incorrect extension"
    transformed = None
    with open(sys.argv[1], 'r') as f:
        raw = f.read()
        transformed = raw.replace('<', '\u276c')
        transformed = transformed.replace('>', '\u276d')
    with open(sys.argv[1], 'w') as f:
        f.write(transformed)
