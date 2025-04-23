#!/usr/bin/env python
# Sorts what's new entries with per-module headings.
# Pass what's new entries on stdin.

import sys
import re
from collections import defaultdict

LABEL_ORDER = ['MajorFeature', 'Feature', 'Enhancement', 'Efficiency',
               'Fix', 'API']


def entry_sort_key(s):
    """
    Sort key function for entries.
    
    This function is designed to be used as a key function in sorting operations.
    It prioritizes entries that start with '- |' by sorting them based on the label
    specified after the pipe character. Entries that do not start with '- |' are
    sorted last and are considered to have the lowest priority.
    
    Parameters:
    s (str): The string entry to be sorted.
    
    Returns:
    int: A sorting key value. Entries starting with '- |' are assigned a
    """

    if s.startswith('- |'):
        return LABEL_ORDER.index(s.split('|')[1])
    else:
        return -1


# discard headings and other non-entry lines
text = ''.join(l for l in sys.stdin
               if l.startswith('- ') or l.startswith(' '))

bucketed = defaultdict(list)

for entry in re.split('\n(?=- )', text.strip()):
    modules = re.findall(r':(?:func|meth|mod|class):'
                         r'`(?:[^<`]*<|~)?(?:sklearn.)?([a-z]\w+)',
                         entry)
    modules = set(modules)
    if len(modules) > 1:
        key = 'Multiple modules'
    elif modules:
        key = ':mod:`sklearn.%s`' % next(iter(modules))
    else:
        key = 'Miscellaneous'
    bucketed[key].append(entry)
    entry = entry.strip() + '\n'

everything = []
for key, bucket in sorted(bucketed.items()):
    everything.append(key + '\n' + '.' * len(key))
    bucket.sort(key=entry_sort_key)
    everything.extend(bucket)
print('\n\n'.join(everything))
