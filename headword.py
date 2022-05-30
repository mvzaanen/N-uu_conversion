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


    def get_word(self):
        """get_word provides word of the headword.
        """
        return self.word


    def get_marker(self):
        """get_marker provides marker of the headword.
        """
        return self.marker
