#!/usr/bin/env python3
"""convert.py

This program takes a spreadsheet in .ods format containing linguistic
information on the N|uu language (collected through field work).  It
validates the input and converts it into an output that can be used as
the input for the dictionary portal and dictionary app.  It can als generate
output (in LaTeX format) for the physical dictionary.
"""

import argparse
from dictionary import Dictionary
import logging
from pandas_ods_reader import read_ods


from itertools import chain

def read_input(filename):
    """Read input .ods file found at filename. Internalize in a Dictionary
    object.
    """
    logging.debug("Reading in file " + filename)
    data = Dictionary() 
    spreadsheet = read_ods(filename , 1)
    for index, row in spreadsheet.iterrows():
        try:
            data.insert_line(row, index + 2) # 2 is header and offset
        except ValueError:
            logging.error("Missing N|uu information on line " + str(index + 2))
    return data


def write_output(base, data):
    """The data is written to the output file (filename) in the format
    that can be used as input to the dictionary portal and dictionary
    app.
    """
    logging.debug("Writing app output to " + base + ".txt")
    data.write_portal(base + ".txt")
    logging.debug("Writing app output to " + base + ".tex")
    data.write_latex(base + ".tex")


def main():
    """Commandline arguments are parsed and handled.  Next, the input
    is read from the input filename.  Validation of the data is
    performed.  Next, the data is converted into the format usable for
    the dictionary portal and dictionary app.  Finally, the data is
    written to output files.  The argument provides the base of the output files
    and the system generates a .txt containing the dictionary portal/app format.
    """

    parser = argparse.ArgumentParser(description="This program converts the N|uu spreadsheet into a format that can be used as input for the dictionary portal.  It also checks the input on several aspects.  It generates output files (.txt) based on the output argument.")
    parser.add_argument("-i", "--input",
            help = "name of ods spreadsheet file",
            action = "store",
            metavar = "FILE")
    parser.add_argument("-o", "--output",
            help = "name of output base filename",
            action = "store",
            metavar = "FILE BASE")
    parser.add_argument("-l", "--log",
            help = "name of logging filename",
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

    if args.log:
        logging.basicConfig(filename = args.log, filemode='w', format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt = '%H:%M:%S', level = args.loglevel)
    else:
        logging.basicConfig(level = args.loglevel)

    # Perform checks on arguments
    if args.input == None:
        parser.error("An input filename is required.")
    if args.output == None:
        parser.error("An output base filename is required.")

    # Handle the data
    data = read_input(args.input)
    write_output(args.output, data)


if __name__ == '__main__':
    main()
