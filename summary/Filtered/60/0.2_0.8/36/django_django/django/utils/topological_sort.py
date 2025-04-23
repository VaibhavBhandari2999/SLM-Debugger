class CyclicDependencyError(ValueError):
    pass


def topological_sort_as_sets(dependency_graph):
    """
    Variation of Kahn's algorithm (1962) that returns sets.

    Take a dependency graph as a dictionary of node => dependencies.

    Yield sets of items in topological order, where the first set contains
    all nodes without dependencies, and each following set contains all
    nodes that may depend on the nodes only in the previously yielded sets.
    """
    todo = dependency_graph.copy()
    while todo:
        current = {node for node, deps in todo.items() if not deps}

        if not current:
            raise CyclicDependencyError('Cyclic dependency in graph: {}'.format(
                ', '.join(repr(x) for x in todo.items())))

        yield current

        # remove current from todo's nodes & dependencies
        todo = {node: (dependencies - current) for node, dependencies in
                todo.items() if node not in current}


def stable_topological_sort(l, dependency_graph):
    """
    Sorts a list of elements based on a stable topological order of a given dependency graph.
    
    Parameters:
    l (list): A list of elements to be sorted.
    dependency_graph (dict): A dictionary representing the dependency graph where keys are nodes and values are sets of dependent nodes.
    
    Returns:
    list: A list of elements sorted in a stable topological order.
    
    This function first performs a topological sort on the dependency graph to get layers of nodes. Then, it iterates over these
    """

    result = []
    for layer in topological_sort_as_sets(dependency_graph):
        for node in l:
            if node in layer:
                result.append(node)
    return result
