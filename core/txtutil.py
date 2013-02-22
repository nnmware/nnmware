# -*- encoding: utf-8 -*-

import re

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
