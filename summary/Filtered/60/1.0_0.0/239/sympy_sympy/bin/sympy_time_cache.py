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
        res = [self]
        for child in self.children():
            res.extend(child.linearize())
        return res

    def print_tree(self, level=0, max_depth=None):
        """
        Prints the tree structure in a formatted manner.
        
        This function recursively prints the tree structure with indentation based on the depth level. Each node is printed with its value, and the tree is printed up to a specified maximum depth.
        
        Parameters:
        level (int): The current depth level of the tree. This parameter is typically not set by the user and is used internally by the function. Default is 0.
        max_depth (int, optional): The maximum depth to which the tree should be printed
        """

        print("  "*level + str(self))
        if max_depth is not None and max_depth <= level:
            return
        for child in self.children():
            child.print_tree(level + 1, max_depth=max_depth)

    def print_generic(self, n=50, method="time"):
        """
        Prints the n slowest nodes in the linearized graph based on the specified method.
        
        Parameters:
        n (int): The number of slowest nodes to print. Default is 50.
        method (str): The method to use for determining the slowness of nodes. Default is "time".
        
        This function sorts the nodes in the linearized graph based on the provided method and prints the names and values of the n slowest nodes.
        """

        slowest = sorted((getattr(node, method)(), node.name()) for node in self.linearize())[-n:]
        for time, name in slowest[::-1]:
            print("%s %s" % (time, name))

    def print_slowest(self, n=50):
        self.print_generic(n=50, method="time")

    def print_slowest_exclusive(self, n=50):
        self.print_generic(n, method="exclusive_time")

    def write_cachegrind(self, f):
        """
        Writes the profiling data in cachegrind format to the specified file or file object.
        
        Parameters:
        f (str or file object): The file path or file object to which the cachegrind data will be written.
        
        Returns:
        None: The function writes directly to the file and does not return any value.
        
        Explanation:
        This function writes the profiling data in cachegrind format to the specified file or file object. It first checks if the provided argument is a string (file path) or
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
