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
        # skip - if present
        while i_self != l_self and sword[i_self] in "-" + chr(9790):
            i_self += 1
        # skip - if present
        while i_other != l_other and oword[i_other] in "-" + chr(9790):
            i_other += 1
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
