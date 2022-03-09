#!/usr/bin/env python3
"""dictionary.py

This file contains the implementation of the Dictionary class.
"""

from entry import Entry
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


def parse(text, mode, line_nr):
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
    elements = re.findall(r';?([^\(\)]*)\(([^\(\)]*)\)', text)
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


def write_latex_header(fp):
    """write_latex_header writes a LaTeX header for the dictionary to fp.
    """
    header = """
\\documentclass{article}
\\usepackage[dvips=false,pdftex=false,vtex=false]{geometry}
\\geometry{
paperwidth=170mm,
paperheight=244mm,
left=10mm,
top=10mm,
includefoot,
twoside
}
\\usepackage[cam,a4,center,pdflatex]{crop}
\\usepackage{tipa}
\\newenvironment{entry}
{\\noindent
}
{
\\\\[.5em]
}
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
        # Lemma_type is a mapping from a lemma (n_uu word) to the field the
        # lemma is found in (general=n_uu, east=n_uu_east, west=n_uu_west).
        self.lemma_type = {}
        # The mappings map a key to the entry (index) in the entries variable.
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
                logging.warning("Duplicate value on line " + str(line_nr) + " " + Entry.lang_name(lang) + ": " + element + " also found on line(s) " + ", ".join(lines))
                self.lang_map[lang][element].append(index)
            else: # Set initial value
                self.lang_map[lang][element] = [index]


    def insert(self, n_uu, n_uu_east, n_uu_west, pos, ipa, ipa_east, ipa_west, english, par_english, afrikaans, par_afrikaans, afr_loc, nama, par_nama, line_nr):
        """Create and add the entry to the entries list. Len(self.entries)
        provides the index of the new entry.
        """
        # Add information to entries
        self.entries.append(Entry(n_uu, n_uu_east, n_uu_west, pos, ipa, ipa_east, ipa_west, english, par_english, afrikaans, par_afrikaans, afr_loc, nama, par_nama, line_nr))

        if (n_uu and n_uu_east) or (n_uu and n_uu_west):
            logging.warning("Both N|uu and N|uu east or west on line " + str(line_nr))

        new_index = len(self.entries) - 1 # Get index which is length - 1

        self.check_add_map(n_uu, Entry.Lang_type.NUU, new_index, line_nr)
        if n_uu != None:
            if n_uu in self.lemma_type and self.lemma_type[n_uu] != Entry.Marker_type.NONE:
                logging.error("Found " + str(n_uu) + " as " + str(self.lemma_type[n_uu]) + " and " + str(Entry.Marker_type.NONE))
            self.lemma_type[n_uu] = Entry.Marker_type.NONE

        self.check_add_map(n_uu_east, Entry.Lang_type.NUU, new_index, line_nr)
        if n_uu_east != None:
            if n_uu_east in self.lemma_type and self.lemma_type[n_uu_east] != Entry.Marker_type.EAST:
                logging.error("Found " + str(n_uu_east) + " as " + str(self.lemma_type[n_uu_east]) + " and " + str(Entry.Marker_type.EAST))
            self.lemma_type[n_uu_east] = Entry.Marker_type.EAST

        self.check_add_map(n_uu_west, Entry.Lang_type.NUU, new_index, line_nr)
        if n_uu_west != None:
            if n_uu_west in self.lemma_type and self.lemma_type[n_uu_west] != Entry.Marker_type.WEST:
                logging.error("Found " + str(n_uu_west) + " as " + str(self.lemma_type[n_uu_west]) + " and " + str(Entry.Marker_type.WEST))
            self.lemma_type[n_uu_west] = Entry.Marker_type.WEST


        self.check_add_map(english, Entry.Lang_type.ENGLISH, new_index, line_nr)
        self.check_add_map(afrikaans, Entry.Lang_type.AFRIKAANS, new_index, line_nr)
        self.check_add_map(afr_loc, Entry.Lang_type.AFR_LOC, new_index, line_nr)
        self.check_add_map(nama, Entry.Lang_type.NAMA, new_index, line_nr)


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
        par_english = convert_to_string(line["Parentheticals, English"])
        pos = convert_to_string(line["Part of Speech, English"])
        afrikaans = convert_to_string(line["Afrikaans community feedback HEADWORD"])
        afr_loc = convert_to_string(line["Afrikaans community feedback Local Variety "])
        par_afrikaans = convert_to_string(line["Afrik Parentheticals"])
        nama = convert_to_string(line["Nama Feedback"])
        par_nama = convert_to_string(line["Nama Parentheticals"])

        # Parse the N|uu and IPA entries as there may be eastern and
        # western values in there.
        n_uu, n_uu_east, n_uu_west = parse(orthography, "Orthography 1", line_nr)
        ipa, ipa_east, ipa_west = parse(ipa, "IPA", line_nr)
        self.insert(n_uu, n_uu_east, n_uu_west, pos, ipa, ipa_east, ipa_west, english, par_english, afrikaans, par_afrikaans, afr_loc, nama, par_nama, line_nr)


    def __str__(self):
        """__str__ provides printable output.
        """
        result = "Dictionary(Entries:\n"
        for i in self.entries:
            result += "  " + str(i) + "\n"
        result += "lemma_type: " + str(self.lemma_type) + "\n"
        result += "n_uu_map: " + str(self.n_uu_map) + "\n"
        result += "n_uu_east_map: " + str(self.n_uu_east_map) + "\n"
        result += "n_uu_west_map: " + str(self.n_uu_west_map) + "\n"
        result += "english_map: " + str(self.english_map) + "\n"
        result += "afrikaans_map: " + str(self.afrikaans_map) + "\n"
        result += "nama_map: " + str(self.nama_map) + "\n"
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
#        for lemma in sorted(sort_mapping):
        for lemma in self.lang_map[lang]:
            sublang = None
            if lang == Entry.Lang_type.NUU:
                sublang = self.lemma_type[lemma]
            for entry in self.lang_map[lang][lemma]:
                self.entries[entry].write_latex(fp, lang, sublang)

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

