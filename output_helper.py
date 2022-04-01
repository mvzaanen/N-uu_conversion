#!/usr/bin/env python3
"""output_helper.py

This file contains helper functions to convert dictionary information to
output. Currently, LaTeX and dicionary app output is provided.
"""


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
    10 : " ", # line feed, mapping to space
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
    332 : "\\={O}", # LATIN CAPITAL LETTER O WITH MACRON
    333 : "\\={o}", # LATIN SMALL LETTER O WITH MACRON
    362 : "\\={U}", # LATIN CAPITAL LETTER U WITH MACRON
    363 : "\\={u}", # LATIN SMALL LETTER U WITH MACRON
    448 : "\\textipa{\\textvertline}", # LATIN LETTER DENTAL CLICK
    449 : "\\textipa{\\textdoublevertline}", # LATIN LETTER LATERAL CLICK
    450 : "\\textipa{\\textdoublebarpipe}", # LATIN LETTER ALVEOLAR CLICK
    451 : "!", # LATIN LETTER RETROFLEX CLICK
    593 : "\\textipa{A}", # LATIN SMALL LETTER ALPHA
    607 : "\\textipa{\\textbardotlessj{}}", # LATIN SMALL LETTER DOTLESS J WITH STROKE
    664 : "\\textipa{\\!o}", # LATIN LETTER BILABIAL CLICK
    688 : "\\super{h}", # MODIFIER LETTER SMALL H
    690 : "$^{j}$", # Modifier Letter Small J 
    700 : "'", # MODIFIER LETTER APOSTROPHE
    769 : "\\'{", # COMBINING ACUTE ACCENT
    770 : "\\^{", # COMBINING CIRCUMFLEX ACCENT
    771 : "\\~{", # COMBINING TILDE
    778 : "\\r{", # COMBINING RING ABOVE
    783 : "\\textdoublegrave{", # COMBINING DOUBLE GRAVE ACCENT
    967 : "\\textipa{X}", # GREEK SMALL LETTER CHI
    7505 : "\\super{N}", # MODIFIER LETTER SMALL ENG
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
    if base == "i" and (combining_char == 778 or combining_char == 805):
        result = "\\textsubring{"
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


def clean_latex(text, mapping):
    """clean_latex takes text and replaces characters so they can be
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


def clean_latex_text(text):
    """clean_latex_text converts the text to LaTeX text.
    """
    return clean_latex(text, text_latex_mapping)


def clean_latex_ipa(ipa):
    """clean_latex_ipa converts the IPA to LaTeX text.
    """
    return clean_latex(ipa, ipa_latex_mapping)


def clean_portal(text):
    """clean_portal makes the text for the portal output clean.
    Currently only unicode 805 character is replaced with 778 and the
    half moons 9789 and 9790 are removed.
    """

    return str(text).replace(chr(805), chr(778)).replace(chr(9789), '').replace(chr(9790), '')
