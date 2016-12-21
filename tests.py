from streampy import Stream
from streamcollector import Collector
from compatibility import _comparer
import unittest


class CreationTest(unittest.TestCase):
    def test_create_stream_without_params(self):
        s = Stream()
        self.assertEquals(0, s.size())

    def test_create_stream_with_list_params(self):
        s = Stream([])
        self.assertEquals(0, s.size())
        s = Stream([1])
        self.assertEquals(1, s.size())

    def test_create_stream_with_generator_params(self):
        s = Stream.range(1000)
        self.assertEquals(1000, s.size())

    def test_create_stream_with_bad_type(self):
        self.assertRaises(TypeError, Stream.__init__, Stream(), None)

    def test_create_stream_with_more_than_one_param(self):
        self.assertRaises(TypeError, Stream.__init__, Stream(), *([], []))


class SizeTest(unittest.TestCase):
    def test_simple_size_1(self):
        self.assertEquals(Stream.range(999).size(), 999)

    def test_simple_size_2(self):
        self.assertEquals(Stream.range(0).size(), 0)

    def test_simple_size_3(self):
        s = Stream("azertyuiop").filter(lambda x: x == 'a')
        self.assertEquals(s.size(), 1)


class FilterTest(unittest.TestCase):
    def test_simple_filter_1(self):
        s = Stream.range(10).filter(lambda x: x % 2 == 0).list()
        self.assertEquals(s, [0, 2, 4, 6, 8])
        s = Stream(['this', 'is', 'a', 'pretty', 'cat']).filter(lambda x: x != 'cat').list()
        self.assertEquals(s, ['this', 'is', 'a', 'pretty'])

    def test_simple_filter_2(self):
        s = Stream('a simple string').filter(lambda x: x == 'a').list()
        self.assertEquals(s, ['a'])

    def test_simple_filter_3(self):
        s = Stream.range(100001).filter(lambda x: x > 50000)
        self.assertEquals(50000, s.size())


class ExcludeTest(unittest.TestCase):
    def test_simple_exclude_1(self):
        s = Stream.range(10).exclude(lambda x: x % 2 == 0).list()
        self.assertEquals(s, [1, 3, 5, 7, 9])
        s = Stream(['this', 'is', 'a', 'pretty', 'cat']).exclude(lambda x: x == 'cat').list()
        self.assertEquals(s, ['this', 'is', 'a', 'pretty'])

    def test_simple_exclude_2(self):
        s = ''.join(Stream('a simple string').exclude(lambda x: x == 'a').list())
        self.assertEquals(s, ' simple string')

    def test_simple_exclude_3(self):
        s = Stream.range(100001).exclude(lambda x: x > 50000)
        self.assertEquals(50001, s.size())


class MapTest(unittest.TestCase):
    def test_simple_map_1(self):
        def add(x, y):
            return x + y

        s = Stream.range(10000).map(lambda x: x * 2).reduce(add, initializer=0)
        self.assertEquals(s, 99990000)

    def test_simple_map_2(self):
        def to_dict(obj):
            return {str(obj): obj}

        s = Stream.range(10000).map(to_dict).size()
        self.assertEquals(s, 10000)

    def test_simple_map_3(self):
        def to_dict(obj):
            return {str(obj): obj}

        s = Stream([1, 2, 3]).map(to_dict).list()
        self.assertEqual(s, [{'1': 1}, {'2': 2}, {'3': 3}])


class ChainTest(unittest.TestCase):
    def test_simple_chain_1(self):
        self.assertEqual(Stream([1]).chain([2]).size(), 2)

    def test_simple_chain_2(self):
        self.assertEqual(Stream([1]).chain([2]).chain(Stream([3, 4, 5])).size(), 5)


class SortTest(unittest.TestCase):
    def test_simple_sort_1(self):
        self.assertEquals(Stream([1, 3, 2, 5, 4, 6]).sort(cmp=lambda x, y: _comparer(x, y)).list(), [1, 2, 3, 4, 5, 6])

    def test_simple_sort_2(self):
        self.assertEquals(Stream([1, 3, 2, 5, 4, 6]).sort(cmp=lambda x, y: _comparer(y, x)).list(), [6, 5, 4, 3, 2, 1])


class LimitTest(unittest.TestCase):
    def test_simple_limit_1(self):
        self.assertEquals(Stream([1, 3, 2, 5, 4, 6]).limit(2).list(), [1, 3])

    def test_simple_limit_2(self):
        self.assertEquals(Stream([1, 3, 2, 5, 4, 6]).limit(0).list(), [])

    def test_simple_limit_3(self):
        self.assertEquals(Stream("yeah baby !").limit(4).list(), ['y', 'e', 'a', 'h'])


class AnyTest(unittest.TestCase):
    def test_simple_any_1(self):
        self.assertEquals(Stream([1, 3, 2, 5, 4, 6]).limit(2).any(lambda x: x == 1), True)

    def test_simple_any_2(self):
        self.assertEquals(Stream([1, 3, 2, 5, 4, 6]).limit(2).any(lambda x: x == 2), False)

    def test_simple_any_3(self):
        self.assertEquals(Stream("yeah baby !").any(lambda x: 'a' < x < 'c'), True)


class AllTest(unittest.TestCase):
    def test_simple_all_1(self):
        self.assertEquals(Stream([1, 3, 2, 5, 4, 6]).limit(2).all(lambda x: 1 <= x <= 6), True)

    def test_simple_all_2(self):
        self.assertEquals(Stream([3, 3, 2, 5, 4, 6]).limit(2).all(lambda x: x == 3), True)

    def test_simple_all_3(self):
        self.assertEquals(Stream('yeah baby !').all(lambda x: 'a' < x < 'c'), False)


class MinTest(unittest.TestCase):
    def test_simple_all_1(self):
        self.assertEquals(Stream([1, 3, 2, 5, 4, 6]).min(), 1)

    def test_simple_all_2(self):
        self.assertEquals(Stream([3, 3, 2, 5, 4, 6]).min(), 2)


class MaxTest(unittest.TestCase):
    def test_simple_all_1(self):
        self.assertEquals(Stream([1, 3, 2, 5, 4, 6]).max(), 6)

    def test_simple_all_2(self):
        self.assertEquals(Stream([4, 42, 2, 5, 4, 6]).max(), 42)


class RangeTest(unittest.TestCase):
    def test_simple_range_1(self):
        self.assertEquals(Stream.range(10).list(), list(range(10)))

    def test_simple_range_2(self):
        self.assertEquals(Stream.range(42000).list(), list(range(42000)))


class FirstTest(unittest.TestCase):
    def test_simple_first_1(self):
        self.assertEquals(Stream.range(10).first(), 0)

    def test_simple_first_2(self):
        self.assertEquals(Stream.range(10).first(predicate=lambda x: x > 1), 2)


class LastTest(unittest.TestCase):
    def test_simple_last_1(self):
        self.assertEquals(Stream.range(10).last(), 9)

    def test_simple_last_2(self):
        self.assertEquals(Stream.range(10).last(predicate=lambda x: x > 1), 9)

    def test_simple_last_3(self):
        self.assertEquals(Stream.range(423).last(predicate=lambda x: 42 < x < 46), 45)


class SkipTest(unittest.TestCase):
    def test_simple_skip_1(self):
        self.assertEquals(Stream.range(10).skip(9).list(), [9])

    def test_simple_skip_2(self):
        self.assertEquals(Stream.range(10).skip(15).list(), [])


class GetItemTest(unittest.TestCase):
    def test_simple_getitem_1(self):
        self.assertEquals(Stream.range(10)[0], 0)

    def test_simple_getitem_2(self):
        self.assertEquals(Stream.range(430)[50], 50)

    def test_simple_getitem_3(self):
        self.assertRaises(IndexError, Stream.__getitem__, Stream([]), 1)


class DistinctTest(unittest.TestCase):
    def test_simple_distinct_1(self):
        self.assertEquals(Stream.range(100).chain(Stream.range(100)).distinct().list(), Stream.range(100).list())

    def test_simple_distinct_2(self):
        self.assertEquals(Stream([1, 1, 1, 1, 1, 1.0, 2]).distinct().list(), [1, 2])


class SubstreamTest(unittest.TestCase):
    def test_simple_substream_1(self):
        self.assertEqual(Stream([1, 2, 3, 4]).substream(0, 1).list(), [1])

    def test_simple_substream_2(self):
        self.assertEqual(Stream([1, 2, 3, 4]).substream(1, 1).list(), [])

    def test_simple_substream_3(self):
        self.assertEqual(Stream([1, 2, 3, 4]).substream(1, 2).list(), [2])

    def test_simple_substream_4(self):
        s = Stream.range(100) \
            .chain(Stream.range(100, 1000)) \
            .substream(100, 200).list()
        self.assertEqual(s, list(range(100, 200)))


class ChunkTest(unittest.TestCase):
    def test_simple_chunk_1(self):
        self.assertEqual(Stream.range(10).chunk(2).list(), [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]])

    def test_simple_chunk_2(self):
        self.assertEqual(Stream.range(10).chunk(3).list(), [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]])

    def test_simple_chunk_3(self):
        self.assertEqual(Stream.range(1).chunk(2).list(), [[0]])


class FunctionnalTest(unittest.TestCase):
    def test_simple_1(self):
        element = Stream \
            .range(100000) \
            .filter(lambda x: x % 2 == 0) \
            .map(lambda x: str(x)) \
            .map(lambda x: 'hey{0}'.format(x)) \
            .first()
        self.assertEquals(element, 'hey0')

    def test_simple_2(self):
        element = Stream \
            .range(100000) \
            .filter(lambda x: x % 2 == 0) \
            .map(lambda x: str(x)) \
            .map(lambda x: 'hey{0}'.format(x)) \
            .limit(10) \
            .last()
        self.assertEquals(element, 'hey18')

    def test_simple_3(self):
        element = Stream.range(100000) \
            .filter(lambda x: x % 2 == 0) \
            .map(lambda x: str(x)) \
            .map(lambda x: 'Hi{0}'.format(x)) \
            .map(lambda x: x.upper()) \
            .filter(lambda x: x.endswith('8')) \
            .limit(10) \
            .map(lambda x: x[2]) \
            .skip(1) \
            .map(int) \
            .list()
        self.assertEquals(element, list(range(1, 10)))

    def test_simple_4(self):
        element = Stream(['You', 'shall', 'not', 'pass']) \
            .map(lambda x: x.upper()) \
            .exclude(lambda x: x == 'NOT') \
            .exclude(lambda x: x == 'PASS') \
            .chain(["pass"]) \
            .map(lambda x: x.upper()) \
            .list()
        self.assertEquals(element, ['YOU', 'SHALL', 'PASS'])


class CollectTest(unittest.TestCase):
    def test_collect_simple_list(self):
        lst = Stream.range(10) \
            .map(lambda x: x * 2) \
            .collect(Collector.list())
        self.assertEqual(lst, [0, 2, 4, 6, 8, 10, 12, 14, 16, 18])

    def test_collect_simple_group_by(self):
        peoples = [
            {'name': 'Camille', 'age': 24},
            {'name': 'Laurent', 'age': 22},
            {'name': 'Matthias', 'age': 21},
            {'name': 'Bertrand', 'age': 25},
            {'name': 'David', 'age': 22},
        ]

        res = {
            21: [{'name': 'Matthias', 'age': 21}],
            22: [
                    {'name': 'Laurent', 'age': 22},
                    {'name': 'David', 'age': 22},
                 ],
            24: [{'name': 'Camille', 'age': 24}],
            25: [{'name': 'Bertrand', 'age': 25}]
        }

        lst = Stream(peoples) \
            .collect(Collector.group_by(lambda x: x['age']))
        self.assertEqual(lst, res)

    def test_collect_simple_count_by(self):
        peoples = [
            {'name': 'Camille', 'age': 24},
            {'name': 'Laurent', 'age': 22},
            {'name': 'Matthias', 'age': 21},
            {'name': 'Bertrand', 'age': 25},
            {'name': 'David', 'age': 22},
        ]

        res = {
            21: 1,
            22: 2,
            24: 1,
            25: 1
        }

        lst = Stream(peoples) \
            .collect(Collector.count_by(lambda x: x['age']))
        self.assertEqual(lst, res)
