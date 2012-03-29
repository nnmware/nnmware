"""Realisation of rendering different markup languages"""

from django.utils.html import escape
from nnmware.core.markdown import Markdown
from nnmware.core.templatetags.typogrify import typogrify

RENDER_METHODS = (
    ('markdown', 'Markdown'),
    ('bbcode', 'BB code'),
    ('html', 'HTML'),
    ('html_br', 'Text+HTML (livejournal)'),
    ('text', 'Plain text'),
    ('wikimarkup', 'MediaWiki markup'),
    )


def normalize_html(data):
    """
    Apply tidy cleanup for data which should be in unicode
    """
    from BeautifulSoup import BeautifulSoup

    soup = BeautifulSoup(data)
    return unicode(soup)


def more_fix(text):
    return text.replace('&lt;!--more--&gt;', '<!--more-->')


class RenderException(Exception):
    """Can't render"""
    pass


def to_html(data):
    data = escape(data).replace('\n', '<br/>\n')
    return data


def render(content, render_method, unsafe=False):
    renderer = Renderer(content, render_method, unsafe)
    return renderer.render()


class Renderer(object):
    def __init__(self, content, render_method, unsafe=False):
        self.content = content.strip()
        self.render_method = render_method
        self.unsafe = unsafe

    def render(self):
        try:
            renderer = getattr(self, 'get_%s_render' % self.render_method)()
            return unicode(typogrify(more_fix(renderer(self.content))))
        except AttributeError:
            raise RenderException(u"Unknown render method: '%s'" % self.render_method)

    def get_markdown_render(self):
        md = Markdown(extensions=['footnotes', 'abbr'], safe_mode=not self.unsafe)
        return md.convert

    def get_text_render(self):
        return textparser.to_html

    def get_html_render(self):
        return lambda x: x
