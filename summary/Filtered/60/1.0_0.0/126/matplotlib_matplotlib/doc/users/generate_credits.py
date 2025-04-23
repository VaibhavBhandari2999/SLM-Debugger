#!/usr/bin/env python
#
# This script generates credits.rst with an up-to-date list of contributors
# to the matplotlib github repository.

from collections import Counter
import locale
import re
import subprocess

TEMPLATE = """.. Note: This file is auto-generated using generate_credits.py

.. _credits:

*******
Credits
*******


Matplotlib was written by John D. Hunter, with contributions from an
ever-increasing number of users and developers.  The current lead developer is
Thomas A. Caswell, who is assisted by many `active developers
<https://www.openhub.net/p/matplotlib/contributors>`_.
Please also see our instructions on :doc:`/citing`.

The following is a list of contributors extracted from the
git revision control history of the project:

{contributors}

Some earlier contributors not included above are (with apologies
to any we have missed):

Charles Twardy,
Gary Ruben,
John Gill,
David Moore,
Paul Barrett,
Jared Wahlstrand,
Jim Benson,
Paul Mcguire,
Andrew Dalke,
Nadia Dencheva,
Baptiste Carvello,
Sigve Tjoraand,
Ted Drain,
James Amundson,
Daishi Harada,
Nicolas Young,
Paul Kienzle,
John Porter,
and Jonathon Taylor.

Thanks to Tony Yu for the original logo design.

We also thank all who have reported bugs, commented on
proposed changes, or otherwise contributed to Matplotlib's
development and usefulness.
"""


def check_duplicates():
    """
    Function to check for duplicate email addresses in the git shortlog output.
    
    This function processes the output of the 'git shortlog --summary --email'
    command to identify contributors and their email addresses. It then counts
    the occurrences of each email address and prints a list of email addresses
    that are associated with more than one name. This can help in identifying
    potential duplicates that might need to be resolved by adding them to the
    .git/info/mailmap file.
    
    Parameters:
    None
    
    Returns:
    """

    text = subprocess.check_output(['git', 'shortlog', '--summary', '--email'])
    lines = text.decode('utf8').split('\n')
    contributors = [line.split('\t', 1)[1].strip() for line in lines if line]
    emails = [re.match('.*<(.*)>', line).group(1) for line in contributors]
    email_counter = Counter(emails)

    if email_counter.most_common(1)[0][1] > 1:
        print('DUPLICATE CHECK: The following email addresses are used with '
              'more than one name.\nConsider adding them to .mailmap.\n')
        for email, count in email_counter.items():
            if count > 1:
                print('{}\n{}'.format(
                    email, '\n'.join(l for l in lines if email in l)))


def generate_credits():
    """
    Generate a credits file for the project.
    
    This function uses the `git shortlog` command to generate a list of contributors
    to the project, sorted alphabetically. The contributors are then written to a
    file named 'credits.rst' in the following format:
    
    - contributor1
    - contributor2
    - ...
    
    The function does not return any value but writes the list of contributors to
    a file.
    
    Parameters:
    None
    
    Returns:
    None
    
    Note:
    The function requires
    """

    text = subprocess.check_output(['git', 'shortlog', '--summary'])
    lines = text.decode('utf8').split('\n')
    contributors = [line.split('\t', 1)[1].strip() for line in lines if line]
    contributors.sort(key=locale.strxfrm)
    with open('credits.rst', 'w') as f:
        f.write(TEMPLATE.format(contributors=',\n'.join(contributors)))


if __name__ == '__main__':
    check_duplicates()
    generate_credits()
