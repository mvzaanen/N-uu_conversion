#!/usr/bin/env python3
"""convert.py

This program takes a spreadsheet in .ods format containing linguistic
information on the N|uu language (collected through field work).  It
validates the input and converts it into an output that can be used as
the input for the dictionary portal and dictionary app.  It can als generate
output (in LaTeX format) for the physical dictionary.
"""

import argparse
import copy
from enum import Enum
import logging
from pandas_ods_reader import read_ods
import re

def write_latex_header(fp):
    """write_latex_header writes a LaTeX header for the dictionary to fp.
    """
    fp.write("\\documentclass{article}\n")
#    fp.write("\\usepackage[utf8]{inputenc}\n")
    fp.write("\\usepackage{tipa}\n")
    fp.write("\\newenvironment{entry}\n")
    fp.write("{\\noindent\n")
    fp.write("}\n")
    fp.write("{\n")
    fp.write("\\\\[.5em]\n")
    fp.write("}\n")
    fp.write("\\newcommand{\\nuu}[1]{\\textbf{#1}}\n")
    fp.write("\\newcommand{\\nuueast}[1]{\\textbf{#1} (Eastern)}\n")
    fp.write("\\newcommand{\\nuuwest}[1]{\\textbf{#1} (Western)}\n")
    fp.write("\\newcommand{\\ipa}[1]{\\textipa{/#1/}}\n")
    fp.write("\\newcommand{\\ipaeast}[1]{\\textipa{/#1/} (Eastern)}\n")
    fp.write("\\newcommand{\\ipawest}[1]{\\textipa{/#1/} (Western)}\n")
    fp.write("\\newcommand{\\english}[1]{#1 (English)}\n")
    fp.write("\\newcommand{\\afrikaans}[1]{#1 (Afrikaans)}\n")
    fp.write("\\newcommand{\\khoekhoegowab}[1]{#1 (Khoekhoegowab)}\n")
    fp.write("\\begin{document}\n")


def write_latex_footer(fp):
    """write_latex_footer writes a LaTeX footer for the dictionary to fp.
    """
    fp.write("\\end{document}\n")


def clean_latex_ipa(text):
    """clean_latex_ipa takes text and replaces characters so they can be
    displayed correctly in LaTeX using \textipa.
    """
    #  text = text.replace(""
    text = text.replace("&", "\&")
    text = text.replace("<", "$<$")
    text = text.replace("=", "$=$")
    text = text.replace("^", "\^{}")
    text = text.replace("~", "\~{}")
    text = text.replace("Â", "\^{A}")
    text = text.replace("â", "\^{a}")
    text = text.replace("æ", "\\ae{}")
    text = text.replace("ç", "\c{c}")
    text = text.replace("é", "\\'{e}")
    text = text.replace("ê", "\\^{e}")
    text = text.replace("ë", '\\"{e}')
    text = text.replace("î", "\\^{\\i}")
    text = text.replace("ò", "\\`{o}")
    text = text.replace("ô", "\\^{o}")
    text = text.replace("õ", "\\={o}")
    text = text.replace("û", "\\^{u}")
    text = text.replace("Ā", "\\={A}")
    text = text.replace("ā", "\\={a}")
    text = text.replace("ē", "\\={e}")
    text = text.replace("ī", "\\={\\i}")
    text = text.replace("ŋ", "N")
    text = text.replace("ō", "\\={o}")
    text = text.replace("ū", "\\={u}")
    text = text.replace("ǀ", "\\textvertline{}")
    text = text.replace("ǁ", "\\textdoublevertline{}")
    text = text.replace("ǂ", "\\textdoublebarpipe{}")
    text = text.replace("ǃ", "!")
    text = text.replace("ɑ", "A") 
    text = text.replace("ɔ", "O")
    text = text.replace("ə", "@")
    text = text.replace("ɛ", "E")
    text = text.replace("ɟ", "\\textbardotlessj{}")
    text = text.replace("ɡ", "g")
    text = text.replace("ɢ", "\\;G")
    text = text.replace("ɦ", "H")
    text = text.replace("ɨ", "1")
    text = text.replace("ɪ", "I")
    text = text.replace("ɲ", "\\textltailn{}")
    text = text.replace("ɵ", "8")
    text = text.replace("ɾ", "R")
    text = text.replace("ʁ", "K")
    text = text.replace("ʉ", "0")
    text = text.replace("ʊ", "U")
    text = text.replace("ʎ", "L")
    text = text.replace("ʏ", "Y")
    text = text.replace("ʔ", "P")
    text = text.replace("ʘ", "\\!o")
    text = text.replace("ʛ", "!G")
    text = text.replace("ʟ", "\\;L")
    text = text.replace("ʢ", "\\textbarrevglotstop{}")
    text = text.replace("ʰ", "\\super{h}")
    text = text.replace("ʱ", "\\super{H}")
    text = text.replace("ʲ", "\\super{j}")
    text = text.replace("ʷ", "\\super{w}")
    text = text.replace("ʼ", "'")
    text = text.replace("ˀ", "\\textraiseglotstop{}")
    text = text.replace("ː", ":")
    text = text.replace("ˤ", "\\super{Q}")
    text = re.sub(" ̀(.)", "\\`{\1}", text)  # CHECK
    text = re.sub(" ́(.)", "\\'{\1}", text)  # CHECK
    text = re.sub(" ̂(.)", "\\^{\1}", text)  # CHECK
    text = re.sub("ô", "\\^{o}", text)  # CHECK
    text = re.sub("â", "\\^{a}", text)  # CHECK
    text = re.sub(" ̃(.)", "\\~{\1}", text)  # CHECK
    text = re.sub(" ̊(.)", "\\r{\1}", text)  # CHECK
    text = re.sub(" ̤(.)", "\\\"*{\1}", text)  # CHECK
    text = re.sub(" ̥(.)", "\\r*{\1}", text)  # CHECK
    text = re.sub("n̩", "\\\\s{n}", text)  # CHECK
    text = re.sub(" ̻(.)", "\\textsubsquare{\1}", text)  # CHECK
    text = text.replace("β", "B")
    text = text.replace("χ", "X")
    text = text.replace("ᵊ", "\\super{@}")
    text = text.replace("ᵏ", "\\super{k}")
    text = text.replace("ᵑ", "\\super{N}")
    text = text.replace("ᵡ", "\\super{X}")
    text = text.replace("ᶠ", "\\super{f}")
    text = text.replace("ᶢ", "\\super{g}")
    text = text.replace("ṳ", "\\\"*{u}")
    text = text.replace("’", "'")
    text = text.replace("…", "\\ldots{}")
    text = text.replace("ⁱ", "\\super{i}")
    text = text.replace("ⁿ", "\\super{n}")
    return text


def clean_latex_text(text):
    """clean_latex_text takes text and replaces characters so they can be
    displayed correctly in LaTeX.
    """
    # From the N|uu fields
    text = text.replace("^", "\^{}")
    text = text.replace("~", "\~{}")
    text = text.replace("ǃ", "!")
    text = text.replace("Â", "\^{A}")
    text = text.replace("â", "\^{a}")
    text = text.replace("î", "\\^{\\i}")
    text = text.replace("ô", "\\^{o}")
    text = text.replace("û", "\\^{u}")
    text = text.replace("ǀ", "\\textipa{\\textvertline}")
    text = text.replace("ǁ", "\\textipa{\\textdoublevertline}")
    text = text.replace("ǂ", "\\textipa{\\textdoublebarpipe}")
    text = text.replace("ɑ", "\\textipa{A}") 
    text = text.replace("ɟ", "\\textipa{\\textbardotlessj{}}")
    text = text.replace("ʘ", "\\textipa{\\!o}")
    text = text.replace("ʼ", "'")  # CHECK
    text = text.replace(" ̂", "\\^{}")  # CHECK
    text = text.replace(" ̃", "\\~{}")  # CHECK
    text = text.replace("χ", "\\textipa{X}")
    text = text.replace("’", "'")  # CHECK
    # From the Afrikaans, English, Khoekhoegowab fields
    text = text.replace("\"", "``")  # CHECK
    text = text.replace("<", "$<$")
    text = text.replace("â", "\\^{a}")
    text = text.replace("é", "\\'{e}")
    text = text.replace("ê", "\\^{e}")
    text = text.replace("ë", "\\\"{e}")
    text = text.replace("ô", "\\^{o}")
    text = text.replace("û", "\\^{u}")
    text = text.replace("Ā", "\\={A}")
    text = text.replace("ā", "\\={a}")
    text = text.replace("ē", "\\={e}")
    text = text.replace("ī", "\\={\i}")
    text = text.replace("ō", "\\={o}")
    text = text.replace("ū", "\\={u}")
    text = text.replace("…", "\\ldots")
    text = re.sub("î", "\\textipa{\\^{i}}", text)  # CHECK
    return text


def convert_to_string(cell):
    """convert the value of a cell to stripped text, but leave it
    None if it is.
    """
    if cell:
        return str(cell).strip()
    else:
        return None


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
        self.line_nr = str(line_nr)
        # Check whether the n_uu information is present.
        if not n_uu and not n_uu_east and not n_uu_west:
            raise ValueError("Missing N|uu information")
        self.n_uu = n_uu
        self.n_uu_east = n_uu_east
        self.n_uu_west = n_uu_west
        # Create key which is the combination of n_uu, n_uu_east,
        # n_uu_west.  The key is only used for messages (error,
        # warning).
        key_list = []
        if n_uu != None:
            key_list.append(n_uu)
        if n_uu_east != None:
            key_list.append(n_uu_east + " (east)")
        if n_uu_west != None:
            key_list.append(n_uu_west + " (west)")
        self.key = ", ".join(key_list)

        # Check whether IPA is present.
        if not ipa and not ipa_east and not ipa_west:
            logging.warning("Missing IPA on line " + self.line_nr + " in " + self.key)
        self.ipa = ipa
        self.ipa_east = ipa_east
        self.ipa_west = ipa_west

        # Check whether English information is present.
        if not english:
            logging.warning("Missing English on line " + self.line_nr + " in " + self.key)
        self.english = english

        # Check whether Afrikaans information is present.
        if not afrikaans:
            logging.warning("Missing Afrikaans on line " + self.line_nr + " in " + self.key)
        self.afrikaans = afrikaans

        # Check whether Khoekhoegowab information is present.
        if not khoekhoegowab:
            logging.warning("Missing Khoekhoegowab on line " + self.line_nr + " in " + self.key)
        self.khoekhoegowab = khoekhoegowab


    def __str__(self):
        """__str__ provides printable output.
        """
        return "Entry(n_uu=" + str(self.n_uu) + ", n_uu_east=" + str(self.n_uu_east) + ", n_uu_west=" + str(self.n_uu_west) + ", ipa=" + str(self.ipa) + ", ipa_east=" + str(self.ipa_east) + ", ipa_west=" + str(self.ipa_west) + ", english=" + str(self.english) + ", afrikaans=" + str(self.afrikaans) + ", Khoekhoegowab=" + str(self.khoekhoegowab) + ", line_nr=" + str(self.line_nr) + ")"

    def __lt__(self, other):
        """__lt__ implements comparison for (alphabetic) ordering.
        """
        return self.key < other.key

    def write_portal(self, fp):
        """write_portal writes the entry to fp so the information can
        be incorporated in the dictionary portal.
        """
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
        """write_latex writes the Entry into latex form to fp.
        """
        fp.write("\\begin{entry}\n")
        if self.n_uu:
            fp.write("\\nuu{" + clean_latex_text(self.n_uu) + "}\n")
        if self.n_uu_east:
            fp.write("\\nuueast{" + clean_latex_text(self.n_uu_east) + "}\n")
        if self.n_uu_west:
            fp.write("\\nuuwest{" + clean_latex_text(self.n_uu_west) + "}\n")
        if self.ipa:
            fp.write("\\ipa{" + clean_latex_ipa(self.ipa) + "}\n")
        if self.ipa_east:
            fp.write("\\ipaeast{" + clean_latex_ipa(self.ipa_east) + "}\n")
        if self.ipa_west:
            fp.write("\\ipawest{" + clean_latex_ipa(self.ipa_west) + "}\n")
        if self.english:
            fp.write("\\english{" + clean_latex_text(self.english) + "}\n")
        if self.afrikaans:
            fp.write("\\afrikaans{" + clean_latex_text(self.afrikaans) + "}\n")
        if self.khoekhoegowab:
            fp.write("\\khoekhoegowab{" + clean_latex_text(self.khoekhoegowab) + "}\n")
        fp.write("\\end{entry}\n")
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
            else: # Keep the old value
                mapping[element] = index


    def insert(self, n_uu, n_uu_east, n_uu_west, ipa, ipa_east, ipa_west, english, afrikaans, khoekhoegowab, line_nr):
        """Create and add the entry to the entries list. Len(self.entries)
        provides the index of the new entry.
        """
        # Add information to entries
        self.entries.append(Entry(n_uu, n_uu_east, n_uu_west, ipa, ipa_east, ipa_west, english, afrikaans, khoekhoegowab, line_nr))

        new_index = len(self.entries) - 1 # Get index which is length - 1

        self.check_add_map(n_uu, self.n_uu_map, new_index, "n_uu", line_nr)
        if n_uu != None:
            self.lemma_type[n_uu] = self.Entry_type.GLOBAL

        self.check_add_map(n_uu_east, self.n_uu_east_map, new_index, "n_uu_east", line_nr)
        if n_uu_east != None:
            self.lemma_type[n_uu_east] = self.Entry_type.EAST

        self.check_add_map(n_uu_west, self.n_uu_west_map, new_index, "n_uu_west", line_nr)
        if n_uu_west != None:
            self.lemma_type[n_uu_west] = self.Entry_type.WEST

        self.check_add_map(ipa, self.ipa_map, new_index, "ipa", line_nr)
        if ipa != None:
            self.ipa_type[ipa] = self.Entry_type.GLOBAL

        self.check_add_map(ipa_east, self.ipa_east_map, new_index, "ipa_east", line_nr)
        if ipa_east != None:
            self.ipa_type[ipa_east] = self.Entry_type.EAST

        self.check_add_map(ipa_west, self.ipa_west_map, new_index, "ipa_west", line_nr)
        if ipa_west != None:
            self.ipa_type[ipa_west] = self.Entry_type.WEST

        self.check_add_map(english, self.english_map, new_index, "english", line_nr)
        self.check_add_map(afrikaans, self.afrikaans_map, new_index, "afrikaans", line_nr)
        self.check_add_map(khoekhoegowab, self.khoekhoegowab_map, new_index, "khoekhoegowab", line_nr)


    def parse(self, text, mode, line_nr):
        """parse analyses the text for (Western) and (Eastern) variants and
        splits the text into potentially three values.  These values are
        returned as a tuple in the following order:
        there is no eastern or western variant, western variant, eastern
        variant. Mode indicates the type of cell that was investigated
        (as a string).
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
                if i[1].casefold() == "Eastern".casefold(): # handle case
                    if east:
                        logging.error("Duplicate Eastern info in " + mode + " on line " + str(line_nr))
                    east = i[0].strip()
                elif i[1].casefold() == "Western".casefold(): # handle case
                    if west:
                        logging.error("Duplicate Western info in " + mode + " on line " + str(line_nr))
                    west = i[0].strip()
                else:
                    logging.warning("Found unknown bracket info: " + str(i[1]) + " in " + mode + " on line " + str(line_nr))
                    general = text
            # Find the rest of the text after the last closing bracket
            rest = re.search(r'\)([^\)]*)$', text)
            if rest and rest[1] != "":
                logging.warning("Found additional text in " + mode + " after brackets: " + str(rest[1]) + " on line " + str(line_nr))

        else:
            general = text
        return general, east, west


    def insert_line(self, line, line_nr):
        """Insert_line adds a line from the spreadsheet into the dictionary
        (self). It parses the Orthography 1 and IPA fields as there may be
        eastern or western variants in there.
        """
        # Convert to string (if needed) and remove any whitespace at beginning
        # or end.
        orthography = convert_to_string(line["Orthography 1"])
        ipa = convert_to_string(line["IPA"])
        english = convert_to_string(line["English"])
        #afrikaans = convert_to_string(line["Afrikaans"])
        afrikaans = convert_to_string(line["Afrikaans community feedback HEADWORD"])
        #khoekhoegowab = convert_to_string(line["Khoekhoegowab"])
        khoekhoegowab = convert_to_string(line["Khoekhoegowab Levi Namaseb"])

        # Parse the N|uu and IPA entries as there may be eastern and
        # western values in there.
        n_uu, n_uu_east, n_uu_west = self.parse(orthography, "Orthography 1", line_nr)
        ipa, ipa_east, ipa_west = self.parse(ipa, "IPA", line_nr)
        self.insert(n_uu, n_uu_east, n_uu_west, ipa, ipa_east, ipa_west, english, afrikaans, khoekhoegowab, line_nr)


    def __str__(self):
        """__str__ provides printable output.
        """
        result = "Dictionary(Entries:\n"
        for i in self.entries:
            result += "  " + str(i) + "\n"
        result += "lemma_type: " + str(self.lemma_type) + "\n"
        result += "ipa_type: " + str(self.ipa_type) + "\n"
        result += "n_uu_map: " + str(self.n_uu_map) + "\n"
        result += "n_uu_east_map: " + str(self.n_uu_east_map) + "\n"
        result += "n_uu_west_map: " + str(self.n_uu_west_map) + "\n"
        result += "ipa_map: " + str(self.ipa_map) + "\n"
        result += "ipa_east_map: " + str(self.ipa_east_map) + "\n"
        result += "ipa_west_map: " + str(self.ipa_west_map) + "\n"
        result += "english_map: " + str(self.english_map) + "\n"
        result += "afrikaans_map: " + str(self.afrikaans_map) + "\n"
        result += "khoekhoegowab_map: " + str(self.khoekhoegowab_map) + "\n"
        result += ")"
        return result


    def write_portal(self, filename):
        """write_portal writes the dictionary information to the file
        with name filename in the format that can be used for the
        dictionary portal.
        """
        output = open(filename, "w")
        for i in self.entries:
            i.write_portal(output)
        output.close()


    def write_latex(self, filename):
        """Write_latex creates a LaTeX file containing the dictionary
        information.
        """
        output = open(filename, "w")
        write_latex_header(output)
        for i in sorted (self.entries):
            i.write_latex(output)
        write_latex_footer(output)
        output.close()



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
