# -*- coding: UTF-8 -*-
"""Generic text cleaning script.

Writes one paragraph per line, and normalizes punctuation & whitespace.
No sentence or word tokenization. Aborts with non-zero exit code on error.

Usage: preproc.py <INFILE> <OUTFILE>

If "output/paratext-corrected.csv" exists, it is used to remove front and
back matter. This file should contain line numbers of core text of each text in
columns "start" and "end" (1-based, inclusive interval);
filenames in column "Label" (without path); front and back matter will
be stripped before cleaning and written to `../paratext/` (relative to input).
"""
import io
import os
import sys
import unicodedata
from getopt import gnu_getopt, GetoptError
import pandas as pd
try:
	import re2 as re
except ImportError:
	import re

LIGATURES = {
        'ﬁ': 'fi',
        'ﬀ': 'ff',
        'ﬂ': 'fl',
        'ﬃ': 'ffi',
        'ﬄ': 'ffl',
        'Ĳ': 'IJ',
        'ĳ': 'ij',
        'Æ': 'AE',
        'æ': 'ae',
        }

def readtext(fname):
	"""Read UTF-8 encoded text file, return NFC-normalized unicode string."""
	with open(fname, 'rt', encoding='utf8') as inp:
		text = inp.read()
	text = unicodedata.normalize('NFC', text)
	return text


def stripparatext(filename, text, paratext):
	"""Strip front and back matter using given table of line numbers.

	Front and back matter is written to separate directory,
	remaining core text is returned for further processing."""
	# NB: text.splitlines() gives wrong results
	lines = io.StringIO(text).readlines()
	label = os.path.splitext(os.path.basename(filename))[0]
	start, end = paratext[label]
	front, core, back = lines[:start], lines[start:end + 1], lines[end + 1:]

	outpath = os.path.splitext(
			filename.replace('/converted/', '/paratext/'))[0]  # HACK
	os.makedirs(os.path.dirname(outpath), exist_ok=True)
	with open(outpath + '_1_front.txt', 'w', encoding='utf8') as out:
		out.writelines(front)
	with open(outpath + '_2_back.txt', 'w', encoding='utf8') as out:
		out.writelines(back)
	return ''.join(core)


def clean(text):
	"""Return cleaned copy of `text`."""
	# get rid of carriage returns, keep line feeds
	if '\n' in text:
		text = re.sub('\r', '', text)
	else:
		text = re.sub('\r', '\n', text)

	# normalize unicode ligatures to ascii
	text = expandligatures(text)

	# remove hidden unicode characters; normalize unicode punctuation to ascii
	text = simplifyunicodespacepunct(text)

	# normalize dashes (but not single hyphens)
	text = re.sub('--+', ' - ', text)

	# replace square brackets because Alpino uses them for bracketed input
	# FIXME: could also escape brackets \[ \]
	text = text.replace('[', '(').replace(']', ')')

	# remove separators, empty lines
	text = re.sub(r'\n[ \t]*(==+|\*+|\*(?: \*)*|~|\.\.|)[ \t]*(?=\n)',
			'\n', text)

	# normalize whitespace
	# no leading or trailling whitespace;
	# collapse spaces and tabs to single space
	text = re.sub('\n[ \t]+', '\n', text.strip())
	text = re.sub('[ \t]+\n', '\n', text)
	text = re.sub('[ \t]+', ' ', text)

	# one paragraph per line
	text = re.sub('\n\n+', '\n', text)

	return text


def expandligatures(text):
	"""Expand single unicode ligatures into multiple ascii characters.

	>>> expandligatures('ﬁlosoof')
	'filosoof'
	"""
	return re.sub('[%s]' % ''.join(LIGATURES),
			lambda x: LIGATURES[x.group()], text)


def simplifyunicodespacepunct(text):
	"""Turn various unicode whitespace and punctuation characters into simple
	ASCII equivalents where appropriate, and discard control characters.

	NB: this discards some information (e.g., left vs right quotes, dash vs
	hyphens), but given that such information is not consistently encoded
	across languages and texts, it is more reliable to normalize to a common
	denominator.

	>>> simplifyunicodespacepunct('‘De verraders’, riep de sjah.')
	"'De verraders', riep de sjah."
	"""
	# Some exotic control codes not handled:
	# U+0085    NEL: Next Line
	# U+2028        LINE SEPARATOR
	# U+2029        PARAGRAPH SEPARATOR

	# Normalize spaces
	# U+00A0 NO-BREAK SPACE
	# U+2000 EN QUAD
	# U+2001 EM QUAD
	# U+2002 EN SPACE
	# U+2003 EM SPACE
	# U+2004 THREE-PER-EM SPACE
	# U+2005 FOUR-PER-EM SPACE
	# U+2006 SIX-PER-EM SPACE
	# U+2007 FIGURE SPACE
	# U+2008 PUNCTUATION SPACE
	# U+2009 THIN SPACE
	# U+200A HAIR SPACE
	# U+202F NARROW NO-BREAK SPACE
	text = re.sub('[\u00a0\u2000-\u200a\u202f]', ' ', text)

	# remove discretionary hyphen, soft space
	# special case: treat soft hyphen at end of line as a regular hyphen,
	# to ensure that it will be dehyphenated properly.
	text = re.sub('\u00ad+\n', '-\n', text)
	#      8 BACKSPACE
	# U+00AD SOFT HYPHEN
	# U+200B ZERO WIDTH SPACE
	# U+2027 HYPHENATION POINT
	text = re.sub('[\b\u00ad\u200b\u2027]', '', text)

	# hyphens
	# U+00B7 MIDDLE DOT
	# U+2010 HYPHEN
	# U+2011 NON-BREAKING HYPHEN
	# U+2212 MINUS SIGN
	text = re.sub('[\u00b7\u2010\u2011\u2212]', '-', text)
	# dashes/bullet points
	# U+2012 FIGURE DASH
	# U+2013 EN DASH
	# U+2014 EM DASH
	# U+2015 HORIZONTAL BAR
	# U+2022 BULLET
	# U+2043 HYPHEN BULLET
	text = re.sub('[\u2012-\u2015\u2022\u2043]', ' - ', text)

	# U+2044 FRACTION SLASH
	# U+2215 DIVISION SLASH
	text = text.replace('[\u2044\u2215]', '/')  # e.g., 'he/she'

	# single quotes:
	# U+2018 left single quotation mark
	# U+2019 right single quotation mark
	# U+201A single low-9 quotation mark
	# U+201B single high-reversed-9 quotation mark
	# U+2039 single left-pointing angle quotation mark
	# U+203A single right-pointing angle quotation mark
	# U+02BC modifier letter apostrophe
	text = re.sub('[\u2018-\u201b\u2039\u203a\u02bc]', "'", text)

	# double quotes:
	# U+201C left double quotation mark
	# U+201D right double quotation mark
	# U+201E double low-9 quotation mark
	# U+201F double high-reversed-9 quotation mark
	# U+00AB left-pointing double angle quotation mark
	# U+00BB right-pointing double angle quotation mark
	text = re.sub("[\u201c-\u201f\u00ab\u00bb]|''", '"', text)

	# ellipsis
	text = text.replace('…', '...')

	return text


def main():
	"""Read filename specified as first argument and write to filename
	specified as second argument."""
	try:
		opts, args = gnu_getopt(
				sys.argv[1:],
				'h',
				('help'))
		fname, outfname = args
	except (GetoptError, ValueError) as err:
		print('error:', err)
		print(__doc__)
		sys.exit(2)
	opts = dict(opts)
	print('%s: %s' % (os.path.basename(__file__), fname))
	if '--help' in opts:
		print(__doc__)
		return
	if os.path.exists('output/paratext-corrected.csv'):
		# line numbers of front and back matter
		paratext = pd.read_csv(
				'output/paratext-corrected.csv', index_col='Label')
		paratext = paratext[~paratext['start'].isnull()]
		if paratext.index.has_duplicates:
			raise ValueError('%r has duplicate filenames' % opts['--paratext'])
		if not all(isinstance(a, int) and a > 0
				for col in (paratext.start, paratext.end)
					for a in col):
			raise ValueError('%r has non-integer linenos or linenos <= 0'
					% opts['--paratext'])
		paratext = {a.Index: (a.start - 1, a.end - 1)
				for a in paratext.itertuples()}
	else:
		paratext = None
	text = readtext(fname)
	if paratext is not None:
		text = stripparatext(fname, text, paratext)
	# FIXME: better way to detect gutenberg texts
	if re.search('project gutenberg', text[:1000],
			flags=re.IGNORECASE) is not None:
		import gutenbergpy.textget
		stripped = gutenbergpy.textget.strip_headers(text.encode('utf8'))
		text = stripped.decode('utf8')
	cleaned = clean(text)
	with open(outfname, 'wt', encoding='utf8') as out:
		out.write(cleaned)


if __name__ == '__main__':
	main()
