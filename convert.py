#!/usr/bin/env python3
"""convert.py

This program takes a spreadsheet in .ods format containing linguistic
information on the N|uu language (collected through field work).  It
validates the input and converts it into an output that can be used as
the input for the dictionary portal and dictionary app.  It can als generate
output (in LaTeX format) for the physical dictionary.
"""

import argparse
from enum import Enum
import logging
from pandas_ods_reader import read_ods
import re


class Entry:
    """The Entry class contains information needed to create dictionary entries.  These can be printed in the form useful for the dictionary portal and dictionary app as well as in LaTeX form.
    """

    def __init__(self, n_uu, n_uu_east, n_uu_west, ipa, ipa_east, ipa_west,
            english, afrikaans, khoekhoegowab, line_nr):
        """An Entry needs to be introduced using the fields that are required
        for output.  Note that a least one of n_uu, n_uu_east, n_uu_west needs
        to be filled (otherwise an exception is raised).  If none of ipa,
        ipa_east, ipa_west is filled, a warning is written on the logging
        channel, similarly if english, afrikaans, or khoekhoegowab (or any
        combination) are not filled.  Line_nr is the line the entry is found in.
        """
        # Check whether the n_uu information is present.
        if n_uu == None and n_uu_east == None and n_uu_west == None:
            raise ValueError("Missing N|uu information")
        self.n_uu = n_uu
        self.n_uu_east = n_uu_east
        self.n_uu_west = n_uu_west
        # Create key which is the combination of n_uu, n_uu_east, n_uu_west.
        key_list = []
        if n_uu != None:
            key_list.append(n_uu)
        if n_uu_east != None:
            key_list.append(n_uu_east + " (east)")
        if n_uu_west != None:
            key_list.append(n_uu_west + " (west)")
        self.key = ", ".join(key_list)
        # Check whether IPA is present.
        if ipa == None and ipa_east == None and ipa_west == None:
            logging.warning("Missing IPA on line " + str(line_nr) + " in " + self.key)
        self.ipa = ipa
        self.ipa_east = ipa_east
        self.ipa_west = ipa_west
        # Check whether English information is present.
        if english == None:
            logging.warning("Missing English on line " + str(line_nr) + " in " + self.key)
        self.english = english
        # Check whether Afrikaans information is present.
        if afrikaans == None:
            logging.warning("Missing Afrikaans on line " + str(line_nr) + " in " + self.key)
        self.afrikaans = afrikaans
        # Check whether Khoekhoegowab information is present.
        if khoekhoegowab == None:
            logging.warning("Missing Khoekhoegowab on line " + str(line_nr) + " in " + self.key)
        self.khoekhoegowab = khoekhoegowab
        self.line_nr = line_nr

    def __str__(self):
        """__str__ provides printable output.
        """
        return "Entry(n_uu=" + self.n_uu + ", n_uu_east=" + self.n_uu_east + ", n_uu_west=" + self.n_uu_west + ", ipa=" + self.ipa + ", ipa_east=" + self.ipa_east + ", ipa_west=" + self.ipa_west + ", english=" + self.english + ", afrikaans=" + self.afrikaans + ", Khoekhoegowab=" + self.khoekhoegowab + ", line_nr=" + self.line_nr + ")"

    def write_portal(self, fp):
        fp.write("**\n")
        fp.write("<Project>N|uu dictionary\n")
        if self.n_uu:
            fp.write("<N|uu>" + self.n_uu + "\n")
        if self.n_uu_east:
            fp.write("<N|uu East>" + self.n_uu_east + "\n")
        if self.n_uu_west:
            fp.write("<N|uu West>" + self.n_uu_west + "\n")
        if self.ipa:
            fp.write("<IPA>" + self.ipa + "\n")
        if self.ipa_east:
            fp.write("<IPA East>" + self.ipa_east + "\n")
        if self.ipa_west:
            fp.write("<IPA West>" + self.ipa_west + "\n")
        if self.english:
            fp.write("<English>" + self.english + "\n")
        if self.afrikaans:
            fp.write("<Afrikaans>" + self.afrikaans + "\n")
        if self.khoekhoegowab:
            fp.write("<Khoekhoegowab>" + self.khoekhoegowab + "\n")
        fp.write("**\n")

    def write_latex(self, fp):
        if self.n_uu:
            fp.write("\\nuu{" + self.n_uu + "}\n")
        if self.n_uu_east:
            fp.write("\\nuu_east{" + self.n_uu_east + "}\n")
        if self.n_uu_west:
            fp.write("\\nuu_west{" + self.n_uu_west + "}\n")
        if self.ipa:
            fp.write("\\ipa{" + self.ipa + "}\n")
        if self.ipa_east:
            fp.write("\\ipa_east{" + self.ipa_east + "}\n")
        if self.ipa_west:
            fp.write("\\ipa_west{" + self.ipa_west + "}\n")
        if self.english:
            fp.write("\\english{" + self.english + "}\n")
        if self.afrikaans:
            fp.write("\\afrikaans{" + self.afrikaans + "}\n")
        if self.khoekhoegowab:
            fp.write("\\khoekhoegowab{" + self.khoekhoegowab + "}\n")
        fp.write("\n\n")


class Dictionary:
    """The Dictionary class stores all information for the dictionary.  It
    checks whether all the required information is present.
    """

    # Entry_type indicates where particular information is stored. For
    # instnace, this could indicate n_uu (=GLOBAL), n_uu_east (=EAST), or
    # n_uu_west (=WEST).
    Entry_type = Enum("Entry_type", "GLOBAL EAST WEST")

    # Entries contains the list of dictionary entries (instances of the
    # Entry class).  The position in this list is used in the mappings
    # (below).
    entries = []
    # Lemma_type is a mapping from a lemma (n_uu word) to the field the
    # lemma is found in (general=n_uu, east=n_uu_east, west=n_uu_west).
    lemma_type = {}
    # IPA_type is a mapping from an ipa representation to the field the
    # IPA is found in (general=n_uu, east=n_uu_east, west=n_uu_west).
    ipa_type = {}
    # The mappings map a key to the entry (index) in the entries variable.
    n_uu_map = {}
    n_uu_east_map = {}
    n_uu_west_map = {}
    ipa_map = {}
    ipa_east_map = {}
    ipa_west_map = {}
    english_map = {}
    afrikaans_map = {}
    khoekhoegowab_map = {}


    def check_add_map(self, element, mapping, index, name, line_nr):
        """Check_add_map checks whether the element is empty and if not, it adds
        it to the mapping, storing the index.  It uses the name for warnings in
        case elements are already present. line_nr is the number of the current
        line.
        """
        if element != None:
            if element in mapping:
                logging.warning("Duplicate value on line " + str(line_nr) + " " + name + ": " + element + " also found on line " + str(self.entries[mapping[element]].line_nr))
            mapping[element] = index

    def insert(self, n_uu, n_uu_east, n_uu_west, ipa, ipa_east, ipa_west, english, afrikaans, khoekhoegowab, line_nr):
        """Create and add the entry to the entries list. Len(self.entries)
        provides the index of the new entry.
        """
        # Convert to string (if needed) and remove any whitespace at beginning
        # or end.
        if n_uu:
            n_uu = str(n_uu).strip()
        if n_uu_east:
            n_uu_east = str(n_uu_east).strip()
        if n_uu_west:
            n_uu_west = str(n_uu_west).strip()
        if ipa:
            ipa = str(ipa).strip()
        if ipa_east:
            ipa_east = str(ipa_east).strip()
        if ipa_west:
            ipa_west = str(ipa_west).strip()
        if english:
            english = str(english).strip()
        if afrikaans:
            afrikaans = str(afrikaans).strip()
        if khoekhoegowab:
            khoekhoegowab = str(khoekhoegowab).strip()

        # Add information to entries
        self.entries.append(Entry(n_uu, n_uu_east, n_uu_west, ipa, ipa_east, ipa_west, english, afrikaans, khoekhoegowab, line_nr))

        new_index = len(self.entries)

        self.check_add_map(n_uu, self.n_uu_map, new_index, "n_uu", line_nr)
        if n_uu != None:
            self.lemma_type[n_uu] = self.Entry_type.GLOBAL

        self.check_add_map(n_uu_east, self.n_uu_east_map, new_index,
                "n_uu_east", line_nr)
        if n_uu_east != None:
            self.lemma_type[n_uu_east] = self.Entry_type.EAST

        self.check_add_map(n_uu_west, self.n_uu_west_map, new_index,
                "n_uu_west", line_nr)
        if n_uu_west != None:
            self.lemma_type[n_uu_west] = self.Entry_type.WEST

        self.check_add_map(ipa, self.ipa_map, new_index, "ipa", line_nr)
        if ipa != None:
            self.ipa_type[ipa] = self.Entry_type.GLOBAL

        self.check_add_map(ipa_east, self.ipa_east_map, new_index, "ipa_east",
                line_nr)
        if ipa_east != None:
            self.ipa_type[ipa_east] = self.Entry_type.EAST

        self.check_add_map(ipa_west, self.ipa_west_map, new_index, "ipa_west",
                line_nr)
        if ipa_west != None:
            self.ipa_type[ipa_west] = self.Entry_type.WEST

        self.check_add_map(english, self.english_map, new_index, "english",
                line_nr)
        self.check_add_map(afrikaans, self.afrikaans_map, new_index,
                "afrikaans", line_nr)
        self.check_add_map(khoekhoegowab, self.khoekhoegowab_map, new_index,
                "khoekhoegowab", line_nr)


    def parse(self, text, line_nr):
        """parse analyses the text for (Western) and (Eastern) variants and
        splits the text into potentially three values.  These values are
        returned as a tuple in the following order:
        there is no eastern or western variant, western variant, eastern
        variant.
        """
        if not text:
            return text, None, None
        east = None
        west = None
        general = None
        # This regular expression searches for an optional comma (which we are
        # not interested in as it can only start at the beginning of the string
        # or directly after a pair of matching brackets).  We then find
        # non-bracket characters, followed by non-bracket characters within a
        # pair of brackets.  In case of a match the first element of the tuple
        # is the word and the second element of the tuple is the label within
        # the brackets.  Note that this ignores everything following the last
        # pair of brackets in case of a match.
        elements = re.findall(r',?([^\(\)]*)\(([^\(\)]*)\)', text)
        # TODO: handle text after last bracket
        if elements:
            for i in elements:
                if i[1] == "Eastern":
                    if east:
                        logging.error("Duplicate Eastern info on line " + str(line_nr))
                    east = i[0].strip()
                elif i[1] == "Western":
                    if west:
                        logging.error("Duplicate Western info on line " + str(line_nr))
                    west = i[0].strip()
                else:
                    logging.warning("Found unknown bracket info: " + str(i[1]) + " on line " + str(line_nr))
                    general = text
        else:
            general = text
        return general, east, west

    def insert_line(self, line, line_nr):
        """Insert_line adds a line from the spreadsheet into the dictionary
        (self). It parses the Orthography 1 and IPA fields as there may be
        eastern or western variants in there.
        """
        n_uu, n_uu_east, n_uu_west = self.parse(line["Orthography 1"], line_nr)
        ipa, ipa_east, ipa_west = self.parse(line["IPA"], line_nr)
        self.insert(n_uu, n_uu_east, n_uu_west, ipa, ipa_east, ipa_west, line["English"], line["Afrikaans"], line["Khoekhoegowab"], line_nr)

    def __str__(self):
        """__str__ provides printable output.
        """
        result = "Dictionary(\n"
        for i in self.entries:
            result += i
        result += ")"
        return result

    def write_portal(self, filename):
        output = open(filename, "w")
        for i in self.entries:
            i.write_portal(output)
        output.close()

    def write_latex_header(self, fp):
        fp.write("\\documentclass{article}\n")
        fp.write("\\newcommand{\\nuu}[1]{#1}\n")
        fp.write("\\newcommand{\\nuu_east}[1]{#1}\n")
        fp.write("\\newcommand{\\nuu_west}[1]{#1}\n")
        fp.write("\\newcommand{\\ipa}[1]{#1}\n")
        fp.write("\\newcommand{\\ipa_east}[1]{#1}\n")
        fp.write("\\newcommand{\\ipa_west}[1]{#1}\n")
        fp.write("\\newcommand{\\english}[1]{#1}\n")
        fp.write("\\newcommand{\\afrikaans}[1]{#1}\n")
        fp.write("\\newcommand{\\khoekhoegowab}[1]{#1}\n")
        fp.write("\\begin{document}\n")

    def write_latex_footer(self, fp):
        fp.write("\\end{document}\n")

    def write_latex(self, filename):
        output = open(filename, "w")
        self.write_latex_header(output)
        for i in self.entries:
            i.write_latex(output)
        self.write_latex_footer(output)
        output.close()
        pass



def read_input(filename):
    """Read input .ods file found at filename. Internalize in a Dictionary
    object.
    """
    logging.debug("Reading in file " + filename)
    global line_nr # GLOBAL
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
        parser.error("An output base filename is required.")

    # Handle the data
    data = read_input(args.input)
    write_output(args.output, data)


if __name__ == '__main__':
    main()
