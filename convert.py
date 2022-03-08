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
from itertools import chain
import logging
from pandas_ods_reader import read_ods
import re

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


def write_latex_data(fp, headword, hw_extra, ipa, pos, other_lang, par_nama, par_afrikaans, par_english):
    """write_latex_data writes the information into LaTeX form to fp.
    """
    fp.write("\\begin{entry}\n")
    fp.write("\\textbf{" + clean(headword, text_latex_mapping) + "}\n")
    if hw_extra:
        fp.write(clean(hw_extra, text_latex_mapping) + "\n")
    if ipa:
        fp.write("[\\textipa{" + clean(ipa, ipa_latex_mapping) + "}]\n")
    fp.write("(" + clean(pos, text_latex_mapping) + ");\n")
    for (text, lang) in other_lang:
        #fp.write(clean(text, text_latex_mapping) + " (" + Entry.lang_name_latex(lang)+ ") \n")
        fp.write("\\underbar{" + Entry.lang_name_latex(lang)+ "}: " + clean(text, text_latex_mapping) + ";\n")
    fp.write("\\newline\n")
    if par_nama:
        fp.write("\\small{\\underbar{Nama}: " + clean(par_nama, text_latex_mapping) + "}\\newline\n")
    if par_afrikaans:
        fp.write("\\small{\\underbar{Afr}: " + clean(par_afrikaans, text_latex_mapping) + "}\\newline\n")
    if par_english:
        fp.write("\\small{\\underbar{Eng}: " + clean(par_english, text_latex_mapping) + "}\\newline\n")
    fp.write("\\end{entry}\n")
    fp.write("\n\n")


ipa_latex_mapping = {
    32 : " ",
    33 : "!",
    34 : "\"",
    35 : "\\#",
    36 : "\\$",
    37 : "\\%",
    38 : "\\&",
    39 : "'",
    40 : "(",
    41 : ")",
    42 : "*",
    43 : "+",
    44 : ",",
    45 : "-",
    46 : ".",
    47 : "/",
    48 : "0",
    49 : "1",
    50 : "2",
    51 : "3",
    52 : "4",
    53 : "5",
    54 : "6",
    55 : "7",
    56 : "8",
    57 : "9",
    58 : ":",
    59 : ";",
    60 : "$<$",
    61 : "$=$",
    62 : "$>$",
    63 : "?",
    64 : "@",
    65 : "\\*{A}",
    66 : "\\*{B}",
    67 : "\\*{C}",
    68 : "\\*{D}",
    69 : "\\*{E}",
    70 : "\\*{F}",
    71 : "\\*{G}",
    72 : "\\*{H}",
    73 : "\\*{I}",
    74 : "\\*{J}",
    75 : "\\*{K}",
    76 : "\\*{L}",
    77 : "\\*{M}",
    78 : "\\*{N}",
    79 : "\\*{O}",
    80 : "\\*{P}",
    81 : "\\*{Q}",
    82 : "\\*{R}",
    83 : "\\*{S}",
    84 : "\\*{T}",
    85 : "\\*{U}",
    86 : "\\*{V}",
    87 : "\\*{W}",
    88 : "\\*{X}",
    89 : "\\*{Y}",
    90 : "\\*{Z}",
    91 : "[",
    92 : "\\",
    93 : "]",
    94 : "\\^{}",
    95 : "\\_",
    96 : "`",
    97 : "a",
    98 : "b",
    99 : "c",
    100 : "d",
    101 : "e",
    102 : "f",
    103 : "g",
    104 : "h",
    105 : "i",
    106 : "j",
    107 : "k",
    108 : "l",
    109 : "m",
    110 : "n",
    111 : "o",
    112 : "p",
    113 : "q",
    114 : "r",
    115 : "s",
    116 : "t",
    117 : "u",
    118 : "v",
    119 : "w",
    120 : "x",
    121 : "y",
    122 : "z",
    123 : "\\{",
    124 : "$|$",
    125 : "\\}",
    126 : "\\~{}",
    194 : "\^{A}", # LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    226 : "\^{a}", # LATIN SMALL LETTER A WITH CIRCUMFLEX
    230 : "\\ae{}", # LATIN SMALL LETTER AE
    231 : "\c{c}", # LATIN SMALL LETTER C WITH CEDILLA
    233 : "\\'{e}", # LATIN SMALL LETTER E WITH ACUTE
    234 : "\\^{e}", # LATIN SMALL LETTER E WITH CIRCUMFLEX
    235 : '\\"{e}', # LATIN SMALL LETTER E WITH DIAERESIS
    238 : "\\^{\\i}", # LATIN SMALL LETTER I WITH CIRCUMFLEX
    242 : "\\`{o}", # LATIN SMALL LETTER O WITH GRAVE
    244 : "\\^{o}", # LATIN SMALL LETTER O WITH CIRCUMFLEX
    245 : "\\={o}", # LATIN SMALL LETTER O WITH TILDE
    251 : "\\^{u}", # LATIN SMALL LETTER U WITH CIRCUMFLEX
    256 : "\\={A}", # LATIN CAPITAL LETTER A WITH MACRON
    257 : "\\={a}", # LATIN SMALL LETTER A WITH MACRON
    275 : "\\={e}", # LATIN SMALL LETTER E WITH MACRON
    299 : "\\={\\i}", # LATIN SMALL LETTER I WITH MACRON
    331 : "N", # LATIN SMALL LETTER ENG
    333 : "\\={o}", # LATIN SMALL LETTER O WITH MACRON
    363 : "\\={u}", # LATIN SMALL LETTER U WITH MACRON
    448 : "\\textvertline{}", # LATIN LETTER DENTAL CLICK
    449 : "\\textdoublevertline{}", # LATIN LETTER LATERAL CLICK
    450 : "\\textdoublebarpipe{}", # LATIN LETTER ALVEOLAR CLICK
    451 : "!", # LATIN LETTER RETROFLEX CLICK
    593 : "A", # LATIN SMALL LETTER ALPHA
    596 : "O", # LATIN SMALL LETTER OPEN O
    601 : "@", # LATIN SMALL LETTER SCHWA
    603 : "E", # LATIN SMALL LETTER OPEN E
    607 : "\\textbardotlessj{}", # LATIN SMALL LETTER DOTLESS J WITH STROKE
    609 : "g", # LATIN SMALL LETTER SCRIPT G
    610 : "\\;G", # LATIN LETTER SMALL CAPITAL G
    614 : "H", # LATIN SMALL LETTER H WITH HOOK
    616 : "1", # LATIN SMALL LETTER I WITH STROKE
    618 : "I", # LATIN LETTER SMALL CAPITAL I
    626 : "\\textltailn{}", # LATIN SMALL LETTER N WITH LEFT HOOK
    629 : "8", # LATIN SMALL LETTER BARRED O
    638 : "R", # LATIN SMALL LETTER R WITH FISHHOOK
    641 : "K", # LATIN LETTER SMALL CAPITAL INVERTED R
    649 : "0", # LATIN SMALL LETTER U BAR
    650 : "U", # LATIN SMALL LETTER UPSILON
    654 : "L", # LATIN SMALL LETTER TURNED Y
    655 : "Y", # LATIN LETTER SMALL CAPITAL Y
    660 : "P", # LATIN LETTER GLOTTAL STOP
    664 : "\\!o", # LATIN LETTER BILABIAL CLICK
    667 : "!G", # LATIN LETTER SMALL CAPITAL G WITH HOOK
    671 : "\\;L", # LATIN LETTER SMALL CAPITAL L
    674 : "\\textbarrevglotstop{}", # LATIN LETTER REVERSED GLOTTAL STOP WITH STROKE
    688 : "\\super{h}", # MODIFIER LETTER SMALL H
    689 : "\\super{H}", # MODIFIER LETTER SMALL H WITH HOOK
    690 : "\\super{j}", # MODIFIER LETTER SMALL J
    695 : "\\super{w}", # MODIFIER LETTER SMALL W
    700 : "'", # MODIFIER LETTER APOSTROPHE
    704 : "\\textraiseglotstop{}", # MODIFIER LETTER GLOTTAL STOP
    720 : ":",  # MODIFIER LETTER TRIANGULAR COLON
    740 : "\\super{Q}", # MODIFIER LETTER SMALL REVERSED GLOTTAL STOP
    768 : "\\`{", # COMBINING GRAVE ACCENT
    769 : "\\'{", # COMBINING ACUTE ACCENT
    770 : "\\^{", # COMBINING CIRCUMFLEX ACCENT
    771 : "\\~{", # COMBINING TILDE
    778 : "\\r{", # COMBINING RING ABOVE
    804 : "\\\"*{", # COMBINING DIAERESIS BELOW
    805 : "\\r{", # COMBINING RING BELOW -> map to COMBINING RING ABOVE
    809 : "\\s{", # COMBINING VERTICAL LINE BELOW
    827 : "\\textsubsquare{", # COMBINING SQUARE BELOW
    946 : "B", # GREEK SMALL LETTER BETA
    967 : "X", # GREEK SMALL LETTER CHI
    7498 : "\\super{@}", # MODIFIER LETTER SMALL SCHWA
    7503 : "\\super{k}", # MODIFIER LETTER SMALL K
    7505 : "\\super{N}", # MODIFIER LETTER SMALL ENG
    7521 : "\\super{X}", # MODIFIER LETTER SMALL CHI
    7584 : "\\super{f}", # MODIFIER LETTER SMALL F
    7586 : "\\super{g}", # MODIFIER LETTER SMALL SCRIPT G
    7795 : "\\\"*{u}", # LATIN SMALL LETTER U WITH DIAERESIS BELOW
    8217 : "'", # RIGHT SINGLE QUOTATION MARK
    8230 : "\\ldots{}", # HORIZONTAL ELLIPSIS
    8305 : "\\super{i}", # SUPERSCRIPT LATIN SMALL LETTER I
    8319 : "\\super{n}", # SUPERSCRIPT LATIN SMALL LETTER N
}

text_latex_mapping = {
    32 : " ",
    33 : "!",
    34 : "\"",
    35 : "\\#",
    36 : "\\$",
    37 : "\\%",
    38 : "\\&",
    38 : "\\&",
    39 : "'",
    40 : "(",
    41 : ")",
    42 : "*",
    43 : "+",
    44 : ",",
    45 : "-",
    46 : ".",
    47 : "/",
    48 : "0",
    49 : "1",
    50 : "2",
    51 : "3",
    52 : "4",
    53 : "5",
    54 : "6",
    55 : "7",
    56 : "8",
    57 : "9",
    58 : ":",
    59 : ";",
    60 : "$<$",
    61 : "$=$",
    62 : "$>$",
    63 : "?",
    64 : "@",
    65 : "A",
    66 : "B",
    67 : "C",
    68 : "D",
    69 : "E",
    70 : "F",
    71 : "G",
    72 : "H",
    73 : "I",
    74 : "J",
    75 : "K",
    76 : "L",
    77 : "M",
    78 : "N",
    79 : "O",
    80 : "P",
    81 : "Q",
    82 : "R",
    83 : "S",
    84 : "T",
    85 : "U",
    86 : "V",
    87 : "W",
    88 : "X",
    89 : "Y",
    90 : "Z",
    91 : "[",
    92 : "\\\\",
    93 : "]",
    94 : "\\^{}",
    95 : "\\_",
    96 : "`",
    97 : "a",
    98 : "b",
    99 : "c",
    100 : "d",
    101 : "e",
    102 : "f",
    103 : "g",
    104 : "h",
    105 : "i",
    106 : "j",
    107 : "k",
    108 : "l",
    109 : "m",
    110 : "n",
    111 : "o",
    112 : "p",
    113 : "q",
    114 : "r",
    115 : "s",
    116 : "t",
    117 : "u",
    118 : "v",
    119 : "w",
    120 : "x",
    121 : "y",
    122 : "z",
    123 : "\\{",
    124 : "$|$",
    125 : "\\}",
    126 : "\\~{}",
    160 : "~", # NON-BREAKING SPACE
    176 : "$^{\circ}$", # DEGREE SIGN
    194 : "\^{A}", # LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    206 : "\^{I}", # LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    226 : "\^{a}", # LATIN SMALL LETTER A WITH CIRCUMFLEX
    233 : "\\'{e}", # LATIN SMALL LETTER E WITH ACUTE
    234 : "\\^{e}", # LATIN SMALL LETTER E WITH CIRCUMFLEX
    235 : '\\"{e}', # LATIN SMALL LETTER E WITH DIAERESIS
    238 : "\\^{\\i}", # LATIN SMALL LETTER I WITH CIRCUMFLEX
    239 : '\\"{\\i}', # LATIN SMALL LETTER I WITH DIAERESIS
    244 : "\\^{o}", # LATIN SMALL LETTER O WITH CIRCUMFLEX
    251 : "\\^{u}", # LATIN SMALL LETTER U WITH CIRCUMFLEX
    256 : "\\={A}", # LATIN CAPITAL LETTER A WITH MACRON
    257 : "\\={a}", # LATIN SMALL LETTER A WITH MACRON
    275 : "\\={e}", # LATIN SMALL LETTER E WITH MACRON
    298 : "\\={I}", # LATIN CAPITAL LETTER I WITH MACRON
    299 : "\\={\\i}", # LATIN SMALL LETTER I WITH MACRON
    333 : "\\={o}", # LATIN SMALL LETTER O WITH MACRON
    363 : "\\={u}", # LATIN SMALL LETTER U WITH MACRON
    448 : "\\textipa{\\textvertline}", # LATIN LETTER DENTAL CLICK
    449 : "\\textipa{\\textdoublevertline}", # LATIN LETTER LATERAL CLICK
    450 : "\\textipa{\\textdoublebarpipe}", # LATIN LETTER ALVEOLAR CLICK
    451 : "!", # LATIN LETTER RETROFLEX CLICK
    593 : "\\textipa{A}", # LATIN SMALL LETTER ALPHA
    607 : "\\textipa{\\textbardotlessj{}}", # LATIN SMALL LETTER DOTLESS J WITH STROKE
    664 : "\\textipa{\\!o}", # LATIN LETTER BILABIAL CLICK
    690 : "$^{j}$", # Modifier Letter Small J 
    700 : "'", # MODIFIER LETTER APOSTROPHE
    770 : "\\^{", # COMBINING CIRCUMFLEX ACCENT
    771 : "\\~{", # COMBINING TILDE
    967 : "\\textipa{X}", # GREEK SMALL LETTER CHI
    8217 : "'", # RIGHT SINGLE QUOTATION MARK
    8220 : "``", # LEFT DOUBLE QUOTATION MARK
    8221 : "''", # RIGHT DOUBLE QUOTATION MARK
    8230 : "\\ldots", # HORIZONTAL ELLIPSIS
    9789 : "}", # FIRST QUARTER MOON
    9790 : "\\textit{", # LAST QUARTER MOON
}


def is_above(char):
    """is_above returns true if the char which is an ord value is a
    combining character that is located above the letter, false
    otherwise.
    """
    return (char >= 768 and char <= 789) or (char == 794) or (char >= 829 and char <= 836) or (char == 838) or (char >= 842 and char <= 844) or (char >= 864 and char <= 865)


def handle_combining(text, index, base, mapping):
    """handle_combining handles a letter that has combining
    characters.  These are always found after the actual letter. 
    text is the full text, index is the start of the combining
    characters, base is the base letter, mapping is the mapping to be
    applied.
    """
    combining_char = ord(text[index])
    accent_above = is_above(combining_char)
    result = mapping[combining_char] # grab combining character
    if index + 1 < len(text) and ord(text[index + 1]) >= 768 and ord(text[index + 1]) <= 880: # test if next char is combining
        (combined, index, rest_above) = handle_combining(text, index + 1, base, mapping)
        accent_above = accent_above or rest_above  # either this character has an accent above or one of the following chars
        return (result + combined + "}", index, accent_above)
    else:
        if accent_above and base == "i":
            base = "\\i" # remove dot on i
        elif accent_above and base == "j":
            base = "\\j" # remove dot on j
        return (result + base + "}", index, accent_above)


def clean(text, mapping):
    """clean takes text and replaces characters so they can be
    displayed correctly in LaTeX using the mapping.
    """
    result = ""
    index = 0
    if text == None:
        text = ""
    while index < len(text):
        base = mapping[ord(text[index])] # Grab base letter
        if index + 1 < len(text) and ord(text[index + 1]) >= 768 and ord(text[index + 1]) <= 880: # test if next char is combining
                (combined, index, accent_above) = handle_combining(text, index + 1, base, mapping)
                result += combined
        else:
            result += base
        index += 1
    return result


def convert_to_string(cell):
    """convert the value of a cell to stripped text, but leave it
    None if it is.
    """
    if cell:
        return str(cell).strip()
    else:
        return None


def clean_portal(text):
    """clean_portal makes the text for the portal output clean.
    Currently only unicode 805 character is replaced with 778.
    """
    return text.replace(chr(805), chr(778))


class Entry:
    """The Entry class contains information needed to create dictionary entries.  These can be printed in the form useful for the dictionary portal and dictionary app as well as in LaTeX form.
    """
    # Entry_type indicates where particular information is stored. For
    # instance, this could indicate n_uu (=GLOBAL), n_uu_east (=EAST), or
    # n_uu_west (=WEST).
    Entry_type = Enum("Entry_type", "GLOBAL EAST WEST")

    # Lang_type indicates the language that should be considered.
    Lang_type = Enum("Lang_type", "NUU NAMA AFRIKAANS ENGLISH")

    def lang_name(lang):
        if lang == Entry.Lang_type.NUU:
            return "N|uu"
        elif lang == Entry.Lang_type.NAMA:
            return "Nama"
        elif lang == Entry.Lang_type.AFRIKAANS:
            return "Afr"
        elif lang == Entry.Lang_type.ENGLISH:
            return "Eng"

    def lang_name_latex(lang):
        if lang == Entry.Lang_type.NUU:
            return "N$|$uu"
        elif lang == Entry.Lang_type.NAMA:
            return "Nama"
        elif lang == Entry.Lang_type.AFRIKAANS:
            return "Afr"
        elif lang == Entry.Lang_type.ENGLISH:
            return "Eng"

    def __init__(self, n_uu, n_uu_east, n_uu_west, pos, ipa, ipa_east, ipa_west,
            english, par_english, afrikaans, par_afrikaans, nama, par_nama, line_nr):
        """An Entry needs to be introduced using the fields that are required
        for output.  Note that a least one of n_uu, n_uu_east, n_uu_west needs
        to be filled (otherwise an exception is raised).  If none of ipa,
        ipa_east, ipa_west is filled, a warning is written on the logging
        channel, similarly if english, afrikaans, or nama (or any
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

        self.pos = pos

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

        # Check whether Nama information is present.
        if not nama:
            logging.warning("Missing Nama on line " + self.line_nr + " in " + self.key)
        self.nama = nama
        self.par_english = par_english
        self.par_afrikaans = par_afrikaans
        self.par_nama = par_nama


    def __str__(self):
        """__str__ provides printable output.
        """
        return "Entry(n_uu=" + str(self.n_uu) + ", n_uu_east=" + str(self.n_uu_east) + ", n_uu_west=" + str(self.n_uu_west) + ", pos=" + str(self.pos) + ", ipa=" + str(self.ipa) + ", ipa_east=" + str(self.ipa_east) + ", ipa_west=" + str(self.ipa_west) + ", english=" + str(self.english) + ", afrikaans=" + str(self.afrikaans) + ", Nama=" + str(self.nama) + ", line_nr=" + str(self.line_nr) + ")"

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
            fp.write("<N|uu>" + clean_portal(self.n_uu) + "\n")
        if self.n_uu_east:
            fp.write("<N|uu East>" + clean_portal(self.n_uu_east) + "\n")
        if self.n_uu_west:
            fp.write("<N|uu West>" + clean_portal(self.n_uu_west) + "\n")
        if self.pos:
            fp.write("<POS>" + clean_portal(self.pos) + "\n")
        if self.ipa:
            fp.write("<IPA>" + clean_portal(self.ipa) + "\n")
        if self.ipa_east:
            fp.write("<IPA East>" + clean_portal(self.ipa_east) + "\n")
        if self.ipa_west:
            fp.write("<IPA West>" + clean_portal(self.ipa_west) + "\n")
        if self.english:
            fp.write("<English>" + clean_portal(self.english) + "\n")
        if self.afrikaans:
            fp.write("<Afrikaans>" + clean_portal(self.afrikaans) + "\n")
        if self.nama:
            fp.write("<Nama>" + clean_portal(self.nama) + "\n")
        fp.write("**\n")


    def write_latex(self, fp, lang, sublang):
        """ write_latex writes the information of the entry to fp
        while taking the language of lang (with sublang available when
        lang == NUU) as head word.
        """
        hw_extra = ""
        ipa = None
        # Grab the right headword and other information
        if lang == self.Lang_type.NUU:
            if sublang == self.Entry_type.GLOBAL:
                ipa = self.ipa
                headword = self.n_uu
            elif sublang == self.Entry_type.EAST:
                headword = self.n_uu_east
                hw_extra += " (Eastern)"
                ipa = self.ipa_east
            elif sublang == self.Entry_type.WEST:
                headword = self.n_uu_west
                hw_extra += " (Western)"
                ipa = self.ipa_west
        elif lang == self.Lang_type.NAMA:
            headword = self.nama
        elif lang == self.Lang_type.AFRIKAANS:
            headword = self.afrikaans
        elif lang == self.Lang_type.ENGLISH:
            headword = self.english
        pos = self.pos
        # build other language text
        other_lang = []
        for l in self.Lang_type:
            if l != lang:
                if l == self.Lang_type.NUU:
                    other_lang.append((self.n_uu, l))
                elif l == self.Lang_type.NAMA:
                    other_lang.append((self.nama, l))
                elif l == self.Lang_type.AFRIKAANS:
                    other_lang.append((self.afrikaans, l))
                elif l == self.Lang_type.ENGLISH:
                    other_lang.append((self.english, l))
        write_latex_data(fp, headword, hw_extra, ipa, pos, other_lang, self.par_nama, self.par_afrikaans, self.par_english)



class Dictionary:
    """The Dictionary class stores all information for the dictionary.  It
    checks whether all the required information is present.
    """

    # Entries contains the list of dictionary entries (instances of the
    # Entry class).  The position in this list is used in the mappings
    # (below).
    entries = []
    # Lemma_type is a mapping from a lemma (n_uu word) to the field the
    # lemma is found in (general=n_uu, east=n_uu_east, west=n_uu_west).
    lemma_type = {}
    # The mappings map a key to the entry (index) in the entries variable.
    lang_map = {}
    for lang in Entry.Lang_type:
        lang_map[lang] = {}


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


    def insert(self, n_uu, n_uu_east, n_uu_west, pos, ipa, ipa_east, ipa_west, english, par_english, afrikaans, par_afrikaans, nama, par_nama, line_nr):
        """Create and add the entry to the entries list. Len(self.entries)
        provides the index of the new entry.
        """
        # Add information to entries
        self.entries.append(Entry(n_uu, n_uu_east, n_uu_west, pos, ipa, ipa_east, ipa_west, english, par_english, afrikaans, par_afrikaans, nama, par_nama, line_nr))

        if (n_uu and n_uu_east) or (n_uu and n_uu_west):
            logging.warning("Both N|uu and N|uu east or west on line " + str(line_nr))

        new_index = len(self.entries) - 1 # Get index which is length - 1

        self.check_add_map(n_uu, Entry.Lang_type.NUU, new_index, line_nr)
        if n_uu != None:
            if n_uu in self.lemma_type and self.lemma_type[n_uu] != Entry.Entry_type.GLOBAL:
                logging.error("Found " + str(n_uu) + " as " + str(self.lemma_type[n_uu]) + " and " + str(Entry.Entry_type.GLOBAL))
            self.lemma_type[n_uu] = Entry.Entry_type.GLOBAL

        self.check_add_map(n_uu_east, Entry.Lang_type.NUU, new_index, line_nr)
        if n_uu_east != None:
            if n_uu_east in self.lemma_type and self.lemma_type[n_uu_east] != Entry.Entry_type.EAST:
                logging.error("Found " + str(n_uu_east) + " as " + str(self.lemma_type[n_uu_east]) + " and " + str(Entry.Entry_type.EAST))
            self.lemma_type[n_uu_east] = Entry.Entry_type.EAST

        self.check_add_map(n_uu_west, Entry.Lang_type.NUU, new_index, line_nr)
        if n_uu_west != None:
            if n_uu_west in self.lemma_type and self.lemma_type[n_uu_west] != Entry.Entry_type.WEST:
                logging.error("Found " + str(n_uu_west) + " as " + str(self.lemma_type[n_uu_west]) + " and " + str(Entry.Entry_type.WEST))
            self.lemma_type[n_uu_west] = Entry.Entry_type.WEST


        self.check_add_map(english, Entry.Lang_type.ENGLISH, new_index, line_nr)
        self.check_add_map(afrikaans, Entry.Lang_type.AFRIKAANS, new_index, line_nr)
        self.check_add_map(nama, Entry.Lang_type.NAMA, new_index, line_nr)


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
        afrikaans_loc = convert_to_string(line["Afrikaans community feedback Local Variety "])
        par_afrikaans = convert_to_string(line["Afrik Parentheticals"])
        nama = convert_to_string(line["Nama Feedback"])
        par_nama = convert_to_string(line["Nama Parentheticals"])

        # Parse the N|uu and IPA entries as there may be eastern and
        # western values in there.
        n_uu, n_uu_east, n_uu_west = self.parse(orthography, "Orthography 1", line_nr)
        ipa, ipa_east, ipa_west = self.parse(ipa, "IPA", line_nr)
        # TODO afrikaans_loc handling
        if afrikaans_loc:
            afrikaans += " " + afrikaans_loc
        self.insert(n_uu, n_uu_east, n_uu_west, pos, ipa, ipa_east, ipa_west, english, par_english, afrikaans, par_afrikaans, nama, par_nama, line_nr)


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
