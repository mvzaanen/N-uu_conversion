#!/usr/bin/env python3
"""convert.py

This program takes a spreadsheet in .ods format containing linguistic
information on the N|uu language (collected through field work).  It
validates the input and converts it into an output that can be used as
the input for the dictionary portal and dictionary app.
"""

import argparse
import logging
from pandas_ods_reader import read_ods
import re

# fields contains the fields from the spreadsheet the conversion
# script is using to create the output.
# "Orthography 1" contains the orthography of an entry, "IPA" contains
# the IPA representation, "English" contains the English translation,
# and "Afrikaans" contains the Afrikaans translation.
fields = ("Orthography 1", "IPA", "English", "Afrikaans")

def read_input(filename):
    """Read input .ods file found at filename. Return the input as is.
    """
    logging.debug("Reading in file " + filename)
    df = read_ods(filename , 1)
    return df

def is_empty(data, i):
    """is_empty checks whether the important fields (defined by
    fields) are empty. If so, it returns True, False otherwise.  It
    provides warnings on logging.warning for all fields.
    """
    status = False
    for field in fields:
        if data[field][i] == None:
        logging.warning(field + " is empty on row " + str(i + 2))
        status = True
    return status

def internalize(data):
    """Validate the data coming from the spreadsheet and store in an
    internal format.
    Different validations are performed and information
    is written on logging.WARNING.  The data itself is stored in a
    dictionary.
    """
    logging.debug("Internalize data")
    for i in range(0, len(data)):
        if is_empty(data, i):
            None

def convert(data):
    """Convert the data from .ods format into a format that can be
    used as input to the dictionary portal or dictionary app.
    """
    logging.debug("Convert data")
    return data

def write_output(filename, data):
    """The data is written to the output file (filename) in the format
    that can be used as input to the dictionary portal and dictionary
    app.
    """
    logging.debug("Writing output to " + filename)


def main():
    """Commandline arguments are parsed and handled.  Next, the input
    is read from the input filename.  Validation of the data is
    performed.  Next, the data is converted into the format usable for
    the dictionary portal and dictionary app.  Finally, the data is
    written to an output file.
    """

    parser = argparse.ArgumentParser(description="This program converts the N|uu spreadsheet into a format that can be used as input for the dictionary portal.  It also checks the input on several aspects.")
    parser.add_argument("-i", "--input",
        help = "name of ods spreadsheet file",
        action = "store",
        metavar = "FILE")
    parser.add_argument("-o", "--output",
        help = "name of output file",
        action = "store",
        metavar = "FILE")
    parser.add_argument("-d", "--debug",
        help = "provide debugging information",
        action = "store_const",
        dest = "loglevel",
        const = logging.DEBUG,
        default = logging.WARNING,
)
    args = parser.parse_args()

    logging.basicConfig(level = args.loglevel)

    # Perform checks on arguments
    if args.input == None:
        parser.error("An input filename is required.")
    if args.output == None:
        parser.error("An output filename is required.")

    # Handle the data
    data = read_input(args.input)
    internal = internalize(data)
    clean_data = convert(internal)
    write_output(args.output, clean_data)


if __name__ == '__main__':
    main()
