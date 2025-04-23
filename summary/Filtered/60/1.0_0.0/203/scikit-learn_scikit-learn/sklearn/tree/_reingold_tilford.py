# Authors: William Mill (bill@billmill.org)
# License: BSD 3 clause

import numpy as np


class DrawTree:
    def __init__(self, tree, parent=None, depth=0, number=1):
        self.x = -1.0
        self.y = depth
        self.tree = tree
        self.children = [
            DrawTree(c, self, depth + 1, i + 1) for i, c in enumerate(tree.children)
        ]
        self.parent = parent
        self.thread = None
        self.mod = 0
        self.ancestor = self
        self.change = self.shift = 0
        self._lmost_sibling = None
        # this is the number of the node in its group of siblings 1..n
        self.number = number

    def left(self):
        return self.thread or len(self.children) and self.children[0]

    def right(self):
        return self.thread or len(self.children) and self.children[-1]

    def lbrother(self):
        n = None
        if self.parent:
            for node in self.parent.children:
                if node == self:
                    return n
                else:
                    n = node
        return n

    def get_lmost_sibling(self):
        if not self._lmost_sibling and self.parent and self != self.parent.children[0]:
            self._lmost_sibling = self.parent.children[0]
        return self._lmost_sibling

    lmost_sibling = property(get_lmost_sibling)

    def __str__(self):
        return "%s: x=%s mod=%s" % (self.tree, self.x, self.mod)

    def __repr__(self):
        return self.__str__()

    def max_extents(self):
        extents = [c.max_extents() for c in self.children]
        extents.append((self.x, self.y))
        return np.max(extents, axis=0)


def buchheim(tree):
    dt = first_walk(DrawTree(tree))
    min = second_walk(dt)
    if min < 0:
        third_walk(dt, -min)
    return dt


def third_walk(tree, n):
    tree.x += n
    for c in tree.children:
        third_walk(c, n)


def first_walk(v, distance=1.0):
    """
    Walk through the tree to position each node horizontally. This function is designed to position nodes in a tree structure horizontally based on their siblings and children.
    
    Parameters:
    - v: The current node in the tree to be positioned.
    - distance (optional): The default distance to be used when positioning nodes. Defaults to 1.0.
    
    Returns:
    - The current node (v) after positioning.
    
    This function recursively positions each node in the tree, ensuring that siblings are appropriately spaced and children are positioned relative to
    """

    if len(v.children) == 0:
        if v.lmost_sibling:
            v.x = v.lbrother().x + distance
        else:
            v.x = 0.0
    else:
        default_ancestor = v.children[0]
        for w in v.children:
            first_walk(w)
            default_ancestor = apportion(w, default_ancestor, distance)
        # print("finished v =", v.tree, "children")
        execute_shifts(v)

        midpoint = (v.children[0].x + v.children[-1].x) / 2

        w = v.lbrother()
        if w:
            v.x = w.x + distance
            v.mod = v.x - midpoint
        else:
            v.x = midpoint
    return v


def apportion(v, default_ancestor, distance):
    """
    Apportions the layout of a tree structure based on given parameters.
    
    This function is used to adjust the layout of a tree node and its siblings
    to ensure a balanced and aesthetically pleasing display. It calculates the
    necessary shifts and adjustments to the node's position and its children's
    positions based on the distance parameter.
    
    Parameters:
    v (Node): The current node in the tree whose layout needs to be adjusted.
    default_ancestor (Node): The default ancestor node, used for
    """

    w = v.lbrother()
    if w is not None:
        # in buchheim notation:
        # i == inner; o == outer; r == right; l == left; r = +; l = -
        vir = vor = v
        vil = w
        vol = v.lmost_sibling
        sir = sor = v.mod
        sil = vil.mod
        sol = vol.mod
        while vil.right() and vir.left():
            vil = vil.right()
            vir = vir.left()
            vol = vol.left()
            vor = vor.right()
            vor.ancestor = v
            shift = (vil.x + sil) - (vir.x + sir) + distance
            if shift > 0:
                move_subtree(ancestor(vil, v, default_ancestor), v, shift)
                sir = sir + shift
                sor = sor + shift
            sil += vil.mod
            sir += vir.mod
            sol += vol.mod
            sor += vor.mod
        if vil.right() and not vor.right():
            vor.thread = vil.right()
            vor.mod += sil - sor
        else:
            if vir.left() and not vol.left():
                vol.thread = vir.left()
                vol.mod += sir - sol
            default_ancestor = v
    return default_ancestor


def move_subtree(wl, wr, shift):
    subtrees = wr.number - wl.number
    # print(wl.tree, "is conflicted with", wr.tree, 'moving', subtrees,
    # 'shift', shift)
    # print wl, wr, wr.number, wl.number, shift, subtrees, shift/subtrees
    wr.change -= shift / subtrees
    wr.shift += shift
    wl.change += shift / subtrees
    wr.x += shift
    wr.mod += shift


def execute_shifts(v):
    shift = change = 0
    for w in v.children[::-1]:
        # print("shift:", w, shift, w.change)
        w.x += shift
        w.mod += shift
        change += w.change
        shift += w.shift + change


def ancestor(vil, v, default_ancestor):
    """
    Determine the common ancestor of a vertex in a tree.
    
    This function finds the common ancestor of a given vertex `v` in a tree,
    using the vertex `vil` and a default ancestor. If `vil.ancestor` is a child
    of `v.parent`, it returns `vil.ancestor`. Otherwise, it returns the
    `default_ancestor`.
    
    Parameters:
    vil (Vertex): The vertex from which to trace the ancestor.
    v (Vertex): The vertex for which to find
    """

    # the relevant text is at the bottom of page 7 of
    # "Improving Walker's Algorithm to Run in Linear Time" by Buchheim et al,
    # (2002)
    # https://citeseerx.ist.psu.edu/doc_view/pid/1f41c3c2a4880dc49238e46d555f16d28da2940d
    if vil.ancestor in v.parent.children:
        return vil.ancestor
    else:
        return default_ancestor


def second_walk(v, m=0, depth=0, min=None):
    v.x += m
    v.y = depth

    if min is None or v.x < min:
        min = v.x

    for w in v.children:
        min = second_walk(w, m + v.mod, depth + 1, min)

    return min


class Tree:
    def __init__(self, label="", node_id=-1, *children):
        self.label = label
        self.node_id = node_id
        if children:
            self.children = children
        else:
            self.children = []
]
a
