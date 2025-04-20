#!/usr/bin/env python
import argparse
import subprocess
import sys
from pathlib import Path

try:
    import closure
except ImportError:
    closure_compiler = None
else:
    closure_compiler = closure.get_jar_filename()

js_path = Path(__file__).parent.parent / 'static' / 'admin' / 'js'


def main():
    """
    Compresses jQuery-based files of the admin app using the Google Closure Compiler.
    
    This script automatically compresses all jQuery-based files of the admin app. It requires the Google Closure Compiler library and Java version 6 or later. If no file paths are provided, it will compress the default admin scripts.
    
    Parameters:
    file (list): Optional list of file paths to compress. If not provided, the default admin scripts will be compressed.
    compiler (str): Path to the Closure Compiler jar file.
    """

    description = """With no file paths given this script will automatically
compress all jQuery-based files of the admin app. Requires the Google Closure
Compiler library and Java version 6 or later."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('file', nargs='*')
    parser.add_argument(
        "-c", dest="compiler", default="~/bin/compiler.jar",
        help="path to Closure Compiler jar file",
    )
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose")
    parser.add_argument("-q", "--quiet", action="store_false", dest="verbose")
    options = parser.parse_args()

    compiler = Path(closure_compiler or options.compiler).expanduser()
    if not compiler.exists():
        sys.exit(
            "Google Closure compiler jar file %s not found. Please use the -c "
            "option to specify the path." % compiler
        )

    if not options.file:
        if options.verbose:
            sys.stdout.write("No filenames given; defaulting to admin scripts\n")
        files = [
            js_path / f
            for f in ["actions.js", "collapse.js", "inlines.js", "prepopulate.js"]
        ]
    else:
        files = [Path(f) for f in options.file]

    for file_path in files:
        to_compress = file_path.expanduser()
        if to_compress.exists():
            to_compress_min = to_compress.with_suffix('.min.js')
            cmd = "java -jar %s --js %s --js_output_file %s" % (compiler, to_compress, to_compress_min)
            if options.verbose:
                sys.stdout.write("Running: %s\n" % cmd)
            subprocess.call(cmd.split())
        else:
            sys.stdout.write("File %s not found. Sure it exists?\n" % to_compress)


if __name__ == '__main__':
    main()
