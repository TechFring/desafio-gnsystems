import html.parser


def iterate_on_json(json_structure, prefix="", keep_dictionaries=False, skip=["__parent__"]):
    for k, v in sorted(json_structure.items()):
        if k in skip:
            continue
        p = prefix + "/" + k
        if isinstance(v, str):
            yield (p, v)
        elif isinstance(v, dict):
            if keep_dictionaries:
                yield (p, v)
            for r in iterate_on_json(v, p, keep_dictionaries, skip):
                yield r
        elif isinstance(v, list):
            for el in v:
                if keep_dictionaries:
                    yield (p, el)
                for r in iterate_on_json(el, p, keep_dictionaries, skip):
                    yield r
        else:
            raise Exception(
                "Unexpected type, the json was altered at path '{0}'".format(
                    p))


class HTMLtoJSONParser(html.parser.HTMLParser):

    def __init__(self, raise_exception=True):
        html.parser.HTMLParser.__init__(self, convert_charrefs=True)
        self.doc = {}
        self.path = []
        self.cur = self.doc
        self.line = 0
        self.raise_exception = raise_exception


    @property
    def json(self):
        return self.doc


    @staticmethod
    def to_json(content, raise_exception=True):
        parser = HTMLtoJSONParser(raise_exception=raise_exception)
        parser.feed(content)
        return parser.json


    @staticmethod
    def iterate(json_structure, prefix="", keep_dictionaries=False,
                skip=["__parent__"]):

        for _ in iterate_on_json(
                json_structure, prefix, keep_dictionaries, skip):
            yield _


    def handle_starttag(self, tag, attrs):
        self.path.append(tag)
        attrs = {k: v for k, v in attrs}
        if tag in self.cur:
            if isinstance(self.cur[tag], list):
                self.cur[tag].append({"__parent__": self.cur})
                self.cur = self.cur[tag][-1]
            else:
                self.cur[tag] = [self.cur[tag]]
                self.cur[tag].append({"__parent__": self.cur})
                self.cur = self.cur[tag][-1]
        else:
            self.cur[tag] = {"__parent__": self.cur}
            self.cur = self.cur[tag]

        for a, v in attrs.items():
            self.cur["@" + a] = v
        self.cur[""] = ""


    def handle_endtag(self, tag):
        del self.path[-1]
        memo = self.cur
        self.cur = self.cur["__parent__"]
        self.clean(memo)


    def handle_data(self, data):
        self.line += data.count("\n")
        if "" in self.cur:
            self.cur[""] += data


    def clean(self, values):
        keys = list(values.keys())
        for k in keys:
            v = values[k]
            if isinstance(v, str):
                c = v.strip(" \n\r\t")
                if c != v:
                    if len(c) > 0:
                        values[k] = c
                    else:
                        del values[k]
                elif len(v) == 0:
                    del values[k]
        del values["__parent__"]
