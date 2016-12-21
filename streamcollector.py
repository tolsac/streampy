class Collector(object):
    class list:
        def collect(self, *args, **kwargs):
            iterable = kwargs.get('iterable', None)
            if not iterable:
                raise Exception('None iterable passed to collector.')
            return list(iterable)

    class group_by:
        def __init__(self, predicate):
            self.predicate = predicate

        def push(self, result, key, element):
            if not key in result:
                result[key] = [element]
            else:
                result[key].append(element)
            return result

        def collect(self, *args, **kwargs):
            iterable = kwargs.get('iterable', None)
            if not iterable:
                raise Exception('None iterable passed to collector.')
            result = {}
            for it in iterable:
                key = self.predicate(it)
                result = self.push(result, key, it)
            return result

    class count_by:
        def __init__(self, predicate):
            self.predicate = predicate

        def count(self, result, key):
            if not key in result:
                result[key] = 1
            else:
                result[key] += 1
            return result

        def collect(self, *args, **kwargs):
            iterable = kwargs.get('iterable', None)
            if not iterable:
                raise Exception('None iterable passed to collector.')
            result = {}
            for it in iterable:
                key = self.predicate(it)
                result = self.count(result, key)
            return result
