from yaml import load, FullLoader


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self))


def config(filename):
    with open(filename) as f:
        return load(f.read(), Loader=FullLoader)
