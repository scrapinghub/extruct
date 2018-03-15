import mf2py

class MicroformatExtractor(object):

    def extract(self, htmlstring, url='http://www.example.com/', encoding='UTF-8'):
        return list(self.extract(htmlstring, url=url))

    def extract_items(self, html, url, document=None):
        for obj in mf2py.parse(html, html_parser="lxml", url=url)['items']:
            if obj['type'] == 'h-entry':
                for o in obj['children']:
                    yield o
            else:
                yield obj
