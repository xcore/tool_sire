import re

def camel_to_under(s):
    return re.sub("([A-Z])([A-Z][a-z])|([a-z0-9])([A-Z])", lambda m:
            '{}_{}'.format(m.group(3), m.group(4)), s).lower()

