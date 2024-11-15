#!/usr/bin/env python

import os

import matplotlib.pylab as plt
import networkx as nx
import numpy
import pandas
from matplotlib.colors import TwoSlopeNorm


class Event:
    """
    An event object holds arbitrary event metadata
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class INode:
    """
    An INode is part of a Filesystem Trie
    We keep track of a count since we are going to use
    this to plot frequency of access.
    """

    def __init__(self, name, count=0):
        self.children = {}
        self.name = name
        self.count = count

    @property
    def basename(self):
        return os.path.basename(self.name) or os.sep

    @property
    def label(self):
        if self.count == 0:
            return self.basename
        return f"{self.basename}\n{self.count}"

    def increment(self, count):
        self.count += count


class Filesystem:
    """
    A Filesystem is a Trie of nodes
    """

    def __init__(self):
        self.root = INode(os.sep)
        self.min_count = 0
        self.max_count = 0

    def get_graph(self, font_size=10, tree=True, node_size=1000, title=None):
        """
        Get a plot for a trie
        """
        plt.figure(figsize=(20, 8))
        graph = nx.DiGraph()

        # Recursive function to walk through root, etc.
        color_counts = {}
        get_counts(counts=color_counts, node=self.root)
        add_to_graph(graph=graph, root=self.root, node=self.root)

        # Set a filter for the highest color so it doesn't bias the entire plot
        unique_counts = list(set(list(color_counts.values())))
        unique_counts.sort()
        without_outliers = reject_outliers(unique_counts)

        # Color based on count (outliers removed)!
        min_count = without_outliers[0]
        max_count = without_outliers[-1]
        colors = derive_node_colors(min_count=min_count, max_count=max_count + 1)

        # We only want to get colors that match the count, so the scale is relevant
        node_colors = []

        # Also update node labels to show count
        new_labels = {}
        for i, node in enumerate(graph.nodes):
            if node == "/":
                count = 0
                new_labels[node] = node
            else:
                count = color_counts[node]
                # Don't put label if count is 0!
                if count == 0:
                    new_labels[node] = node
                else:
                    new_labels[node] = f"{node}\n{count}"

            # This adjusts the color scale within the range
            # that does not have outliers
            if count < min_count:
                count = min_count
            if count > max_count:
                count = max_count
            node_colors.append(colors[count])

        # Tree visualization (much better) requires graphviz, dot, etc.
        if tree:
            for i, layer in enumerate(nx.topological_generations(graph)):
                for n in layer:
                    graph.nodes[n]["layer"] = i
            pos = nx.multipartite_layout(graph, subset_key="layer", align="horizontal")

            # Flip the layout so the root node is on top
            for k in pos:
                pos[k][-1] *= -1
        else:
            pos = nx.spring_layout(graph)

        # This will plot, and the user can call plt.show() or plt.savefig()
        title = title or "Filesystem Recording Trie"
        plt.title(title)
        nx.draw(
            graph,
            pos,
            with_labels=False,
            alpha=0.5,
            node_size=node_size,
            node_color=node_colors,
            font_size=font_size,
        )

        # Update and rotate the labels a bit
        for node, (x, y) in pos.items():
            plt.text(x, y, new_labels[str(node)], rotation=45, ha="center", va="center")
        plt.tight_layout()
        return graph

    def insert(self, path, count=0, remove_so_version=True):
        """
        Insert an INode into the filesystem.

        If we are adding a count, increment by it. We also build the tree
        without .so.<version> to compare across.
        """
        if remove_so_version:
            path = normalize_path(path)
        node = self.root
        partial_path = []
        for part in path.split(os.sep):
            partial_path.append(part)
            if part not in node.children:
                assembled_path = os.sep.join(partial_path)
                node.children[part] = INode(assembled_path)
            node = node.children[part]
        node.increment(count)

        # Update counts
        if node.count < self.min_count:
            self.min_count = node.count
        if node.count > self.max_count:
            self.max_count = node.count

    def find(self, path):
        """
        Search the filesystem for a path
        """
        node = self.root
        for part in path.split(os.sep):
            if part not in node.children:
                return
            node = node.children[part]
        return node


def reject_outliers(data, m=2.0):
    """
    Reject outliers to derive the color scale.
    """
    # Median isn't influenced by outliers
    d = numpy.abs(data - numpy.median(data))
    mdev = numpy.median(d)
    s = d / mdev if mdev else numpy.zeros(len(d))
    return numpy.array(data)[s < m]


def normalize_path(path):
    """
    Normalize the path, meaning removing so library versions.
    """
    if ".so." in path:
        return path.split(".so.")[0] + ".so"
    return path


class Traces:
    """
    A Set of traces to operate on.

    Lookup: is typically only done once
    Open: is when the file is read
    """

    def __init__(self, files=None):
        self.files = files or []
        self.check()

    def count(self):
        return len(self.files)

    def check(self):
        """
        Ensure that all trace files provided actually exist.
        """
        events = []
        for filename in self.files:
            filename = os.path.abspath(filename)
            if not os.path.exists(filename):
                raise ValueError(f"{filename} does not exist")
            events.append(filename)
        self.files = events

    def iter_events(self, operation="Open"):
        """
        Iterate through files and yield event object
        """
        for filename in self.files:
            basename = os.path.basename(filename)
            for line in read_file(filename).split("\n"):
                if not line:
                    continue
                # date, time, golang-file  timestamp function path
                # 2024/11/08 10:46:19 recorder.go:46: 1731062779714551943 Lookup     /etc
                parts = [x for x in line.split() if x]
                if parts[-2] != operation:
                    continue
                yield Event(
                    filename=filename,
                    basename=basename,
                    function=parts[-2],
                    path=parts[-1],
                    timestamp=int(parts[-3]),
                    normalized_path=normalize_path(parts[-1]),
                )

    def to_dataframe(self, operation="Open"):
        """
        Create a data frame of lookup values, we can save for later and derive paths from it.

        Normalized path removes the so version, if we find it. ms_in_state is milliseconds in state
        and is the time from the current event to the next, which is the time spent in that event.
        """
        df = pandas.DataFrame(
            columns=[
                "filename",
                "basename",
                "function",
                "path",
                "normalized_path",
                # This is a normalized path
                "previous_path",
                "timestamp",
                "ms_in_state",
            ]
        )
        idx = 0
        previous_timestamp = None
        previous_path = None
        current = None
        for event in self.iter_events(operation=operation):
            normalized_path = normalize_path(event.path)
            df.loc[idx, :] = [
                event.filename,
                os.path.basename(event.filename),
                event.function,
                event.path,
                normalized_path,
                previous_path,
                event.timestamp,
                None,
            ]
            if current is not None and event.filename != current:
                previous_path = None
                previous_timestamp = None
            if previous_timestamp is not None:
                df.loc[idx - 1, "ms_in_state"] = event.timestamp - previous_timestamp
            previous_timestamp = event.timestamp
            previous_path = normalized_path
            current = event.filename
            idx += 1
        return df

    def distance_matrix(self, operation="Open"):
        """
        Generate pairwise distance matrix for paths
        """
        lookup = self.as_paths(operation=operation)
        names = list(lookup.keys())
        df = pandas.DataFrame(index=names, columns=names)
        for filename1 in names:
            for filename2 in names:
                if filename1 > filename2:
                    continue
                aligned1, aligned2 = align_paths(lookup[filename1], lookup[filename2])
                distance = calculate_levenshtein(aligned1, aligned2)
                df.loc[filename1, filename2] = float(distance)
                df.loc[filename2, filename1] = float(distance)
        return df

    @property
    def samples(self):
        return list(self.as_paths().values())

    def iter_loo(self):
        """
        Yield train and test data for leave 1 out samples.
        Return the name of the test sample to identify it.
        I mostly just wanted to call this function "iter_loo" :)
        """
        paths = self.as_paths()
        for left_out in paths:
            train = [v for k, v in paths.items() if k != left_out]
            test = paths[left_out]
            yield train, test, left_out

    def as_paths(self, fullpath=False, operation="Open", remove_so_version=True):
        """
        Return lists of paths (lookup) corresponding to traces.
        """
        lookup = {}
        for event in self.iter_events(operation=operation):
            key = event.basename
            if fullpath:
                key = event.filename
            if key not in lookup:
                lookup[key] = []
            if remove_so_version:
                lookup[key].append(event.normalized_path)
            else:
                lookup[key].append(event.path)
        return lookup

    def all_counts(self, operation="Open", remove_so_version=True):
        """
        Return lookup of all counts corresponding to traces.

        Since we just have one lookup, this one is returned
        sorted.
        """
        lookup = {}
        for event in self.iter_events(operation=operation):
            path = event.path
            if remove_so_version:
                path = event.normalized_path
            if path not in lookup:
                lookup[path] = 0
            lookup[path] += 1
        return dict(sorted(lookup.items(), key=lambda item: item[1], reverse=True))

    def as_counts(self, fullpath=False, operation="Open", remove_so_version=True):
        """
        Return lookup of counts corresponding to traces.
        """
        lookup = {}
        for event in self.iter_events(operation=operation):
            key = event.basename
            if fullpath:
                key = event.filename
            if event.filename not in lookup:
                lookup[key] = {}
            path = event.path
            if remove_so_version:
                path = event.normalized_path
            if path not in lookup[key]:
                lookup[key][path] = 0
            lookup[key][path] += 1
        return lookup


def read_file(filename):
    with open(filename, "r") as fd:
        content = fd.read()
    return content


# Plotting helpers


def add_to_graph(graph, root, node, parent=None):
    """
    Helper function to add node to graph
    """
    if node != root:
        # This is probably a bug, just skip for now
        if node.basename != parent.basename:
            graph.add_edge(parent.basename, node.basename)
    for path, child in node.children.items():
        add_to_graph(graph=graph, root=root, node=child, parent=node)


def derive_node_colors(min_count, max_count):
    """
    Given the min, max, and a center, return a range of colors
    """
    palette = plt.cm.get_cmap("viridis")
    center = int(abs(max_count - min_count) / 2)
    norm = TwoSlopeNorm(vmin=min_count, vcenter=center, vmax=max_count)
    return [palette(norm(c)) for c in range(min_count, max_count)]


def get_counts(counts={}, node=None):
    """
    Get a flat list of counts
    """
    for path, child in node.children.items():
        counts[path] = child.count
        get_counts(counts, child)


# Alignment helpers


def align_paths(paths1, paths2, match_score=1, mismatch_score=-1, gap_penalty=-1):
    """
    This is a hacked Needleman-Wunsch algorithm for global sequence alignment,
    but instead of handling a sequence (string) we do two lists of paths
    """
    # Initialize the scoring matrix
    rows = len(paths1) + 1
    cols = len(paths2) + 1
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    # Fill the first row and column with gap penalties
    for i in range(1, rows):
        matrix[i][0] = matrix[i - 1][0] + gap_penalty
    for j in range(1, cols):
        matrix[0][j] = matrix[0][j - 1] + gap_penalty

    # Calculate the scores for the rest of the matrix
    for i in range(1, rows):
        for j in range(1, cols):
            match = matrix[i - 1][j - 1] + (
                match_score if paths1[i - 1] == paths2[j - 1] else mismatch_score
            )
            delete = matrix[i - 1][j] + gap_penalty
            insert = matrix[i][j - 1] + gap_penalty
            matrix[i][j] = max(match, delete, insert)

    # Backtrack to find the optimal alignment
    alignment1 = []
    alignment2 = []
    i = rows - 1
    j = cols - 1
    while i > 0 or j > 0:
        if (
            i > 0
            and j > 0
            and matrix[i][j]
            == matrix[i - 1][j - 1]
            + (match_score if paths1[i - 1] == paths2[j - 1] else mismatch_score)
        ):
            alignment1 = [paths1[i - 1]] + alignment1
            alignment2 = [paths2[j - 1]] + alignment2
            i -= 1
            j -= 1
        elif i > 0 and matrix[i][j] == matrix[i - 1][j] + gap_penalty:
            alignment1 = [paths1[i - 1]] + alignment1
            alignment2 = [""] + alignment2
            i -= 1
        else:
            alignment1 = [""] + alignment1
            alignment2 = [paths2[j - 1]] + alignment2
            j -= 1

    return alignment1, alignment2


def calculate_levenshtein(paths1, paths2):
    """
    Calculate Levenshtein distance between two sets of paths.
    They should already be aligned so we can compare the
    entries directly.

    For each, we save the pattern as a recording of whether the
    path is considered a deletion, insertion, or sub.
    """
    len1, len2 = len(paths1), len(paths2)

    # Create a matrix of zeros with dimensions (len1 + 1, len2 + 1)
    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    # Initialize the first row and column
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j

    # Fill the matrix
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if paths1[i - 1] == paths2[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,  # Deletion
                matrix[i][j - 1] + 1,  # Insertion
                matrix[i - 1][j - 1] + cost,  # Substitution
            )
    return matrix[-1][-1]
