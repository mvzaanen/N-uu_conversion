#!/usr/bin/env python3
"""headword.py

This file contains the implementation of the Headword class, which
represents one particular word that can function as a headword in the
dictionary.
"""

class Headword:
    """The Headword class contains information that is needed to
    represent a headword. A headword consists of a word (text) and
    possibly a label (Marker_type) indicating for instance dialect
    information (which is not the same as langauge).
    """
    # Marker_type indicates where particular information is stored. For
    # instance, this could indicate n_uu (=NONE), n_uu_east (=EAST), or
    # n_uu_west (=WEST).
    Marker_type = Enum("Marker_type", "NONE EAST WEST")

    def marker2text(marker):
        if marker == Marker_type.NONE:
            return ""
        elif marker == Marker_type.EAST:
            return "east"
        elif marker == Marker_type.WEST:
            return "west"

    def __init__(self, word, marker):
        """A Headword contains a word and a dialect marker.
        """
        self.word = word
        self.marker = marker

    def __str__(self):
        """__str__ provides printable output.
        """
        return str(self.word) + " (" + marker2text(self.marker) + ")"

    def __lt__(self, other):
        """__lt__ implements comparison for (alphabetic) ordering.
        """
        return self.word < other.word

    def write_portal(self, fp):
        """write_portal writes the headword to fp so the information can
        be incorporated in the dictionary portal.
        """
        fp.write(clean_portal(self.word) + " (" + marker2text(self.marker) + ")"

    def write_latex(self, fp):
        """write_latex writes the headword to fp so the information can
        be incorporated in a LaTeX file.
        """
        fp.write(clean_portal(clean_latex_text(self.word)) + " (" + marker2text(self.marker) + ")"
