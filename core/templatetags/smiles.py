from django.template import Library

register = Library()

EMOTICONS = {
    u'O:-)': u'angel_mini',
    u'@}-&gt;--': u'rose_mini',
    u'*HEART*': u'heart_mini',
    u':-[': u'blush_mini',
    u':-)': u'smile_mini',
    u'%)': u'rolleyes_mini',
    u'8-)': u'lol_mini2',
    u'*ROFL*': u'rofl_mini',
    u';-)': u'laugh_mini',
    u':-P': u'mocking_mini',
    u';D': u'wink_mini',
    u':-\\': u'beee_mini',
    u'*STOP*': u'fool_mini2',
    u'*CRAZY*': u'crazy_mini',
    u'*BYE*': u'bye_mini',
    u'=-O': u'chok_mini',
    u'*JOKINGLY*': u'lol_mini',
    u'*WASSUP*': u'mamba_mini',
    u'*DONT_KNOW*': u'secret_mini',
    u'*HELP*': u'vava_mini',
    u':-*': u'kiss_mini',
    u']:-&gt;': u'diablo_mini',
    u'*BRAVO*': u'clapping_mini',
    u'*SORRY*': u'sorry_mini',
    u':-(': u'sad_mini',
    u":&#39;-(": u'cray_mini2',
    u'[:-}': u'aggressive_mini',
    u'*THUMBS UP*': u'good_mini',
    u'*SCRATCH*': u'scratch_one-s_head_mini',
    u':-X': u'bo_mini',
    u'*DRINK*': u'drink_mini',
    u'*PARDON*': u'pardon_mini',
    u'*DANCE*': u'dance_mini',
    u'*YES*': u'yahoo_mini',
    u'&gt;:o': u'mad_mini',
    u':-!': u'sad_mini2',
    u'*IN LOVE*': u'man_in_love_mini',
    u'*NO*': u'nea_mini',
    u'*HELLO*': u'dirol_mini',
    u':-D': u'happy_mini',
    u':-|': u'wacko_mini',
    u'*TIRED*': u'cray_mini',
    u'*OK*': u'music_mini2'}


@register.filter
def smiles(value):
    """
    Smiles library
    """
    for key, val in EMOTICONS.items():
        value = value.replace(key, """<img src="/s/emo/%s.gif" />""" % val)
    return value

smiles.is_safe = True
