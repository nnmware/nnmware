# -*- encoding: utf-8 -*-

import re

##################################################
## SLUG HELPERS ##

_REMOVELIST = [
    "a", "an", "as", "at", "before", "but", "by", "for", "from",
    "is", "in", "into", "like", "of", "off", "on", "onto", "per",
    "since", "than", "the", "this", "that", "to", "up", "via",
    "with"
]
_RE_REMOVE = re.compile('\\b(' + '|'.join(_REMOVELIST) + ')\\b', re.IGNORECASE)
_RE_UNNEEDED = re.compile(r'[^\w\s-]')


def URLify(s, num_chars=None):
    """ based on urlify.js from django
        effect:
            removes common words (_REMOVELIST)
            removes unneeded whitespaces around '-'
            trim leading/trailing whitespaces
            lowercase string
            replace space with '-'
            if num_chars if given trim to number of given characters
            finnaly quotes other URLunsafe words with urlib.quote
    """

    ret = _RE_REMOVE.sub('', s)
    ret = _RE_UNNEEDED.sub('', s)
    ret = ret.strip().replace(' ', '-').lower()

    if num_chars is not None:
        ret = ret[:num_chars]

    # remove duplicate '-'
    while '--' in ret:
        ret = ret.replace('--', '-')

    return ret

# URLify

_BR_CLEANUP = re.compile(r'<\s*br\s*/?\s*>', re.IGNORECASE)


def text_cleanup(txt, clean_br=True, cleanup_double_space=True, strip_ws=True):
    if txt:
        if clean_br:
            txt = _BR_CLEANUP.sub(' ', txt)  # remove <br />
        if strip_ws:
            txt = txt.strip()  # strip all leading/trailing spaces
        if cleanup_double_space:
            while '  ' in txt:
                txt = txt.replace('  ', ' ')   # remove double spaces
        return txt
    else:
        return txt


alnum_re = re.compile(r'^\w+$')
