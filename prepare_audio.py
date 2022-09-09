#!/usr/bin/env python3
"""audio.py

This program takes a spreadsheet in .ods format containing linguistic
information on the N|uu language (collected through field work).  It
checks the audio columns, identifies the correct wav files and copies
them to a specified audio directory.
"""

import argparse
import filecmp
import glob
import logging
import re
from pandas_ods_reader import read_ods

def read_input(filename):
    """Read input .ods file found at filename.  Return a list of
    entries that contain the information on the word and the
    recordings.
    """
    logging.debug("Reading in file " + filename)
    spreadsheet = read_ods(filename , 1)
    data = []
    for index, row in spreadsheet.iterrows():
        entry = {}
        entry["tw"] = row["Dictionary Recording (target word only)"]
        entry["tw in s"] = row["Recordings (target word in sentence)"]
        entry["word"] = row["Orthography 1"]
        data.append(entry)
    return data


def write_output(file, data, base, target):
    """For each word in the column "word" in data, this function
    searches the names of the audio files (in "tw") and globs 
    this filename in the base directory (recursively).  It then writes
    a bash copy function to the output.  The target is the target
    directory where the audio files should go.
    """
    logging.debug("Writing app output to " + file)
    output = open(file, "w")
    output.write("mkdir -p " + target + "\n")
    for i in data:
        if not i["tw"]:
            output.write("# " + i["word"] + " does not have dictionary recording\n")
        else:
            # handle target word (tw) audio
            output.write("# " + i["word"] + "\n")
            files = re.split("[ ;,]+", i["tw"])
            for f in files:
                if f == "--" or f == "":  # We can skip the -- or empty strings
                    break
                logging.debug("Handling " + f)
                if "." in f:
                    logging.error("Found period in " + f)
                locations_lc = glob.glob(base + "/**/" + f + ".wav", recursive = True)
                locations_uc = glob.glob(base + "/**/" + f + ".WAV", recursive = True)
                locations_nc = glob.glob(base + "/**/" + f, recursive = True)
                nr_files_lc = len(locations_lc)
                nr_files_uc = len(locations_uc)
                nr_files_nc = len(locations_nc)
                if nr_files_lc + nr_files_uc + nr_files_nc == 1:
                    output.write("cp \"")
                    if nr_files_lc == 1:
                        output.write(locations_lc[0])
                    elif nr_files_uc == 1:
                        output.write(locations_uc[0])
                    else:
                        output.write(locations_nc[0])
                    output.write("\" " + target + "/" + f + ".wav\n")
                elif nr_files_lc + nr_files_uc + nr_files_nc == 0:
                    logging.warning("Did not find " + f)
                    output.write("# Did not find " + f + "\n")
                else:
                    logging.warning("Found multiple " + f)
                    # Check for duplicates
                    locations = locations_lc + locations_uc + locations_nc
                    same = True
                    for i in range(len(locations)):
                        for j in range(i + 1, len(locations)):
                            same &= filecmp.cmp(locations[i], locations[j])
                    if same:
                        output.write("cp \"")
                        output.write(locations[0] + "\" ")
                        output.write(target + "/" + f + ".wav\n")
                    else:
                        logging.error("Found multiple different " + f)
                        output.write("# Found multiple different " + f + "\n")
    output.close()


def main():
    """Commandline arguments are parsed and handled.  Next, the input
    is read from the input filename.  Validation of the data is
    performed.  Next, the data is converted into the format usable for
    the dictionary portal and dictionary app.  Finally, the data is
    written to output files.  The argument provides the base of the output files
    and the system generates a .txt containing the dictionary portal/app format.
    """

    parser = argparse.ArgumentParser(description="This program checks the N|uu spreadsheet to identify audio files that are used. It provides a script that copies the used audio files.")
    parser.add_argument("-i", "--input",
            help = "name of ods spreadsheet file",
            action = "store",
            metavar = "FILE")
    parser.add_argument("-o", "--output",
            help = "name of output filename",
            action = "store",
            metavar = "FILE")
    parser.add_argument("-t", "--target",
            help = "target directory",
            action = "store",
            metavar = "DIR")
    parser.add_argument("-b", "--base",
            help = "name of directory that contains all audio files",
            action = "store",
            metavar = "FILE")
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
    if args.base == None:
        parser.error("A base directory is required.")
    if args.output == None:
        parser.error("An output filename is required.")
    if args.target == None:
        parser.error("A target directory is required.")

    # Handle the data
    data = read_input(args.input)
    write_output(args.output, data, args.base, args.target)


if __name__ == '__main__':
    main()
