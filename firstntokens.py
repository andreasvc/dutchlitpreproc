"""Write lines from stdin until specified number of tokens is reached.

Usage: python3 firstntokens.py 1000 input.tok output.tok

Assumes input with one sentence per line of space-separated tokens."""
import sys

def firstntokens(maxn, fname, outfname):
	"""Write lines from ``fname`` to ``outfname`` until ``maxn`` tokens is
	reached."""
	n = 0
	with open(fname, encoding='utf8') as inp:
		with open(outfname, 'wt', encoding='utf8') as out:
			for line in inp:
				print(line, end='', file=out)
				n += len(line.split())
				if n > maxn:
					break


def main():
	"""CLI."""
	try:
		_, maxn, fname, outfname = sys.argv
		maxn = int(maxn)
	except ValueError:
		print(__doc__)
	else:
		firstntokens(maxn, fname, outfname)


if __name__ == '__main__':
	main()
