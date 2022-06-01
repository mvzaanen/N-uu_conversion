#!/usr/bin/env python3
"""dictionary.py

This file contains the implementation of the Dictionary class.
"""

from entry import Entry
from headword import Headword
from output_helper import is_above
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


def get_latex_header():
    """get_latex_header returns a string with a LaTeX header for the
    dictionary.
    """
    return """\\documentclass[10pt,twocolumn]{extarticle}
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
\\newcommand*\\nowtitle{}
\\fancyhead[L]{\\textsf{\\rightmark}} % Top left header
\\fancyhead[R]{\\textsf{\\leftmark}} % Top right header
\\fancyhead[CO]{\\textbf{\\thepage}} % Top odd center header
\\fancyhead[CE]{\\textbf{\\nowtitle}} % Top even center header
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


def get_latex_footer():
    """get_latex_footer returns a string with a LaTeX footer for the
    dictionary.
    """
    return "\\end{document}\n"


def skip_sort_words(word, i):
	l = len(word)
	if i + 7 < l and word[i:i + 7] == "iemand ": #
		return (i + 7, True)
	if i + 7 < l and word[i:i + 7] == "(wees) ": #
		return (i + 7, True)
	if i + 5 < l and word[i:i + 5] == "(be) ": #
		return (i + 5, True)
	if i + 5 < l and word[i:i + 5] == "iets ": #
		return (i + 5, True)
	if i + 5 < l and word[i:i + 5] == "wees ": #
		return (i + 5, True)
	if i + 4 < l and word[i:i + 4] == "die ": #
		return (i + 4, True)
	if i + 4 < l and word[i:i + 4] == "the ": #
		return (i + 4, True)
	if i + 3 < l and word[i:i + 3] == "be ": #
		return (i + 3, True)
	if i + 3 < l and word[i:i + 3] == "'n ": #
		return (i + 3, True)
	if i + 3 < l and word[i:i + 3] == "om ": #
		return (i + 3, True)
	if i + 3 < l and word[i:i + 3] == "te ": #
		return (i + 3, True)
	if i + 2 < l and word[i:i + 2] == "a ": #
		return (i + 2, True)
	# skip -, `, space, and LAST QUARTER MOON (9790) if present
	if i < l and word[i] in "- `'(" + chr(9790):
		return (i + 1, True)
	return (i, False)

                          #!        #!
sort_in = "āâēêëīîōôūû"
sort_in += "ʘǀǁ"
sort_in += "!" + chr(451)
sort_in += "ǂ"
sort_out = "aaeeeiioouu"
sort_out += chr(ord("z")+1) + chr(ord("z")+2) + chr(ord("z")+3)
sort_out += chr(ord("z")+4) + chr(ord("z")+4)
sort_out += chr(ord("z")+5)


def clean_sort(element):
    """clean_sort simplifies entries (element) such that they can be
    ordered properly together.
    """
    # grab the string representation and lowercase
    clean_element = str(element).lower()
    i_word = 0
    l_word = len(clean_element)
    # skip words
    (i_word, skipped) = skip_sort_words(clean_element, i_word)
    while skipped:
        (i_word, skipped) = skip_sort_words(clean_element, i_word)
    clean_element = clean_element[i_word:]
    # clean letters
    trans_map = clean_element.maketrans(sort_in, sort_out)
    clean_element = clean_element.translate(trans_map)
    result = ""
    for i in clean_element:
        if not is_above(ord(i)):
            result += i
    return result


def entry_sort(entry, element, lang):
    """entry_sort provides a string that can be used to sort within
    entries of the same clean_sort.
    """
    result = []
    # grab the string representation and lowercase
    el = str(element).lower()
    i_word = 0
    l_word = len(el)
    # skip words
    (i_word, skipped) = skip_sort_words(el, i_word)
    while skipped:
        (i_word, skipped) = skip_sort_words(el, i_word)
    # first the cleaned headword
    result.append(el[i_word:])
    # next the POS
    result.append(Entry.pos2text(entry.pos))
    # next the other headwords
    result.append(", ".join(map(str, [hw for hw in entry.headwords[lang] if hw != element])))
    # next the skipped initial part
    result.append(el[:i_word])
    return " @ ".join(result)



class Dictionary:
    """The Dictionary class stores all information for the dictionary.  It
    checks whether all the required information is present.
    """

    def __init__(self):
        # Entries contains the list of dictionary entries (instances of the
        # Entry class).  The position in this list is used in the mappings
        # (below).
        self.entries = []
        # The lang_map maps a headword to the entry (index) in the
        # entries variable.  The sort_map keeps the simplified word
        # (used for sorting) as keys, mapping to the entries (indices)
        # in the entries variable as well as the original word (so a
        # tuple of index and original word).
        self.lang_map = {}
        self.sort_map = {}
        for lang in Entry.Lang_type:
            self.lang_map[lang] = {}
            self.sort_map[lang] = {}


    def check_add_map(self, element, lang, index, line_nr):
        """Check_add_map checks whether the element is empty and if not, it adds
        it to the mapping, storing the index.  It uses the name for warnings in
        case elements are already present. line_nr is the number of the current
        line.
        """
        if element != None:
            # Add entry to lang_map
            if element in self.lang_map[lang]:
                lines = []
                for el in self.lang_map[lang][element]:
                    lines.append(self.entries[el].line_nr)
                logging.warning("Duplicate value on line " + str(line_nr) + " " + Entry.lang2text(lang) + ": " + str(element) + " also found on line(s) " + ", ".join(lines))
                self.lang_map[lang][element].append(index)
            else: # Set initial value
                self.lang_map[lang][element] = [index]
            # Add entry to sort_map, first find word to order on
            sort_element = clean_sort(element)
            if sort_element in self.sort_map[lang]:
                self.sort_map[lang][sort_element].append((index, element))
            else: # Set initial value
                self.sort_map[lang][sort_element] = [(index, element)]


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


    def get_portal(self):
        """get_portal returns a string of the dictionary information
        in the format that can be used for the dictionary portal.
        """
        result = ""
        for i in self.entries:
            result += i.get_portal()
        return result


    def get_lang_latex(self, lang):
        """get_lang_latex returns a string with the LaTeX lemmas
        sorted according to mapping.
        """
        result = "{\\hfill\\\\\\Large\\textbf{" + Entry.lang2latex_long(lang) + "}}\\\\\n"
        result += "\\renewcommand*\\nowtitle{" + Entry.lang2latex_long(lang) + " }\n"
        for element in sorted(self.sort_map[lang]):
            for values in sorted(self.sort_map[lang][element], key = lambda x: entry_sort(self.entries[x[0]], x[1], lang)):
                index = values[0] # index in entries
                word = values[1] # actual, original word
                result += self.entries[index].get_latex(word, lang)
        return result


    def get_latex(self):
        """get_latex returns a string containing the dictionary
        information.
        """
        result = get_latex_header()
        ### N|uu
        result += self.get_lang_latex(Entry.Lang_type.NUU)
        ### Nama
        result += self.get_lang_latex(Entry.Lang_type.NAMA)
        ### Afrikaans
        result += self.get_lang_latex(Entry.Lang_type.AFRIKAANS)
        ### English
        result += self.get_lang_latex(Entry.Lang_type.ENGLISH)
        result += get_latex_footer()
        return result

