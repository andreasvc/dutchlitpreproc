# Dutch Literature Pipeline

Preprocessing pipeline for Dutch literature and other texts:
convert, clean, tokenize, truncate, and normalize spelling.

## Requirements

Python packages:

    $ pip install -r requirements.txt

Other requirements:

- Calibre: `$ apt-get install calibre`
- Alpino: https://www.let.rug.nl/vannoord/alp/Alpino/

  Alpino should be installed and available in `$ALPINO_HOME`
- Spelling normalization script:
  `$ git clone https://github.com/gertjanvannoord/oudeboeken.git`
  (clone next to this repository)
- GNU Make

## Usage

    $ bash pipeline.sh <FILENAME> <TOKENLIMIT>
    
    <FILENAME> a file in a format recognized by Calibre (e.g, epub, html, ...)
    <TOKENLIMT> truncate to this number of tokens (rounded up to next sentence boundary)

Writes output in the following subdirectories in `output/`:
`converted`, `cleaned`, `tokenized`, `tokenized-first$2tokens`,
and `spelling`.

Front and back matter from Project Gutenberg is automatically removed.
Line numbers for front and back matter can also be specified manually
in a .csv file. To generate such a .csv file, run:

    $ python3 genpara.py 'converted/*/*.txt'

This generates `output/paratext-uncorrected.csv`. Rename this file to
`output/paratext-corrected.csv`, and edit this file so that the line numbers in
columns "start" and "end" (1-based, inclusive interval) refer to the text that
should be kept for each filename in column "Label" (without path or extension).
Re-run the pipeline. Front and back matter will be stripped before cleaning and
written to `output/paratext/`.

## Example

Project Gutenberg text with ID 18066

    $ wget http://www.gutenberg.lib.md.us/1/8/0/6/18066/18066-h/18066-h.htm
    $ bash pipeline.sh 18066-h.htm 2000

## Other scripts

See `Makefile` for some other scripts that are useful for diagnostic purposes.
