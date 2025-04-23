#!/usr/bin/env python3


from pathlib import Path
from tempfile import TemporaryDirectory
from subprocess import check_call


PY_VERSIONS = '3.6', '3.7', '3.8', '3.9'


def main(version, outdir):
    for pyversion in PY_VERSIONS:
        test_sdist(pyversion, version, outdir)
        test_wheel(pyversion, version, outdir)


def run(cmd, cwd=None):
    """
    Run a command in a subprocess.
    
    This function executes a command in a subprocess. The command can be provided as a list of strings or a single string. If a string is provided, it is split into a list using `split()`. The function returns the result of `check_call`, which typically returns 0 on success, or raises CalledProcessError if the command fails.
    
    Parameters:
    cmd (str or list): The command to execute, either as a single string or a list of strings
    """

    if isinstance(cmd, str):
        cmd = cmd.split()
    return check_call(cmd, cwd=cwd)


def green(text):
    return "\033[32m%s\033[0m" % text


def test_sdist(pyversion, version, outdir, wheel=False):

    print(green('-' * 80))
    if not wheel:
        print(green('    Testing Python %s (sdist)' % pyversion))
    else:
        print(green('    Testing Python %s (wheel)' % pyversion))
    print(green('-' * 80))

    python_exe = f'python{pyversion}'
    wheelname = f'sympy-{version}-py3-none-any.whl'
    tarname = f'sympy-{version}.tar.gz'
    tardir = f'sympy-{version}'

    with TemporaryDirectory() as tempdir:
        outdir = Path(outdir)
        tempdir = Path(tempdir)
        venv = tempdir / f'venv{pyversion}'
        pip = venv / "bin" / "pip"
        python = venv / "bin" / "python"
        run(f'{python_exe} -m venv {venv}')
        run(f'{pip} install -U -q pip')
        if not wheel:
            run(f'{pip} install -q mpmath')
            run(f'cp {outdir/tarname} {tempdir/tarname}')
            run(f'tar -xzf {tempdir/tarname} -C {tempdir}')
            run(f'{python} setup.py -q install', cwd=tempdir/tardir)
        else:
            run(f'{pip} install -q {outdir/wheelname}')
        isympy = venv / "bin" / "isympy"
        run([python, '-c', "import sympy; print(sympy.__version__); print('sympy installed successfully')"])
        run(f'{python} -m isympy --version')
        run(f'{isympy} --version')


def test_wheel(*args):
    return test_sdist(*args, wheel=True)


if __name__ == "__main__":
    import sys
    sys.exit(main(*sys.argv[1:]))
el=True)


if __name__ == "__main__":
    import sys
    sys.exit(main(*sys.argv[1:]))
