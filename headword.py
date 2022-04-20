#!/usr/bin/env python3
"""headword.py

This file contains the implementation of the Headword class, which
represents one particular word that can function as a headword in the
dictionary.
"""

from enum import Enum


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
        while i_self != l_self and i_other != l_other and sword[i_self] == oword[i_other]:
            i_self += 1
            i_other += 1
        if i_self == l_self or i_other == l_other:
            return l_self < l_other
        else:
            return sword[i_self] < oword[i_other]


    def get_word(self):
        """get_word provides word of the headword.
        """
        return self.word


    def get_marker(self):
        """get_marker provides marker of the headword.
        """
        return self.marker
