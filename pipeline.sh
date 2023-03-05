#!/bin/bash
# Preprocess a Dutch text: convert, clean, tokenize
#
# bash pipeline.sh <FILENAME> <TOKENLIMIT>
# Example: bash pipeline.sh 18066-h.htm 2000
#
# <FILENAME> a file in a format recognized by Calibre (e.g, epub, html, ...)
# <TOKENLIMT> the maximum number of tokens (rounded up to nearest sentence boundary)
#
# Writes output in the following subdirectories:
# converted, cleaned, tokenized, tokenized-first$2tokens
set -e

# Strip path and last extension
NAME="$(basename "${1%.*}")"

mkdir -p output/converted output/cleaned output/tokenized output/tokenized-first$2tokens
ebook-convert "$1" "output/converted/$NAME.txt"
python3 preproc.py "output/converted/$NAME.txt" "output/cleaned/$NAME.txt"
$ALPINO_HOME/Tokenization/add_key < "output/cleaned/$NAME.txt" \
        | $ALPINO_HOME/Tokenization/tokenize.sh \
        | $ALPINO_HOME/Tokenization/number_sents \
		> "output/tokenized/$NAME.tok"
python3 firstntokens.py \
	$2 \
	"output/tokenized/$NAME.tok" \
	"output/tokenized-first$2tokens/$NAME.tok"
