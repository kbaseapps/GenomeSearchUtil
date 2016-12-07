# -*- coding: utf-8 -*-
import gzip
import io
import codecs

# This class helps iterate over lines in .gz files or over lines in subprocess 
# output depending on source type.
class CombinedLineIterator:

    def __init__(self, source):
        if isinstance(source, basestring):
            self.index_file = io.TextIOWrapper(io.BufferedReader(gzip.open(source)),
                                               encoding="utf-8")
            self.process = None
        else:
            self.process = source
            self.index_file = None
        pass

    def close(self):
        if self.index_file:
            self.index_file.close()
        else:
            if self.process.poll() is None:
                self.process.kill()

    # iterator implementation
    def __iter__(self):
        if self.index_file:
            return self.index_file.__iter__()
        return self

    def next(self):
        if self.index_file:
            raise ValueError("Unsupported operation (call __iter__ first)")
        else:
            line = None
            while True:
                line = self.process.stdout.readline().decode('utf-8')
                if line == '' and self.process.poll() is not None:
                    raise StopIteration
                if line:
                    break
            return line

    # context management (inside "with" block)
    def __enter__(self):
        if self.index_file:
            return self.index_file.__enter__()
        else:
            return self

    def __exit__(self, *exc_info):
        self.close()
