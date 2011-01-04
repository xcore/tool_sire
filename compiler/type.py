specifiers = {
    'proc'      : 0, 
    'func'      : 1, 
    'var'       : 2, 
    'val'       : 3, 
    'chanend'   : 4, 
    'chan'      : 5, 
    'port'      : 6, 
    'core'      : 7,
    'tag'       : 8,
}

forms = {
    'undefined' : 0,   
    'single'    : 1, 
    'array'     : 2, 
    'alias'     : 3, 
    'sub'       : 4,
    'procedure' : 5,
}

class Type(object):
    def __init__(self, specifier, form='undefined'):
        if not specifier in specifiers:
            raise Exception("Invalid specifier '{}'".format(specifier))
        if not form in forms:
            raise Exception("Invalid form '{}'".format(form))
        self.specifier = specifier
        self.form = form

    def isTag(self):
        return self.specifier == 'tag'

    def __hash__(self):
        return specifiers[self.specifier] + 10*forms[self.form]

    def __eq__(self, other):
        return self.specifier == other.specifier and self.form == other.form

    def __cmp__(self, other):
        return self == other

    def __repr__(self):
        return "Type({}, {})".format(self.specifier, self.form)
