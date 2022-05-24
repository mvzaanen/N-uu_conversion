#!/usr/bin/env python3
"""dictionary.py

This file contains the implementation of the Dictionary class.
"""

from entry import Entry
from headword import Headword
import logging
import re



def convert_to_string(cell):
    """convert the value of a cell to stripped text, but leave it
    None if it is None.
    """
    if cell:
        return str(cell).strip()
    else:
        return None


def parse(text):
    """parse analyses the text for (Western) and (Eastern) variants and
    splits the text into potentially three values.  These values are
    returned as a list of Headwords.
    """
    result = []
    if not text:
        return result
    # This regular expression searches for an optional comma (which we are
    # not interested in as it can only start at the beginning of the string
    # or directly after a pair of matching brackets).  We then find
    # non-bracket characters, followed by non-bracket characters within a
    # pair of brackets.  In case of a match the first element of the tuple
    # is the word and the second element of the tuple is the label within
    # the brackets.  Note that this ignores everything following the last
    # pair of brackets in case of a match.
    hws = text.split(';')
    for hw in hws:
        marker = Headword.Marker_type.NONE
        text = hw.strip()
        east = re.match("(.*)\(Eastern\)", hw, re.I)
        west = re.match("(.*)\(Western\)", hw, re.I)
        if east:
            text = east[1].strip()
            marker = Headword.Marker_type.EAST
        elif west:
            text = west[1].strip()
            marker = Headword.Marker_type.WEST
        result.append(Headword(text, marker))
    return result


def write_latex_header(fp):
    """write_latex_header writes a LaTeX header for the dictionary to fp.
    """
    header = """\\documentclass[10pt,twocolumn]{extarticle}
\\usepackage[dvips=false,pdftex=false,vtex=false]{geometry}
\\setlength{\columnseprule}{0.4pt}
\\geometry{
    a4paper,
    left=10mm,
    right=23mm,
    top=10mm,
    bottom=10mm,
    includehead,
    twoside
}
\\usepackage{tipa}
\\usepackage{fancyhdr}
\\fancyhead[L]{\\textsf{\\rightmark}} % Top left header
\\fancyhead[R]{\\textsf{\\leftmark}} % Top right header
\\fancyhead[C]{\\textbf{\\textsf{\\thepage}}} % Top center header
\\fancyfoot[L]{} % Bottom left footer
\\fancyfoot[R]{} % Bottom right footer
\\fancyfoot[C]{} % Bottom center footer
\\renewcommand{\\headrulewidth}{0.4pt} % Rule under the header
\\renewcommand{\\footrulewidth}{0pt} % Rule under the footer
\\addtolength{\\textheight}{\\headsep}
\\setlength{\\headsep}{0pt} % Separator between header and text
\\pagestyle{fancy} % Use the custom headers and footers throughout the document
% headervalue, headword, pos, IPA, meaning, parentheticals
\\newcommand{\\entry}[6]{#2\\markboth{#1}{#1} #3 #4 #5 #6}
\\setlength{\parindent}{0cm}
\\setlength{\parskip}{0mm}
\\begin{document}
"""
    fp.write(header)


def write_latex_footer(fp):
    """write_latex_footer writes a LaTeX footer for the dictionary to fp.
    """
    fp.write("\\end{document}\n")






class Dictionary:
    """The Dictionary class stores all information for the dictionary.  It
    checks whether all the required information is present.
    """

    def __init__(self):
        # Entries contains the list of dictionary entries (instances of the
        # Entry class).  The position in this list is used in the mappings
        # (below).
        self.entries = []
        # The mappings map a headword to the entry (index) in the entries variable.
        self.lang_map = {}
        for lang in Entry.Lang_type:
            self.lang_map[lang] = {}


    def check_add_map(self, element, lang, index, line_nr):
        """Check_add_map checks whether the element is empty and if not, it adds
        it to the mapping, storing the index.  It uses the name for warnings in
        case elements are already present. line_nr is the number of the current
        line.
        """
        if element != None:
            if element in self.lang_map[lang]:
                lines = []
                for el in self.lang_map[lang][element]:
                    lines.append(self.entries[el].line_nr)
                logging.warning("Duplicate value on line " + str(line_nr) + " " + Entry.lang2text(lang) + ": " + str(element) + " also found on line(s) " + ", ".join(lines))
                self.lang_map[lang][element].append(index)
            else: # Set initial value
                self.lang_map[lang][element] = [index]


    def insert(self, n_uu, pos, ipa, nama, afrikaans, afr_loc, english, par_nama, par_afrikaans, par_english, line_nr):
        """Create and add the entry to the entries list. Len(self.entries)
        provides the index of the new entry.  Parse the language
        and IPA fields.
        """
        # Create headwords
        hws = {}
        hws[Entry.Lang_type.NUU] = parse(n_uu)
        if ipa:
            hws[Entry.Lang_type.IPA] = parse(ipa)
        if nama:
            hws[Entry.Lang_type.NAMA] = parse(nama)
        if afrikaans:
            hws[Entry.Lang_type.AFRIKAANS] = parse(afrikaans)
        if afr_loc:
            hws[Entry.Lang_type.AFR_LOC] = parse(afr_loc)
        if english:
            hws[Entry.Lang_type.ENGLISH] = parse(english)
        parentheticals = {}
        if par_nama:
            parentheticals[Entry.Lang_type.NAMA] = par_nama
        if par_afrikaans:
            parentheticals[Entry.Lang_type.AFRIKAANS] = par_afrikaans
        if par_english:
            parentheticals[Entry.Lang_type.ENGLISH] = par_english

        if not pos:  
            pos = ""
            logging.warning("Missing POS on line " + str(line_nr))
        # Add information to entries
        self.entries.append(Entry(hws, pos, parentheticals, line_nr))
        new_index = len(self.entries) - 1 # Get index which is length - 1

        # Insert information in self.lang_map
        for lang in hws:
            for hw in hws[lang]:
                self.check_add_map(hw, lang, new_index, line_nr)


    def insert_line(self, line, line_nr):
        """Insert_line adds a line from the spreadsheet into the dictionary
        (self). It parses the Orthography 1 and IPA fields as there may be
        eastern or western variants in there.
        """
        # Convert to string (if needed) and remove any whitespace at beginning
        # or end.
        n_uu = convert_to_string(line["Orthography 1"])
        ipa = convert_to_string(line["IPA"])
        pos = convert_to_string(line["Part of Speech, English"])
        nama = convert_to_string(line["Nama Feedback"])
        par_nama = convert_to_string(line["Nama Parentheticals"])
        afrikaans = convert_to_string(line["Afrikaans community feedback HEADWORD"])
        afr_loc = convert_to_string(line["Afrikaans community feedback Local Variety "])
        par_afrikaans = convert_to_string(line["Afrik Parentheticals"])
        english = convert_to_string(line["English"])
        par_english = convert_to_string(line["Parentheticals, English"])

        self.insert(n_uu, pos, ipa, nama, afrikaans, afr_loc, english, par_nama, par_afrikaans, par_english, line_nr)


    def __str__(self):
        """__str__ provides printable output.
        """
        result = "Dictionary(Entries:\n"
        for i in self.entries:
            result += "  " + str(i) + "\n"
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


    def write_lang_latex(self, fp, lang):
        """write_lang_latex writes the LaTeX lemmas sorted according
        to mapping to fp.
        """
        for element in sorted(self.lang_map[lang]):
            for index in self.lang_map[lang][element]:
                self.entries[index].write_latex(fp, element, lang)


    def write_latex(self, filename):
        """Write_latex creates a LaTeX file containing the dictionary
        information.
        """
        output = open(filename, "w")
        write_latex_header(output)
        ### N|uu
        self.write_lang_latex(output, Entry.Lang_type.NUU)
        ### Nama
        self.write_lang_latex(output, Entry.Lang_type.NAMA)
        ### Afrikaans
        self.write_lang_latex(output, Entry.Lang_type.AFRIKAANS)
        ### English
        self.write_lang_latex(output, Entry.Lang_type.ENGLISH)
        write_latex_footer(output)
        output.close()

