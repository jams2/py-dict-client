"""
Formatting input word into a valid string for dict server.
In RFC2229 [https://datatracker.ietf.org/doc/html/rfc2229#section-2.2]
the grammar is specified as the following:

'''
                                               ; (  Octal, Decimal.)
   CHAR        =  <any UTF-8 character (1 to 6 octets)>
   CTL         =  <any ASCII control           ; (  0- 37,  0.- 31.)
                   character and DEL>          ; (    177,     127.)
   CR          =  <ASCII CR, carriage return>  ; (     15,      13.)
   LF          =  <ASCII LF, linefeed>         ; (     12,      10.)
   SPACE       =  <ASCII SP, space>            ; (     40,      32.)
   HTAB        =  <ASCII HT, horizontal-tab>   ; (     11,       9.)
   <">         =  <ASCII quote mark>           ; (     42,      34.)
   <'>         =  <ASCII single quote mark>    ; (     47,      39.)
   CRLF        =  CR LF
   WS          =  1*(SPACE / HTAB)

   dqstring    =  <"> *(dqtext/quoted-pair) <">
   dqtext      =  <any CHAR except <">, "\", and CTLs>
   sqstring    =  <'> *(dqtext/quoted-pair) <'>
   sqtext      =  <any CHAR except <'>, "\", and CTLs>
   quoted-pair =  "\" CHAR

   atom        =  1*<any CHAR except SPACE, CTLs, <'>, <">, and "\">
   string      =  *<dqstring / sqstring / quoted-pair>
   word        =  *<atom / string>
   description =  *<word / WS>
   text        =  *<word / WS>
'''
"""
import re

# every utf-8 character except <SPC>, <">, <'>, or <\>
ATOM = re.compile(
    f"^([{chr(33)}]|[{chr(35)}-{chr(38)}]|[{chr(40)}-{chr(91)}]|[{chr(93)}-{chr(1114111)}])+$"
)
# every utf-8 character except <">
DQABLE = re.compile(f"^([{chr(32)}-{chr(33)}]|[{chr(35)}-{chr(1114111)}])+$")
# DQABLE wrapped in double quotes
DQSTRING = re.compile(f'^"([{chr(32)}-{chr(33)}]|[{chr(35)}-{chr(1114111)}])+"$')
# every utf-character except <'>
SQABLE = re.compile(f"^([{chr(32)}-{chr(38)}]|[{chr(40)}-{chr(1114111)}])+$")
# SQABLE wrapped in single qoutes
SQSTRING = re.compile(f"^'([{chr(32)}-{chr(38)}]|[{chr(40)}-{chr(1114111)}])+'$")


class Word:
    def __init__(self, word_raw):
        self.raw = word_raw
        self.formatted = self._format_word(word_raw)

    def _format_word(self, word):
        if ATOM.match(word) or DQSTRING.match(word) or SQSTRING.match(word):
            return word
        elif DQABLE.match(word):
            return f'"{word}"'
        elif SQABLE.match(word):
            return f"'{word}'"
        else:
            raise ValueError(f"Invalid word `{word}`")

    def __str__(self):
        return self.formatted
