import re

def valid_header(header):
    matches = re.search(r'%PDF-\d.\d', header)

    if matches is not None:
        value = 1
    else:
        value = 0

    return value

def is_modified(xref):
    if xref > 1:
        value = 1
    else:
        value = 0

    return value

def is_malformed(obj, endobj, stream, endstream):
    if obj != endobj or stream != endstream:
        value = 1
    else:
        value = 0
    
    return value