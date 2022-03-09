#!/usr/bin/env python3
"""entry.py

This file contains the implementation of the Entry class, which
represents an entry in the dictionary (spreadsheet).
"""

from enum import Enum
from headword import Headword
import logging
from output_helper import clean_portal, clean_latex_text, clean_latex_ipa


class Entry:
    """The Entry class contains information needed to create dictionary entries.  These can be printed in the form useful for the dictionary portal and dictionary app as well as in LaTeX form.
    """
    # Lang_type indicates the language that should be considered.
    # Note that we encode IPA as a language, as the IPA entries behave
    # similarly to headwords.
    Lang_type = Enum("Lang_type", "NUU IPA NAMA AFRIKAANS AFR_LOC ENGLISH")

    def lang2text(lang):
        if lang == Entry.Lang_type.NUU:
            return "N|uu"
        elif lang == Entry.Lang_type.IPA:
            return "IPA"
        elif lang == Entry.Lang_type.NAMA:
            return "Nama"
        elif lang == Entry.Lang_type.AFRIKAANS:
            return "Afr"
        elif lang == Entry.Lang_type.AFR_LOC:
            return "Afr loc"
        elif lang == Entry.Lang_type.ENGLISH:
            return "Eng"

    def lang2latex(lang):
        if lang == Entry.Lang_type.NUU:
            return "N$|$uu"
        elif lang == Entry.Lang_type.IPA:
            return "IPA"
        elif lang == Entry.Lang_type.NAMA:
            return "Nama"
        elif lang == Entry.Lang_type.AFRIKAANS:
            return "Afr"
        elif lang == Entry.Lang_type.AFR_LOC:
            return "Afr$^{\\mbox{\\footnotesize}loc}$"
        elif lang == Entry.Lang_type.ENGLISH:
            return "Eng"

    def __init__(self, headwords, pos, parentheticals, line_nr):
        """An Entry needs to be introduced using the fields that are required
        for output.  headwords contains a dictionary with Lang_type as
        keys and lists of headwords as values. POS is a pos type.
        parentheticals is also a dictionary with Lang_type as keys and
        as values a string.  line_nr is the line the entry is found in.
        """
        self.line_nr = str(line_nr)
        self.headwords = headwords
        self.pos = pos
        self.parentheticals = parentheticals


    def __str__(self):
        """__str__ provides printable output.
        """
        result = "Entry("
        for lang in self.headwords:
            result += Entry.lang2text(lang) + "("
            result += ", ".join(map(str, self.headwords[lang]))
            result += ") "
        result += "POS(" + self.pos + ") "
        for lang in self.parentheticals:
            result += Entry.lang2text(lang) + "("
            result += self.parentheticals[lang]
            result += ") "
        result += self.line_nr
        return result


    def write_portal(self, fp):
        """write_portal writes the entry to fp so the information can
        be incorporated in the dictionary portal.
        """
        fp.write("**\n")
        fp.write("<Project>N|uu dictionary\n")
        for lang in self.headwords:
            fp.write("<" + Entry.lang2text(lang) + ">")
            fp.write(", ".join(map(str, self.headwords[lang])))
            fp.write("\n")
        fp.write("<POS>" + self.pos + "\n")
        for lang in self.parentheticals:
            fp.write("<" + Entry.lang2text(lang) + " par>")
            fp.write(self.parentheticals[lang])
            fp.write("\n")
        fp.write("**\n")


    def write_latex(self, fp, headword, lang):
        """write_latex writes the entry to fp so the
        information can be incorporated in a LaTeX file.  The lemma
        will be based on the headword which is found in the language
        lang.  This will not work if lang is Lang_type.IPA as that
        requires special treatment.
        """
        fp.write("\\begin{entry}\n")
        fp.write("\\textbf{" + clean_latex_text(headword.get_word()) + "}")
        marker = Headword.marker2text(headword.get_marker())
        if marker != "":
            fp.write(" (" + marker + ")")

        # write the other headwords
        fp.write(", " + ", ".join(map(clean_latex_text, map(str, [hw for hw in self.headwords[lang] if hw != headword]))) + "\n")

        if lang == Entry.Lang_type.NUU: # write IPA after N|uu
            if Entry.Lang_type.IPA in self.headwords: # do we have IPA?
                fp.write("[\\textipa{")
                fp.write(", ".join(map(clean_latex_ipa, map(str, self.headwords[Entry.Lang_type.IPA]))))
                fp.write("}]\n")

        # write POS
        fp.write("(" + clean_latex_text(self.pos) + ");\n")

        # do the other languages
        for l in Entry.Lang_type:
            if l != lang and l != Entry.Lang_type.IPA and l in self.headwords:
                fp.write("\\underbar{" + Entry.lang2latex(l)+ "}: ")
                fp.write(", ".join(map(clean_latex_text, map(str, self.headwords[l]))) + "\n")
        fp.write("\\newline\n")
        # do the other parentheticals
        for l in Entry.Lang_type:
            if l != lang and l != Entry.Lang_type.IPA and l in self.parentheticals:
                fp.write("\\underbar{" + Entry.lang2latex(l)+ "}: ")
                fp.write(clean_latex_text(self.parentheticals[l]) + "\n")
        fp.write("\\end{entry}\n")
        fp.write("\n\n")
