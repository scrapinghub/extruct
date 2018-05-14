import mf2py


class MicroformatExtractor(object):

    def extract(self, htmlstring, base_url=None, encoding='UTF-8'):
        return list(self.extract_items(htmlstring, base_url=base_url))

    def extract_items(self, html, base_url=None):
        for obj in mf2py.parse(html, html_parser="lxml", url=base_url)['items']:
            yield obj
