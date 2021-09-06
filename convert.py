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


def read_input(filename):
    """Read input .ods file found at filename. Return the input as is.
    """
    logging.debug("Reading in file " + filename)
    df = read_ods(filename , 1)
    return df

def validate(data):
    """Validate the data coming from the spreadsheet.  The format is
    as follows: @@@.  Different validations are performed and
    information is written on logging.WARNING.  The data itself is not
    changed, only validated.
    """
    logging.debug("Validating data")
    for i in range(0, len(data)):
        if data["Orthography 1"][i] == None:
            logging.warning("Orthography 1 is empty on row " + str(i + 2))

        if data["Green Orthography"][i] == None:
            logging.warning("Green Orthography is empty on row " + str(i + 2))

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

    if args.input == None:
        parser.error("An input filename is required.")
    data = read_input(args.input)

    validate(data)

    clean_data = convert(data)

    if args.output == None:
        parser.error("An output filename is required.")
    write_output(args.output, clean_data)


if __name__ == '__main__':
    main()
