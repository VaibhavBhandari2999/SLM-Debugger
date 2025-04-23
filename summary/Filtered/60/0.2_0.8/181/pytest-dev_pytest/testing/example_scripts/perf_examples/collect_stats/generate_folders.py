import argparse
import pathlib

HERE = pathlib.Path(__file__).parent
TEST_CONTENT = (HERE / "template_test.py").read_bytes()

parser = argparse.ArgumentParser()
parser.add_argument("numbers", nargs="*", type=int)


def generate_folders(root, elements, *more_numbers):
    """
    Generate a directory structure with nested folders and test files.
    
    This function creates a directory structure starting from a root directory. It generates a specified number of folders and test files at each level of the hierarchy. The function supports an arbitrary number of nested levels.
    
    Parameters:
    root (Path): The root directory where the structure will be created.
    elements (int): The number of folders and test files to create at each level.
    *more_numbers (int): Additional levels of nesting, each with the
    """

    fill_len = len(str(elements))
    if more_numbers:
        for i in range(elements):
            new_folder = root.joinpath(f"foo_{i:0>{fill_len}}")
            new_folder.mkdir()
            new_folder.joinpath("__init__.py").write_bytes(TEST_CONTENT)
            generate_folders(new_folder, *more_numbers)
    else:
        for i in range(elements):
            new_test = root.joinpath(f"test_{i:0<{fill_len}}.py")
            new_test.write_bytes(TEST_CONTENT)


if __name__ == "__main__":
    args = parser.parse_args()
    generate_folders(HERE, *(args.numbers or (10, 100)))
