#!/usr/bin/env python3
"""entry.py

This file contains the implementation of the Entry class, which
represents an entry in the dictionary (spreadsheet).
"""

from enum import Enum
from headword import Headword
import logging
from output_helper import clean_portal, clean_portal_text, clean_latex_text, clean_latex_ipa, latex_cut
import re


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
            return "Afrikaans"
        elif lang == Entry.Lang_type.AFR_LOC:
            return "Afr loc"
        elif lang == Entry.Lang_type.ENGLISH:
            return "English"


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


    def __init__(self, headwords, pos, parentheticals, audio_word, audio_sentence, line_nr):
        """An Entry needs to be introduced using the fields that are required
        for output.  headwords contains a dictionary with Lang_type as
        keys and lists of headwords as values. POS is a pos type.
        parentheticals is also a dictionary with Lang_type as keys and
        as values a string.  line_nr is the line the entry is found in.
        audio_word and audio_sentence contain references to audio
        files of individual words or sentences respectively.
        """
        self.line_nr = str(line_nr)
        self.headwords = headwords
        self.pos = pos
        self.parentheticals = parentheticals
        self.audio_word = audio_word
        self.audio_sentence = audio_sentence


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


    def get_hidden(self, lang):
        """get_hidden returns a list of words that the user should also be able
        to search for, based on the contents of the headwords.  Select
        only those for language lang.
        """
        result = []
        if lang == Entry.Lang_type.NUU:
            to_split = []
            for hw in self.headwords[Entry.Lang_type.NUU]:
                if Headword.marker2text(hw.get_marker()) != "": # words that have markers need to be added
                    to_split.append(hw.get_word())
            for word in to_split:
                hidden_words = set()
                for subword in re.split(" |,", word):
                    if len(subword) > 1 and subword != "(Western)" and subword != "(Eastern)":
                        hidden_words.add(subword)
                result += list(hidden_words)
        else:
            to_check = []
            if lang in self.headwords:
                to_check = self.headwords[lang]
            hidden_words = set()
            for hw in to_check:
                for subword in re.split(" |,|'|`|\)|\(", hw.get_word()):
                    if subword != hw.get_word() and len(subword) > 1 and subword != "NKK:" and subword[-1] != ".":
                        hidden_words.add(subword)
            result += list(hidden_words)
        return result


    def get_portal(self):
        """get_portal returns a string of the entry to fp so the
        information can be incorporated in the dictionary portal.
        """
        result = "**\n"
        result += "<Project>N|uu dictionary\n"
        # Fields should be ordered as follows:
        #<N|uu>						N|uu
        #<Synonym>					N|uu synonyms
        #<IPA>						IPA
        #<IPA>						IPA synonyms (field is also IPA)
        #<Part of speech>				Part of speech
        #<Afr loc>					Afr loc
        #<Afr loc>					Afr loc synonyms (field is also Afr loc)
        #<Additional Nama information>			Additional Nama information
        #<Additional Afrikaans information>		Additional Afrikaans information
        #<Additional English information>		Additional English information
        #<Sound>					Sound
        #<Nama>					Nama
        #<Synonym> 					Nama synonyms 
        #<Afrikaans>					Afrikaans
        #<Synonym> 					Afrikaans synonyms 
        #<English>					English
        #<Synonym> 					English synonyms 
        #<Hidden>					Hidden field
        #<Synonym>					Hidden extra field, if more than one hidden field is required

        # N|uu
        result += "<N|uu>"
        result += "\n<Synonym>".join(map(clean_portal_text, self.headwords[Entry.Lang_type.NUU]))
        result += "\n"
        # IPA
        result += "<IPA>"
        result += "\n<IPA>".join(map(clean_portal, self.headwords[Entry.Lang_type.IPA]))
        result += "\n"
        # POS
        result += "<Part of speech>" + Entry.pos2text(self.pos) + "\n"
        # AFR LOC
        if Entry.Lang_type.AFR_LOC in self.headwords:
            result += "<Afr loc>"
            result += "\n<Afr loc>".join(map(clean_portal_text, self.headwords[Entry.Lang_type.AFR_LOC]))
            result += "\n"
        # Nama parentheticals
        if Entry.Lang_type.NAMA in self.parentheticals:
            result += "<Additional Nama information>"
            result += clean_portal_text(self.parentheticals[Entry.Lang_type.NAMA])
            result += "\n"
        # Afrikaans parentheticals
        if Entry.Lang_type.AFRIKAANS in self.parentheticals:
            result += "<Additional Afrikaans information>"
            result += clean_portal_text(self.parentheticals[Entry.Lang_type.AFRIKAANS])
            result += "\n"
        # English parentheticals
        if Entry.Lang_type.ENGLISH in self.parentheticals:
            result += "<Additional English information>"
            result += clean_portal_text(self.parentheticals[Entry.Lang_type.ENGLISH])
            result += "\n"
        # Sound
        if self.audio_word:
            for f in re.split(" *[,;] *", self.audio_word):
                if f != "--" and f != "":
                    result += "<Sound>" + f + ".wav\n"
        # Nama
        result += "<Nama>"
        result += "\n<Synonym>".join(map(clean_portal_text, self.headwords[Entry.Lang_type.NAMA]))
        result += "\n"
        # Afrikaans
        result += "<Afrikaans>"
        result += "\n<Synonym>".join(map(clean_portal_text, self.headwords[Entry.Lang_type.AFRIKAANS]))
        result += "\n"
        # English
        result += "<English>"
        result += "\n<Synonym>".join(map(clean_portal_text, self.headwords[Entry.Lang_type.ENGLISH]))
        result += "\n"
        # HIDDEN
        hidden_words = Entry.get_hidden(self, Entry.Lang_type.NUU)
        if len(hidden_words) != 0:
            result += "<Hidden N|uu>"
            result += "\n<Synonym>".join(map(clean_portal_text, hidden_words))
            result += "\n"
        hidden_words = Entry.get_hidden(self, Entry.Lang_type.NAMA)
        if len(hidden_words) != 0:
            result += "<Hidden Nama>"
            result += "\n<Synonym>".join(map(clean_portal_text, hidden_words))
            result += "\n"
        hidden_words = Entry.get_hidden(self, Entry.Lang_type.AFRIKAANS)
        if len(hidden_words) != 0:
            result += "<Hidden Afrikaans>"
            result += "\n<Synonym>".join(map(clean_portal_text, hidden_words))
            result += "\n"
        hidden_words = Entry.get_hidden(self, Entry.Lang_type.AFR_LOC)
        if len(hidden_words) != 0:
            result += "<Hidden Afr loc>"
            result += "\n<Synonym>".join(map(clean_portal_text, hidden_words))
            result += "\n"
        hidden_words = Entry.get_hidden(self, Entry.Lang_type.ENGLISH)
        if len(hidden_words) != 0:
            result += "<Hidden English>"
            result += "\n<Synonym>".join(map(clean_portal_text, hidden_words))
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
        result += latex_cut(main, 30)
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
