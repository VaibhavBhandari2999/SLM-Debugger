#!/usr/bin/env python3

from os.path import join, basename, normpath
from subprocess import check_call

def main(version, outdir):
    """
    Generate a release for the SymPy project.
    
    This function performs a series of steps to prepare and generate a release for the SymPy project. It checks the version and output directory, updates the mailmap and authors files, creates the necessary directories, builds the release files, and runs several validation and testing stages.
    
    Parameters:
    version (str): The version number for the SymPy release.
    outdir (str): The output directory where the release files will be stored.
    
    Returns:
    None:
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
    newlines = '\n'
    vline = '-' * 80
    print(color(newlines + vline))
    for msg in msgs:
        print(color(msg))
    print(color(vline + newlines))

def run_stage(cmd):
    """
    Runs a given command and prints the status.
    
    This function executes a command and prints the command line used. It also prints the status of the command execution, indicating whether it was successful or not.
    
    Parameters:
    cmd (list): The command to be executed, provided as a list of strings.
    
    Returns:
    None: This function does not return any value. It prints the command and its status to the console.
    
    Example:
    >>> run_stage(['ls', '-l'])
    running:    $
    """

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
    """
    Builds release files for a Python package.
    
    This function is responsible for generating and moving release files to a specified output directory. It runs a setup command to build the release file, then moves the generated file to the output directory.
    
    Parameters:
    cmd (str): The command to run with setup.py, such as 'sdist' or 'bdist_wheel'.
    fname (str): A format string for the release file name, which includes a placeholder for the version number.
    outdir (
    """

    fname = fname % (version,)
    run_stage(['python', 'setup.py', '-q', cmd])
    src = join('dist', fname)
    dst = join(outdir, fname)
    run_stage(['mv', src, dst])


def check_version(version, outdir):
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
