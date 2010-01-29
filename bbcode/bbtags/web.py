from bbcode import *
import re
import urllib

class Url(TagNode):
    """
    Creates a hyperlink.
    
    Usage:
     
    [code lang=bbdocs linenos=0][url=<http://www.domain.com>]Text[/url]
[url]http://www.domain.com[/url][/code]
    """
    verbose_name = 'Link'
    open_pattern = re.compile(r'(\[url\]|\[url="?(?P<href>[^\]]+)"?\]|\[url (?P'
                               '<arg1>\w+)="?(?P<val1>[^ ]+)"?( (?P<arg2>\w+)="'
                               '?(?P<val2>[^ ]+)"?)?\])')
    close_pattern = re.compile(patterns.closing % 'url')
    
    def parse(self):
        gd = self.match.groupdict()
        gd.update({'css':''})
        if gd['arg1']:
            gd[gd['arg1']] = gd['val1']
        if gd['arg2']:
            gd[gd['arg2']] = gd['val2']
        if gd['href']:
            href = self.variables.resolve(gd['href'])
            inner = self.parse_inner()
        else:
            inner = ''
            for node in self.nodes:
                if node.is_text_node or isinstance(node, AutoDetectURL):
                    inner += node.raw_content
                else:
                    self.soft_raise("Url tag cannot have nested tags without "
                                    "an argument.")
            href = self.variables.resolve(inner)
            inner = href
        if gd['css']:
            css = ' class="%s"' % gd['css'].replace(',',' ')
        else:
            css = ''
        raw_href = self.variables.resolve(href)
        if raw_href.startswith('http://'):
            href = raw_href[:7] + urllib.quote(raw_href[7:])
        else:
            href = urllib.quote(raw_href)
        css = self.variables.resolve(css)
        return '<a href="%s"%s>%s</a>' % (href, css, inner)
    

class Email(TagNode):
    """
    Creates an email link.
    
    Usage:
    
    [code lang=bbdocs linenos=0][email]name@domain.com[/email]
[email=<name@domain.com>]Text[/email][/code]
    """
    verbose_name = 'E-Mail'
    open_pattern = re.compile(r'(\[email\]|\[email=(?P<mail>[^\]]+\]))')
    close_pattern = re.compile(patterns.closing % 'email')

    def parse(self):
        gd = self.match.groupdict()
        email = gd.get('email', None)
        if email:
            inner = ''
            for node in self.nodes:
                if node.is_text_node or isinstance(node, AutoDetectURL):
                    inner += node.raw_content
                else:
                    inner += node.parse()
            return '<a href="mailto:%s">%s</a>' % (email, inner)
        else:
            inner = ''
            for node in self.nodes:
                inner += node.raw_content
            return '<a href="mailto:%s">%s</a>' % (inner, inner)
    
    

    
    
class Img(ArgumentTagNode):
    """
    Displays an image.
    
    Usage:
    
    [code lang=bbdocs linenos=0][img]http://www.domain.com/image.jpg[/img]
[img=<align>]http://www.domain.com/image.jpg[/img][/code]
    
    Arguments:
    
    Allowed values for [i]align[/i]: left, center, right. Default: None.
    """
    verbose_name = 'Image'
    open_pattern = re.compile(patterns.single_argument % 'img')
    close_pattern = re.compile(patterns.closing % 'img')
    
    def parse(self):
        inner = ''
        for node in self.nodes:    
            if node.is_text_node or isinstance(node, AutoDetectURL):
                inner += node.raw_content
            else:
                soft_raise("Img tag cannot have nested tags without an argument.")
                return self.raw_content
        inner = self.variables.resolve(inner)
        if self.argument:
            return '<img src="%s" alt="image" class="img-%s" />' % (inner, self.argument)
        else:
            return '<img src="%s" alt="image" />' % inner
    
    
class Youtube(TagNode):
    """
    Includes a youtube video. Post the URL to the youtube video inside the tag.
    
    Usage:
    
    [code lang=bbdocs linenos=0][youtube]http://www.youtube.com/watch?v=FjPf6B8EVJI[/youtube][/code]
    """
    _video_id_pattern = re.compile('v=(\w+)')
    open_pattern = re.compile(patterns.no_argument % 'youtube')
    close_pattern = re.compile(patterns.closing % 'youtube')
    
    def parse(self):
        url = ''
        for node in self.nodes:
            if node.is_text_node or isinstance(node, AutoDetectURL):
                inner += node.raw_content
            else:
                soft_raise("Youtube tag cannot have nested tags")
                return self.raw_content
        match = self._video_id_pattern.search(url)
        if not match:
            soft_raise("'%s' does not seem like a youtube link" % url)
            return self.raw_content
        videoid = match.groups()
        if not videoid:
            soft_raise("'%s' does not seem like a youtube link" % url)
            return self.raw_content
        videoid = videoid[0]
        return (
            '<object width="560" height="340"><param name="movie" value="http:/'
            '/www.youtube.com/v/%s&amp;hl=en&amp;fs=1&amp;"></param><param name'
            '="allowFullScreen" value="true"></param><param name="allowscriptac'
            'cess" value="always"></param><embed src="http://www.youtube.com/v/'
            '%s&amp;hl=en&amp;fs=1&amp;" type="application/x-shockwave-flash" a'
            'llowscriptaccess="always" allowfullscreen="true" width="560" heigh'
        )
    
    
class AutoDetectURL(SelfClosingTagNode):
    open_pattern = re.compile('((ht|f)tps?:\/\/([-\w\.]+)+(:\d+)?(\/([\w\/_\.,-]*(\?\S+)?)?)?)')

    def parse(self):
        url = self.match.group()
        return '<a href="%s">%s</a>' % (url, url)
    

register(Url)
register(Img)
register(Email)
register(Youtube)
register(AutoDetectURL)
