PDF Compare
===========
A simply python script that will load two PDFs up and diff them out.  This allows you to visually determine differences between them in a semi-automated way.  It does this by turning each page into an image and comparing each pixel to create a image difference for each page.
The diffs are saved out to the specified output directory prefixed with a random string generated for the run and the page number.  The diffs take the maximum page count and size of both inputs, meaning if both PDFs have different page counts, the largest count will be used.
Diffs are saved as PNGs.  Diffs are comprised of two colors: Black and Red.  Black represents pixels that match between the PDF page.  Red represents pixels that do not match between the PDF page.  If one PDFs page count exceeds the other, all diffs from the rest of the pages will be entirely red.


Install Dependencies
------------
Install **poppler**
*macOs*
::
  brew install poppler

*Ubuntu*
Poppler may already be packaged with your distribution.
::
  apt-get install poppler-utils

Install via Pipenv
-------
Install **pipenv**:
::
   pip3 install --user pipenv

Install **pdf-compare**:
::
   pipenv install git+https://github.com/DalinSeivewright/pdf-compare.git#egg=pdf-compare

Install via pip3
----------------
Install **pdf-compare**:
::
   pip3 install git+https://github.com/DalinSeivewright/pdf-compare.git#egg=pdf-compare


Usage
-----
PDF Compare is run with:
::
   pdf-compare.py [options]

Options
-------
* **-i**, **--input**: Specifies the path to an input PDF.  Must be specified twice.
* **-o**, **--output**: Specifies the output directory to save the diffs.  Must exist.
* **-e**, **--exclude-matching**:  Specifies whether or not pages that are an exact match will be saved out.
* **-q**, **--quite**: Turns off all logging to command line.
* **-v**, **--verbose**: Enables different levels of logging verboseness.  Once turns on "Extra Info" mode.  Twice turns on "Debug" mode.
