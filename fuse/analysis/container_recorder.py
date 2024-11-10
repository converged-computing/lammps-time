#!/usr/bin/env python

import pandas
import os


class Event:
    """
    An event object holds arbitrary event metadata
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


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
                )

    def to_dataframe(self, operation="Open"):
        """
        Create a data frame of lookup values, we can save for later and derive paths from it
        """
        df = pandas.DataFrame(columns=["filename", "function", "path", "timestamp"])
        idx = 0
        for event in self.iter_events(operation=operation):
            df.loc[idx, :] = [
                event.filename,
                event.function,
                event.path,
                event.timestamp,
            ]
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
                df.loc[filename1, filename2] = distance
                df.loc[filename2, filename1] = distance
        return df

    def as_paths(self, fullpath=False, operation="Open"):
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
            lookup[key].append(event.path)
        return lookup

    def all_counts(self, operation="Open"):
        """
        Return lookup of all counts corresponding to traces.

        Since we just have one lookup, this one is returned
        sorted.
        """
        lookup = {}
        for event in self.iter_events(operation=operation):
            if event.path not in lookup:
                lookup[event.path] = 0
            lookup[event.path] += 1
        return dict(sorted(lookup.items(), key=lambda item: item[1], reverse=True))

    def as_counts(self, fullpath=False, operation="Open"):
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
            if event.path not in lookup[key]:
                lookup[key][event.path] = 0
            lookup[key][event.path] += 1
        return lookup


def read_file(filename):
    with open(filename, "r") as fd:
        content = fd.read()
    return content


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
