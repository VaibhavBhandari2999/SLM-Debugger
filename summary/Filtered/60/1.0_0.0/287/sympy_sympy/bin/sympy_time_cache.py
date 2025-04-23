from __future__ import print_function

import time
import timeit


class TreeNode(object):
    def __init__(self, name):
        self._name = name
        self._children = []
        self._time = 0

    def __str__(self):
        return "%s: %s" % (self._name, self._time)

    __repr__ = __str__

    def add_child(self, node):
        self._children.append(node)

    def children(self):
        return self._children

    def child(self, i):
        return self.children()[i]

    def set_time(self, time):
        self._time = time

    def time(self):
        return self._time

    total_time = time

    def exclusive_time(self):
        return self.total_time() - sum(child.time() for child in self.children())

    def name(self):
        return self._name

    def linearize(self):
        """
        Linearize a tree structure.
        
        This function takes a tree-like object and returns a list of its nodes in a linearized form, meaning it traverses the tree in a depth-first manner and collects all nodes into a single list.
        
        Parameters:
        self (TreeNode): The root node of the tree to be linearized.
        
        Returns:
        list: A list of TreeNode objects representing the linearized tree structure.
        
        Example:
        Given a tree with the following structure:
        A
        / \
        B
        """

        res = [self]
        for child in self.children():
            res.extend(child.linearize())
        return res

    def print_tree(self, level=0, max_depth=None):
        """
        Prints the tree structure in a formatted manner.
        
        This function recursively prints the tree nodes in a hierarchical format, with indentation indicating the depth of each node.
        
        Parameters:
        level (int): The current depth level of the node. Defaults to 0.
        max_depth (int, optional): The maximum depth to print. If specified, nodes beyond this depth will not be printed. Defaults to None.
        
        Returns:
        None: This function does not return any value. It prints the tree structure to
        """

        print("  "*level + str(self))
        if max_depth is not None and max_depth <= level:
            return
        for child in self.children():
            child.print_tree(level + 1, max_depth=max_depth)

    def print_generic(self, n=50, method="time"):
        slowest = sorted((getattr(node, method)(), node.name()) for node in self.linearize())[-n:]
        for time, name in slowest[::-1]:
            print("%s %s" % (time, name))

    def print_slowest(self, n=50):
        self.print_generic(n=50, method="time")

    def print_slowest_exclusive(self, n=50):
        self.print_generic(n, method="exclusive_time")

    def write_cachegrind(self, f):
        """
        Writes a cachegrind output to a file or file-like object.
        
        Parameters:
        - f (str or file-like object): The file or file-like object to which the cachegrind output will be written. If a string is provided, it is treated as a filename and the file is opened in write mode.
        
        Returns:
        - None: The function writes directly to the provided file or file-like object and does not return any value.
        
        Key Parameters:
        - `f`: The target file or file-like
        """

        if isinstance(f, str):
            f = open(f, "w")
            f.write("events: Microseconds\n")
            f.write("fl=sympyallimport\n")
            must_close = True
        else:
            must_close = False

        f.write("fn=%s\n" % self.name())
        f.write("1 %s\n" % self.exclusive_time())

        counter = 2
        for child in self.children():
            f.write("cfn=%s\n" % child.name())
            f.write("calls=1 1\n")
            f.write("%s %s\n" % (counter, child.time()))
            counter += 1

        f.write("\n\n")

        for child in self.children():
            child.write_cachegrind(f)

        if must_close:
            f.close()


pp = TreeNode(None)  # We have to use pp since there is a sage function
                     #called parent that gets imported
seen = set()


def new_import(name, globals={}, locals={}, fromlist=[]):
    """
    This function is a custom import function that extends the standard import mechanism in Python. It records the import process in a tree structure and measures the time taken for each import.
    
    Parameters:
    - name (str): The name of the module to be imported.
    - globals (dict, optional): The global symbol table for the module that is importing. Defaults to {}.
    - locals (dict, optional): The local symbol table for the module that is importing. Defaults to {}.
    - fromlist (list,
    """

    global pp
    if name in seen:
        return old_import(name, globals, locals, fromlist)
    seen.add(name)

    node = TreeNode(name)

    pp.add_child(node)
    old_pp = pp
    pp = node

    #Do the actual import
    t1 = timeit.default_timer()
    module = old_import(name, globals, locals, fromlist)
    t2 = timeit.default_timer()
    node.set_time(int(1000000*(t2 - t1)))

    pp = old_pp

    return module

old_import = __builtins__.__import__

__builtins__.__import__ = new_import
old_sum = sum

from sympy import *

sum = old_sum

sageall = pp.child(0)
sageall.write_cachegrind("sympy.cachegrind")

print("Timings saved. Do:\n$ kcachegrind sympy.cachegrind")
