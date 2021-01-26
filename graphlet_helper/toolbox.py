#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# 
# author: dan berenberg
import functools
from datetime import datetime

import torch

class _filetype(object):
    @staticmethod
    def read(filename):
        raise NotImplementedError

    @staticmethod
    def write(obj, filename):
        raise NotImplementedError


class listfile(_filetype):
    @staticmethod
    def read(filename):
        """Reads lines of a textfile"""
        with open(filename, 'r') as fRead:
            samples = list(map(lambda line: line.strip(), fRead))
        return samples
    
    @staticmethod
    def write(obj, filename):
        """Writes a list to a textfile, each entry occupying a different line"""
        with open(filename, 'w') as f:
            print(*obj, sep='\n', file=f)

class Timer(object):
    """Records time passed"""
    def __init__(self, jumpstart=False):
        self.__start_time = datetime.now() if jumpstart else None
        self.__stop_time  = None
        self.__elapsed = None
    
    @property
    def start_time(self):
        return self.__start_time

    @property
    def stop_time(self):
        return self.__stop_time

    @property
    def elapsed_time(self):
        if self.__stop_time is not None:
            return self.__stop_time - self.__start_time
        else:
            return datetime.now() - self.__start_time
        
    def start(self):
        if self.__start_time is None:
            self.__start_time = datetime.now()
        return self

    def stop(self):
        if self.__stop_time is None:
            self.__stop_time = datetime.now()
            self.__elapsed_time = self.__stop_time - self.__start_time

        return self

class Composer(object):
    """
    Composes several callables, assumes the i/o types of each callable are amicable
    """
    def __init__(self, *callables):
        self._callables = callables
        self._composition = self._compose(iter(callables), self.identity)

    def identity(self, x):
        return x

    def __len__(self):
        return len(self._callables)

    def feeding_to(self, fn):
        return Composer(*self._callables, fn)

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            return Composer(*self._callables[start:stop:step])
        elif isinstance(key, int):
            return self._callables[key]
        elif isinstance(key, tuple):
            return NotImplementedError(f"tuple as index")
        else:
            raise TypeError(f"Invalid argument type: {type(key)}")

    def _compose(self, funcerator, f):
        try:
            g = next(funcerator)
            @functools.wraps(g)
            def h(*args, **kwargs):
                return g(f(*args, **kwargs))
            return self._compose(funcerator, h)
        except StopIteration:
            return f

    def __call__(self, x):
        return self._composition(x)

class AdjacencyMatrixMaker(object):
    """Converts a distance map to an adjacency matrix"""
    def __init__(self, threshold, selfloop=True):
        self._threshold = threshold
        self._selfloop  = selfloop

    @property
    def weighted(self):
        return self._weighted

    @property
    def threshold(self):
        return self._threshold

    def convert(self, distance_map):
        A = distance_map.clone()
        A = ( A <= self._threshold ).float()
        if not self._selfloop:
            n = A.shape[0]
            mask = torch.eye(n).bool()
            A.masked_fill_(mask, 0)
        return A

    def __call__(self, distance_map):
        return self.convert(distance_map)

class CoordLoader(object):
    """
    Converts an N x 3 matrix to an distance matrix
    """
    def __init__(self, silent_if_square=True):
        """
        initialize
        args:
            :silent_if_square (bool) - do nothing if the input matrix is already square
        """
        self.silent_if_square = silent_if_square

    def convert(self, coords):
        shape = coords.shape
        assert len(shape) == 2 
        
        if (shape[0] == shape[1]) and self.silent_if_square:
            return coords # do nothing when the input is already a square matrix
        else:
            assert shape[1] == 3
            return torch.cdist(coords, coords, p=2)

    def __call__(self, coords):
        return self.convert(coords)

if __name__ == '__main__':
    pass

