#!/usr/bin/env python3

from os.path import join, basename, normpath
from subprocess import check_call

def main(version, outdir):
    """
    Generate a Python release for a given SymPy version.
    
    This function prepares and generates a release for a specified SymPy version.
    It performs several steps including updating mailmap, authors, creating
    release files, and running various tests and documentation builds.
    
    Parameters:
    version (str): The version of SymPy for which the release is being prepared.
    outdir (str): The output directory where the release files will be stored.
    
    Returns:
    None: This function does not return anything. It performs actions such as
    """

    check_version(version, outdir)
    run_stage(['bin/mailmap_update.py'])
    run_stage(['bin/authors_update.py'])
    run_stage(['mkdir', '-p', outdir])
    build_release_files('bdist_wheel', 'sympy-%s-py3-none-any.whl', outdir, version)
    build_release_files('sdist', 'sympy-%s.tar.gz', outdir, version)
    run_stage(['release/compare_tar_against_git.py', join(outdir, 'sympy-%s.tar.gz' % (version,)), '.'])
    run_stage(['release/test_install.py', version, outdir])
    run_stage(['release/build_docs.py', version, outdir])
    run_stage(['release/sha256.py', version, outdir])
    run_stage(['release/authors.py', version, outdir])


def green(text):
    return "\033[32m%s\033[0m" % text

def red(text):
    return "\033[31m%s\033[0m" % text

def print_header(color, *msgs):
    """
    Prints a header with a specified color and messages.
    
    This function prints a header with a specified color and multiple messages. The header consists of a vertical line of 80 dashes, followed by the messages, and ends with another line of dashes.
    
    Parameters:
    color (function): A function that takes a string and returns a colored string.
    *msgs (str): Variable length argument list of messages to be printed in the header.
    
    Returns:
    None: This function does not return any value
    """

    newlines = '\n'
    vline = '-' * 80
    print(color(newlines + vline))
    for msg in msgs:
        print(color(msg))
    print(color(vline + newlines))

def run_stage(cmd):
    cmdline = '    $ %s' % (' '.join(cmd),)

    print_header(green, 'running:', cmdline)
    try:
        check_call(cmd)
    except Exception as e:
        print_header(red, 'failed:', cmdline)
        raise e from None
    else:
        print_header(green, 'completed:', cmdline)


def build_release_files(cmd, fname, outdir, version):
    fname = fname % (version,)
    run_stage(['python', 'setup.py', '-q', cmd])
    src = join('dist', fname)
    dst = join(outdir, fname)
    run_stage(['mv', src, dst])


def check_version(version, outdir):
    """
    Check if the version of the SymPy release matches the expected version.
    
    Args:
    version (str): The expected version of SymPy.
    outdir (str): The output directory name.
    
    Raises:
    AssertionError: If the version does not match the checked-out version or the output directory name.
    """

    from sympy.release import __version__ as checked_out_version
    if version != checked_out_version:
        msg = "version %s does not match checkout %s"
        raise AssertionError(msg % (version, checked_out_version))
    if basename(normpath(outdir)) != 'release-%s' % (version,):
        msg = "version %s does not match output directory %s"
        raise AssertionError(msg % (version, outdir))


if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])
