#!/usr/bin/env python3
"""entry.py

This file contains the implementation of the Entry class, which
represents an entry in the dictionary (spreadsheet).
"""

from enum import Enum
import logging
from output_helper import clean_portal, clean_latex_text, clean_latex_ipa


def write_latex_data(fp, headword, hw_extra, ipa, pos, other_lang, par_nama, par_afrikaans, par_english):
    """write_latex_data writes the information into LaTeX form to fp.
    """
    fp.write("\\begin{entry}\n")
    fp.write("\\textbf{" + clean_latex_text(headword) + "}\n")
    if hw_extra:
        fp.write(clean_latex_text(hw_extra) + "\n")
    if ipa:
        fp.write("[\\textipa{" + clean_latex_ipa(ipa) + "}]\n")
    fp.write("(" + clean_latex_text(pos) + ");\n")
    for (text, lang) in other_lang:
        fp.write("\\underbar{" + Entry.lang_name_latex(lang)+ "}: " + clean_latex_text(text) + ";\n")
    fp.write("\\newline\n")
    if par_nama:
        fp.write("\\small{\\underbar{Nama}: " + clean_latex_text(par_nama) + "}\\newline\n")
    if par_afrikaans:
        fp.write("\\small{\\underbar{Afr}: " + clean_latex_text(par_afrikaans) + "}\\newline\n")
    if par_english:
        fp.write("\\small{\\underbar{Eng}: " + clean_latex_text(par_english) + "}\\newline\n")
    fp.write("\\end{entry}\n")
    fp.write("\n\n")



class Entry:
    """The Entry class contains information needed to create dictionary entries.  These can be printed in the form useful for the dictionary portal and dictionary app as well as in LaTeX form.
    """
    # Marker_type indicates where particular information is stored. For
    # instance, this could indicate n_uu (=NONE), n_uu_east (=EAST), or
    # n_uu_west (=WEST).
    Marker_type = Enum("Marker_type", "NONE EAST WEST")

    # Lang_type indicates the language that should be considered.
    Lang_type = Enum("Lang_type", "NUU NAMA AFRIKAANS AFR_LOC ENGLISH")

    def lang_name(lang):
        if lang == Entry.Lang_type.NUU:
            return "N|uu"
        elif lang == Entry.Lang_type.NAMA:
            return "Nama"
        elif lang == Entry.Lang_type.AFRIKAANS:
            return "Afr"
        elif lang == Entry.Lang_type.AFR_LOC:
            return "Afr loc"
        elif lang == Entry.Lang_type.ENGLISH:
            return "Eng"

    def lang_name_latex(lang):
        if lang == Entry.Lang_type.NUU:
            return "N$|$uu"
        elif lang == Entry.Lang_type.NAMA:
            return "Nama"
        elif lang == Entry.Lang_type.AFRIKAANS:
            return "Afr"
        elif lang == Entry.Lang_type.AFR_LOC:
            return "Afr$^{\\mbox{\\footnotesize}loc}$"
        elif lang == Entry.Lang_type.ENGLISH:
            return "Eng"

    def __init__(self, n_uu, n_uu_east, n_uu_west, pos, ipa, ipa_east, ipa_west,
            english, par_english, afrikaans, par_afrikaans, afr_loc, nama, par_nama, line_nr):
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
        self.afr_loc = afr_loc

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
        if self.afr_loc:
            fp.write("<Afr_loc>" + clean_portal(self.afr_loc) + "\n")
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
            if sublang == self.Marker_type.NONE:
                ipa = self.ipa
                headword = self.n_uu
            elif sublang == self.Marker_type.EAST:
                headword = self.n_uu_east
                hw_extra += " (Eastern)"
                ipa = self.ipa_east
            elif sublang == self.Marker_type.WEST:
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
                if l == self.Lang_type.NUU: # TODO check on empty
                    other_lang.append((self.n_uu, l))
                elif l == self.Lang_type.NAMA and self.nama:
                    other_lang.append((self.nama, l))
                elif l == self.Lang_type.AFRIKAANS and self.afrikaans:
                    other_lang.append((self.afrikaans, l))
                elif l == self.Lang_type.AFR_LOC and self.afr_loc:
                    other_lang.append((self.afr_loc, l))
                elif l == self.Lang_type.ENGLISH and self.english:
                    other_lang.append((self.english, l))
        write_latex_data(fp, headword, hw_extra, ipa, pos, other_lang, self.par_nama, self.par_afrikaans, self.par_english)

