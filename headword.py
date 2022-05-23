#!/usr/bin/env python3
"""headword.py

This file contains the implementation of the Headword class, which
represents one particular word that can function as a headword in the
dictionary.
"""

from enum import Enum
from output_helper import is_above


class Headword:
    """The Headword class contains information that is needed to
    represent a headword. A headword consists of a word (text) and
    possibly a label (Marker_type) indicating for instance dialect
    information (which is not the same as langauge).
    """

    # Marker_type indicates where particular information is stored. For
    # instance, this could indicate n_uu (=NONE), n_uu_east (=EAST), or
    # n_uu_west (=WEST).
    Marker_type = Enum("Marker_type", "EAST WEST NONE")


    def marker2text(marker):
        if marker == Headword.Marker_type.NONE:
            return ""
        elif marker == Headword.Marker_type.EAST:
            return "Eastern"
        elif marker == Headword.Marker_type.WEST:
            return "Western"


    def marker2latex(marker):
        if marker == Headword.Marker_type.NONE:
            return ""
        elif marker == Headword.Marker_type.EAST:
            return "Eastern"
        elif marker == Headword.Marker_type.WEST:
            return "Western"


    def __init__(self, word, marker):
        """A Headword contains a word and a dialect marker.
        """
        self.word = word
        self.marker = marker


    def __str__(self):
        """__str__ provides printable output.
        """
        result = str(self.word)
        if self.marker != Headword.Marker_type.NONE:
            result += " (" + Headword.marker2text(self.marker) + ")"
        return result

    def skip_words(word, i):
        # skip -, `, space, and LAST QUARTER MOON (9790) if present
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
        if i < l and word[i] in "- `'(" + chr(9790):
            return (i + 1, True)
        return (i, False)

    sort_order = {
            "a" : 1,
            "ā" : 1,
            "â" : 1,
            "b" : 2,
            "c" : 3,
            "d" : 4,
            "e" : 5,
            "ē" : 5,
            "ê" : 5,
            "ë" : 5,
            "f" : 6,
            "g" : 7,
            "h" : 8,
            "i" : 9,
            "ī" : 9,
            "î" : 9,
            "j" : 10,
            "k" : 11,
            "l" : 12,
            "m" : 13,
            "n" : 14,
            "o" : 15,
            "ō" : 15,
            "ô" : 15,
            "p" : 16,
            "q" : 17,
            "r" : 18,
            "s" : 19,
            "t" : 20,
            "u" : 21,
            "ū" : 21,
            "û" : 21,
            "v" : 22,
            "w" : 23,
            "x" : 24,
            "y" : 25,
            "z" : 26,
            "ʘ" : 27,
            "ǀ" : 28,
            "ǁ" : 29,
            "ǃ" : 30,
            "!" : 30,
            "ǂ" : 31,
            " " : ord(" ") + 99,
            "," : ord(",") + 99,
            "-" : ord("-") + 99,
            "\'" : ord("\'") + 99,
            "`" : ord("`") + 99,
            "(" : ord("(") + 99,
            ")" : ord(")") + 99,
            "?" : ord("?") + 99,
            "/" : ord("/") + 99,
            "ʼ" : ord("ʼ") + 99,
            "’" : ord("’") + 99,
            "☾" : ord("☾") + 99,
            }



    def __lt__(self, other):
        """__lt__ compares alphabetically on headword.
        """
        sword = self.word.lower()
        oword = other.word.lower()
        if sword == oword:
            return False
        i_self = 0
        l_self = len(sword)
        i_other = 0
        l_other = len(oword)
        # Find words need to be skipped for sword
        (i_self, skipped) = Headword.skip_words(sword, i_self)
        while skipped:
            (i_self, skipped) = Headword.skip_words(sword, i_self)
        # Find words need to be skipped for oword
        (i_other, skipped) = Headword.skip_words(oword, i_other)
        while skipped:
            (i_other, skipped) = Headword.skip_words(oword, i_other)
        # find point where the words are different
        different = False
        while not different:
            if i_self != l_self and i_other != l_other and sword[i_self] == oword[i_other]:
                i_self += 1
                i_other += 1
            elif i_self != l_self and sword[i_self] not in Headword.sort_order:
                if not is_above(ord(sword[i_self])):
                    print("skipping i_self " + str(i_self) + " in " + str(sword))
                i_self += 1
            elif i_other != l_other and oword[i_other] not in Headword.sort_order:
                if not is_above(ord(oword[i_other])):
                    print("skipping i_other " + str(i_other) + " in " + str(oword))
                i_other += 1
            else:
                different = True
        try:
            if i_self == l_self or i_other == l_other:
                return l_self < l_other
            else:
                return Headword.sort_order[sword[i_self]] < Headword.sort_order[oword[i_other]]
        except:
            print(sword)
            print(oword)



    def get_word(self):
        """get_word provides word of the headword.
        """
        return self.word


    def get_marker(self):
        """get_marker provides marker of the headword.
        """
        return self.marker
