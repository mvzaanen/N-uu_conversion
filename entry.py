#!/usr/bin/env python3
"""entry.py

This file contains the implementation of the Entry class, which
represents an entry in the dictionary (spreadsheet).
"""

from enum import Enum
from headword import Headword
import logging
from output_helper import clean_portal, clean_latex_text, clean_latex_ipa, latex_cut


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
            return "Afr$^{\\mbox{\\footnotesize{ons}}}$"
        elif lang == Entry.Lang_type.ENGLISH:
            return "Eng"


    def lang2latex_long(lang):
        if lang == Entry.Lang_type.NUU:
            return "N$|$uuki"
        elif lang == Entry.Lang_type.IPA:
            return "IPA"
        elif lang == Entry.Lang_type.NAMA:
            return "Namagowab"
        elif lang == Entry.Lang_type.AFRIKAANS:
            return "Afrikaans"
        elif lang == Entry.Lang_type.AFR_LOC:
            return "Afr$^{\\mbox{\\footnotesize{ons}}}$"
        elif lang == Entry.Lang_type.ENGLISH:
            return "English"


    pos2text_map = {
            "" : "MISSING",
            "noun" : "T1",
            "verb" : "T2",
            "particle" : "T3",
            "noun phrase" : "T1a",
            "noun, proper, personal" : "T1b",
            "noun, proper, place" : "T1b",
            "verb phrase" : "T2a",
            "pronoun" : "T4",
            "phrase, greeting" : "T5",
            "interrogative" : "T6",
            "adverb" : "T7",
            "phrase" : "T5",
            "noun, proper" : "T1b",
            "numeral" : "T8",
            "noun, proper, place, river" : "T1b",
            "interjection" : "T9",
            "adjective" : "T10",
            "quantifier" : "T11",
            "particle, adjective" : "T3, T10",
            "verb (transitive)" : "T2",
            "verb, particle" : "T2, T3",
            "verb, noun" : "T1, T2",
            "verb, interjection" : "T2, T9",
            "verb, adjective" : "T2, T10",
            "noun; verb" : "T1, T2",
            "noun, verb" : "T1, T2",
            "noun, particle" : "T1, T3",
            }


    def pos2text(pos):
        return Entry.pos2text_map[pos]


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


    def get_portal(self):
        """get_portal returns a string of the entry to fp so the
        information can be incorporated in the dictionary portal.
        """
        result = "**\n"
        result += "<Project>N|uu dictionary\n"
        for lang in self.headwords:
            result += "<" + Entry.lang2text(lang) + ">"
            result += "\n<synonym>".join(map(clean_portal, self.headwords[lang]))
            result += "\n"
        result += "<POS>" + Entry.pos2text(self.pos) + "\n"
        for lang in self.parentheticals:
            result += "<" + Entry.lang2text(lang) + " par>"
            result += clean_portal(self.parentheticals[lang])
            result += "\n"
        result += "**\n"
        return result


    def get_latex(self, headword, lang):
        """get_latex returns a string of the information of the entry 
        in LaTeX format.  The lemma will be based on the headword
        which is found in the language lang.  This will not work if
        lang is Lang_type.IPA as that requires special treatment.
        """
        result = ""
        # find index of headword in Entry
        index = self.headwords[lang].index(headword)
        main = clean_latex_text(headword.get_word())
        marker = Headword.marker2text(headword.get_marker())
        if marker != "":
            main += " (" + marker + ")"

        result += "\\entry{"
        result += latex_cut(main, 45)
        result += "}{"
        result += "\\textbf{" + main
        result += "}"

        # write the other headwords
        if len(self.headwords[lang]) != 1:
            result += ", " + ", ".join(map(clean_latex_text, map(str, [hw for hw in self.headwords[lang] if hw != headword])))

        if lang == Entry.Lang_type.AFRIKAANS: # write AFR_LOC after AFRIKAANS
            if Entry.Lang_type.AFR_LOC in self.headwords:
                result += " \\underbar{" + Entry.lang2latex(Entry.Lang_type.AFR_LOC)+ "}: "
                result += ", ".join(map(clean_latex_text, map(str, self.headwords[Entry.Lang_type.AFR_LOC]))) + " "

        result += "}{"

        # write POS
        result += "(" + clean_latex_text(Entry.pos2text(self.pos)) + ")"
        result += "}{"

        if lang == Entry.Lang_type.NUU: # write IPA after N|uu
            if Entry.Lang_type.IPA in self.headwords: # do we have IPA?
                # reorder based on index of headword
                ipa_ordered = self.headwords[Entry.Lang_type.IPA][:]
                try:
                    ipa_ordered.insert(0, ipa_ordered.pop(index))
                except IndexError:
                    logging.error("Different number of N|uu and IPA entries on line " + str(self.line_nr))
                result += "[\\textipa{"
                result += ", ".join(map(clean_latex_ipa, map(str, ipa_ordered)))
                result += "}]"
        result += "}{"

        # do the other languages
        lang_order = [Entry.Lang_type.NUU, Entry.Lang_type.IPA, Entry.Lang_type.NAMA, Entry.Lang_type.AFRIKAANS, Entry.Lang_type.AFR_LOC, Entry.Lang_type.ENGLISH]
        for l in lang_order:
            # Skip AFR_LOC if the language is AFRIKAANS (as that is
            # part of the main entry)
            if not (lang == Entry.Lang_type.AFRIKAANS and l == Entry.Lang_type.AFR_LOC):
                if l != lang and l != Entry.Lang_type.IPA and l in self.headwords:
                    result += "\\underbar{" + Entry.lang2latex(l)+ "}: "
                    result += ", ".join(map(clean_latex_text, map(str, self.headwords[l]))) + " "
        result += "}{"
        # do the other parentheticals
        # move current language to the front of the list (i.e., do first)
        lang_order.insert(0, lang_order.pop(lang_order.index(lang)))
        for l in lang_order:
            if l != Entry.Lang_type.IPA and l in self.parentheticals:
                result += "\\underbar{\\textit{" + Entry.lang2latex(l) + "}}: "
                result += clean_latex_text(self.parentheticals[l]) + " "
        result += "}"
        result += "\n\n"
        return result
