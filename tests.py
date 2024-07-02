import unittest
from unittest.mock import mock_open, patch
import pathlib

from streampy import Stream


class CreationTest(unittest.TestCase):
    def test_create_stream_without_params(self):
        s = Stream()
        self.assertEqual(0, s.size())

    def test_create_stream_with_list_params(self):
        s = Stream([])
        self.assertEqual(0, s.size())

        s = Stream([1])
        self.assertEqual(1, s.size())

        s = Stream([1, 2, 3])
        self.assertEqual(3, s.size())

    def test_create_stream_with_generator_params(self):
        s = Stream.range(1000)
        self.assertEqual(1000, s.size())

    def test_create_stream_with_bad_type(self):
        self.assertRaises(TypeError, Stream.__init__, Stream(), None)

    def test_create_stream_with_more_than_one_param(self):
        self.assertRaises(TypeError, Stream.__init__, Stream(), *([], []))


class SizeTest(unittest.TestCase):
    def test_simple_size_1(self):
        self.assertEqual(Stream.range(999).size(), 999)

    def test_simple_size_2(self):
        self.assertEqual(Stream.range(0).size(), 0)

    def test_simple_size_3(self):
        s = Stream("azertyuiop")
        self.assertEqual(s.size(), 10)


class FilterTest(unittest.TestCase):
    def test_simple_filter_1(self):
        s = Stream.range(10).filter(lambda x: x % 2 == 0).to_list()
        self.assertEqual(s, [0, 2, 4, 6, 8])
        s = (
            Stream(["this", "is", "a", "pretty", "cat"])
            .filter(lambda x: x != "cat")
            .to_list()
        )
        self.assertEqual(s, ["this", "is", "a", "pretty"])

    def test_simple_filter_2(self):
        s = Stream("a simple string").filter(lambda x: x == "a").to_list()
        self.assertEqual(s, ["a"])

    def test_simple_filter_3(self):
        s = Stream.range(100001).filter(lambda x: x > 50000)
        self.assertEqual(50000, s.size())


class ExcludeTest(unittest.TestCase):
    def test_simple_exclude_1(self):
        s = Stream.range(10).exclude(lambda x: x % 2 == 0).to_list()
        self.assertEqual(s, [1, 3, 5, 7, 9])
        s = (
            Stream(["this", "is", "a", "pretty", "cat"])
            .exclude(lambda x: x == "cat")
            .to_list()
        )
        self.assertEqual(s, ["this", "is", "a", "pretty"])

    def test_simple_exclude_2(self):
        s = "".join(Stream("a simple string").exclude(lambda x: x == "a").to_list())
        self.assertEqual(s, " simple string")

    def test_simple_exclude_3(self):
        s = Stream.range(100001).exclude(lambda x: x > 50000)
        self.assertEqual(50001, s.size())


class MapTest(unittest.TestCase):
    def test_simple_map_1(self):
        def add(x, y):
            return x + y

        s = Stream.range(10000).map(lambda x: x * 2).reduce(add, initial=0)
        self.assertEqual(s, 99990000)

    def test_simple_map_2(self):
        def to_dict(obj):
            return {str(obj): obj}

        s = Stream.range(10000).map(to_dict).size()
        self.assertEqual(s, 10000)

    def test_simple_map_3(self):
        def to_dict(obj):
            return {str(obj): obj}

        s = Stream([1, 2, 3]).map(to_dict).to_list()
        self.assertEqual(s, [{"1": 1}, {"2": 2}, {"3": 3}])


class ChainTest(unittest.TestCase):
    def test_simple_chain_1(self):
        self.assertEqual(Stream([1]).chain([2]).size(), 2)

    def test_simple_chain_2(self):
        self.assertEqual(Stream([1]).chain([2]).chain(Stream([3, 4, 5])).size(), 5)


class LimitTest(unittest.TestCase):
    def test_simple_limit_1(self):
        self.assertEqual(Stream([1, 3, 2, 5, 4, 6]).limit(2).to_list(), [1, 3])

    def test_simple_limit_2(self):
        self.assertEqual(Stream([1, 3, 2, 5, 4, 6]).limit(0).to_list(), [])

    def test_simple_limit_3(self):
        self.assertEqual(Stream("yeah baby !").limit(4).to_list(), ["y", "e", "a", "h"])


class AnyTest(unittest.TestCase):
    def test_simple_any_1(self):
        self.assertEqual(
            Stream([1, 3, 2, 5, 4, 6]).limit(2).any(lambda x: x == 1), True
        )

    def test_simple_any_2(self):
        self.assertEqual(
            Stream([1, 3, 2, 5, 4, 6]).limit(2).any(lambda x: x == 2), False
        )

    def test_simple_any_3(self):
        self.assertEqual(Stream("yeah baby !").any(lambda x: "a" < x < "c"), True)


class AllTest(unittest.TestCase):
    def test_simple_all_1(self):
        self.assertEqual(
            Stream([1, 3, 2, 5, 4, 6]).limit(2).all(lambda x: 1 <= x <= 6), True
        )

    def test_simple_all_2(self):
        self.assertEqual(
            Stream([3, 3, 2, 5, 4, 6]).limit(2).all(lambda x: x == 3), True
        )

    def test_simple_all_3(self):
        self.assertEqual(Stream("yeah baby !").all(lambda x: "a" < x < "c"), False)


class MinTest(unittest.TestCase):
    def test_simple_all_1(self):
        self.assertEqual(Stream([1, 3, 2, 5, 4, 6]).min(), 1)

    def test_simple_all_2(self):
        self.assertEqual(Stream([3, 3, 2, 5, 4, 6]).min(), 2)


class MaxTest(unittest.TestCase):
    def test_simple_all_1(self):
        self.assertEqual(Stream([1, 3, 2, 5, 4, 6]).max(), 6)

    def test_simple_all_2(self):
        self.assertEqual(Stream([4, 42, 2, 5, 4, 6]).max(), 42)


class RangeTest(unittest.TestCase):
    def test_simple_range_1(self):
        self.assertEqual(Stream.range(10).to_list(), list(range(10)))

    def test_simple_range_2(self):
        self.assertEqual(Stream.range(42000).to_list(), list(range(42000)))


class FirstTest(unittest.TestCase):
    def test_simple_first_1(self):
        self.assertEqual(Stream.range(10).first(), 0)


class LastTest(unittest.TestCase):
    def test_simple_last_1(self):
        self.assertEqual(Stream.range(10).last(), 9)


class GetItemTest(unittest.TestCase):
    def test_simple_getitem_1(self):
        self.assertEqual(Stream.range(10)[0], 0)

    def test_simple_getitem_2(self):
        self.assertEqual(Stream.range(430)[50], 50)

    def test_simple_getitem_3(self):
        self.assertRaises(IndexError, Stream.__getitem__, Stream([]), 1)


class DistinctTest(unittest.TestCase):
    def test_distinct_with_duplicates(self):
        s = Stream([1, 2, 2, 3, 4, 4, 5])
        self.assertEqual(s.distinct().to_list(), [1, 2, 3, 4, 5])

    def test_distinct_with_no_duplicates(self):
        s = Stream([1, 2, 3, 4, 5])
        self.assertEqual(s.distinct().to_list(), [1, 2, 3, 4, 5])

    def test_distinct_with_empty_stream(self):
        s = Stream([])
        self.assertEqual(s.distinct().to_list(), [])

    def test_distinct_with_all_duplicates(self):
        s = Stream([1, 1, 1, 1, 1])
        self.assertEqual(s.distinct().to_list(), [1])

    def test_distinct_with_mixed_types(self):
        s = Stream([1, "a", 1, "b", "a"])
        self.assertEqual(s.distinct().to_list(), [1, "a", "b"])

    def test_distinct_with_predicate(self):
        s = Stream(["apple", "banana", "apricot", "blueberry"])
        self.assertEqual(s.distinct(lambda x: x[0]).to_list(), ["apple", "banana"])

    def test_distinct_with_predicate_and_duplicates(self):
        s = Stream(["apple", "banana", "apricot", "blueberry", "avocado"])
        self.assertEqual(s.distinct(lambda x: x[0]).to_list(), ["apple", "banana"])

    def test_distinct_with_complex_objects(self):
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

            def __repr__(self):
                return f"Person(name={self.name}, age={self.age})"

        p1 = Person("Alice", 30)
        p2 = Person("Bob", 30)
        p3 = Person("Alice", 40)
        s = Stream([p1, p2, p3])
        self.assertEqual(s.distinct(lambda x: x.name).to_list(), [p1, p2])

    def test_distinct_with_non_hashable_elements(self):
        s = Stream([[1, 2], [1, 2], [3, 4]])
        self.assertEqual(s.distinct(lambda x: tuple(x)).to_list(), [[1, 2], [3, 4]])

    def test_simple_distinct_1(self):
        self.assertEqual(
            Stream.range(100).chain(Stream.range(100)).distinct().to_list(),
            Stream.range(100).to_list(),
        )

    def test_simple_distinct_2(self):
        self.assertEqual(Stream([1, 1, 1, 1, 1, 1.0, 2]).distinct().to_list(), [1, 2])


class CompactTest(unittest.TestCase):
    def test_simple_compact_1(self):
        self.assertEqual(Stream([1, None, 2, None, 3]).compact().to_list(), [1, 2, 3])


class ChunkTest(unittest.TestCase):
    def test_simple_chunk_1(self):
        self.assertEqual(
            Stream.range(10).chunk(2).to_list(),
            [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
        )

    def test_simple_chunk_2(self):
        self.assertEqual(
            Stream.range(10).chunk(3).to_list(), [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        )

    def test_simple_chunk_3(self):
        self.assertEqual(Stream.range(1).chunk(2).to_list(), [[0]])


class FunctionnalTest(unittest.TestCase):
    def test_simple_1(self):
        element = (
            Stream.range(100000)
            .filter(lambda x: x % 2 == 0)
            .map(lambda x: str(x))
            .map(lambda x: "hey{0}".format(x))
            .first()
        )
        self.assertEqual(element, "hey0")

    def test_simple_2(self):
        element = (
            Stream.range(100000)
            .filter(lambda x: x % 2 == 0)
            .map(lambda x: str(x))
            .map(lambda x: "hey{0}".format(x))
            .limit(10)
            .last()
        )
        self.assertEqual(element, "hey18")

    def test_simple_3(self):
        element = (
            Stream.range(100000)
            .filter(lambda x: x % 2 == 0)
            .map(lambda x: str(x))
            .map(lambda x: "Hi{0}".format(x))
            .map(lambda x: x.upper())
            .filter(lambda x: x.endswith("8"))
            .limit(10)
            .map(lambda x: x[2])
            .skip(1)
            .map(int)
            .to_list()
        )
        self.assertEqual(element, list(range(1, 10)))

    def test_simple_4(self):
        element = (
            Stream(["You", "shall", "not", "pass"])
            .map(lambda x: x.upper())
            .exclude(lambda x: x == "NOT")
            .exclude(lambda x: x == "PASS")
            .chain(["pass"])
            .map(lambda x: x.upper())
            .to_list()
        )
        self.assertEqual(element, ["YOU", "SHALL", "PASS"])


class FindIndexTest(unittest.TestCase):
    def test_find_index_exists(self):
        s = Stream.range(10)
        self.assertEqual(s.find_index(lambda x: x == 5), 5)

    def test_find_index_not_exists(self):
        s = Stream.range(10)
        self.assertEqual(s.find_index(lambda x: x == 10), -1)

    def test_find_index_first_element(self):
        s = Stream.range(10)
        self.assertEqual(s.find_index(lambda x: x == 0), 0)

    def test_find_index_last_element(self):
        s = Stream.range(10)
        self.assertEqual(s.find_index(lambda x: x == 9), 9)

    def test_find_index_with_non_integers(self):
        s = Stream(["apple", "banana", "cherry"])
        self.assertEqual(s.find_index(lambda x: x == "banana"), 1)


class FlattenTest(unittest.TestCase):
    def test_flatten_simple_lists(self):
        s = Stream([[1, 2], [3, 4], [5, 6]])
        self.assertEqual(s.flatten().to_list(), [1, 2, 3, 4, 5, 6])

    def test_flatten_empty_lists(self):
        s = Stream([[], [], []])
        self.assertEqual(s.flatten().to_list(), [])

    def test_flatten_mixed_empty_and_non_empty_lists(self):
        s = Stream([[1, 2], [], [3, 4]])
        self.assertEqual(s.flatten().to_list(), [1, 2, 3, 4])

    def test_flatten_nested_lists(self):
        s = Stream([[1, [2, 3]], [4], [5, [6]]])
        self.assertEqual(s.flatten().to_list(), [1, [2, 3], 4, 5, [6]])

    def test_flatten_non_list_elements(self):
        s = Stream([[1, 2], "abc", [3, 4]])
        self.assertEqual(s.flatten().to_list(), [1, 2, "a", "b", "c", 3, 4])


class FlattenDeepTest(unittest.TestCase):
    def test_flatten_deep_simple_lists(self):
        s = Stream([1, [2, [3, 4], 5], 6])
        self.assertEqual(s.flatten_deep().to_list(), [1, 2, 3, 4, 5, 6])

    def test_flatten_deep_empty_lists(self):
        s = Stream([[], [], []])
        self.assertEqual(s.flatten_deep().to_list(), [])

    def test_flatten_deep_mixed_empty_and_non_empty_lists(self):
        s = Stream([[1, 2], [], [3, [4]]])
        self.assertEqual(s.flatten_deep().to_list(), [1, 2, 3, 4])

    def test_flatten_deep_with_strings(self):
        s = Stream(["a", ["b", ["c"]], "d"])
        self.assertEqual(s.flatten_deep().to_list(), ["a", "b", "c", "d"])

    def test_flatten_deep_nested_empty_lists(self):
        s = Stream([1, [2, [], [3, [], 4], 5], 6])
        self.assertEqual(s.flatten_deep().to_list(), [1, 2, 3, 4, 5, 6])


class JoinTest(unittest.TestCase):
    def test_join_with_comma(self):
        s = Stream(["a", "b", "c"])
        self.assertEqual(s.join(","), "a,b,c")

    def test_join_with_empty_string(self):
        s = Stream(["a", "b", "c"])
        self.assertEqual(s.join(""), "abc")

    def test_join_single_element(self):
        s = Stream(["a"])
        self.assertEqual(s.join(","), "a")

    def test_join_empty_stream(self):
        s = Stream([])
        self.assertEqual(s.join(","), "")

    def test_join_with_numbers(self):
        s = Stream([1, 2, 3])
        self.assertEqual(s.join(","), "1,2,3")


class RemoveTest(unittest.TestCase):
    def test_remove_even_numbers(self):
        s = Stream.range(10).remove(lambda x: x % 2 == 0)
        self.assertEqual(s.to_list(), [1, 3, 5, 7, 9])

    def test_remove_odd_numbers(self):
        s = Stream.range(10).remove(lambda x: x % 2 != 0)
        self.assertEqual(s.to_list(), [0, 2, 4, 6, 8])

    def test_remove_all_elements(self):
        s = Stream.range(10).remove(lambda x: True)
        self.assertEqual(s.to_list(), [])

    def test_remove_no_elements(self):
        s = Stream.range(10).remove(lambda x: False)
        self.assertEqual(s.to_list(), list(range(10)))

    def test_remove_specific_value(self):
        s = Stream.range(10).remove(lambda x: x == 5)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4, 6, 7, 8, 9])


class AdditionalStreamTests(unittest.TestCase):
    def test_first_on_non_empty_stream(self):
        s = Stream.range(5)
        self.assertEqual(s.first(), 0)

    def test_first_on_empty_stream(self):
        s = Stream([])
        self.assertIsNone(s.first())

    def test_last_on_non_empty_stream(self):
        s = Stream.range(5)
        self.assertEqual(s.last(), 4)

    def test_last_on_empty_stream(self):
        s = Stream([])
        self.assertIsNone(s.last())

    def test_any_true(self):
        s = Stream.range(10)
        self.assertTrue(s.any(lambda x: x > 5))

    def test_any_false(self):
        s = Stream.range(10)
        self.assertFalse(s.any(lambda x: x > 10))

    def test_all_true(self):
        s = Stream.range(10)
        self.assertTrue(s.all(lambda x: x < 10))

    def test_all_false(self):
        s = Stream.range(10)
        self.assertFalse(s.all(lambda x: x < 5))


class DropTest(unittest.TestCase):
    def test_drop_first_few_elements(self):
        s = Stream.range(10).drop(3)
        self.assertEqual(s.to_list(), [3, 4, 5, 6, 7, 8, 9])

    def test_drop_more_than_length(self):
        s = Stream.range(5).drop(10)
        self.assertEqual(s.to_list(), [])

    def test_drop_zero_elements(self):
        s = Stream.range(5).drop(0)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4])

    def test_drop_negative(self):
        with self.assertRaises(ValueError):
            Stream.range(5).drop(-1)


class DropWhileTest(unittest.TestCase):
    def test_drop_while_less_than_5(self):
        s = Stream.range(10).drop_while(lambda x: x < 5)
        self.assertEqual(s.to_list(), [5, 6, 7, 8, 9])

    def test_drop_while_all_elements(self):
        s = Stream.range(10).drop_while(lambda x: x < 10)
        self.assertEqual(s.to_list(), [])

    def test_drop_while_none_elements(self):
        s = Stream.range(10).drop_while(lambda x: x < 0)
        self.assertEqual(s.to_list(), list(range(10)))

    def test_drop_while_complex_condition(self):
        s = Stream(["a", "bb", "ccc", "dddd"]).drop_while(lambda x: len(x) < 3)
        self.assertEqual(s.to_list(), ["ccc", "dddd"])


class DropRightTest(unittest.TestCase):
    def test_drop_right_few_elements(self):
        s = Stream.range(10).drop_right(3)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4, 5, 6])

    def test_drop_right_more_than_length(self):
        s = Stream.range(5).drop_right(10)
        self.assertEqual(s.to_list(), [])

    def test_drop_right_zero_elements(self):
        s = Stream.range(5).drop_right(0)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4])

    def test_drop_right_negative(self):
        s = Stream.range(5).drop_right(-1)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4])


class DropRightWhileTest(unittest.TestCase):
    def test_drop_right_while_greater_than_5(self):
        s = Stream.range(10).drop_right_while(lambda x: x > 5)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4, 5])

    def test_drop_right_while_all_elements(self):
        s = Stream(range(10, 20)).drop_right_while(lambda x: x > 0)
        self.assertEqual(s.to_list(), [])

    def test_drop_right_while_none_elements(self):
        s = Stream.range(10).drop_right_while(lambda x: x < 0)
        self.assertEqual(s.to_list(), list(range(10)))

    def test_drop_right_while_complex_condition(self):
        s = Stream(["a", "bb", "ccc", "dddd"]).drop_right_while(lambda x: len(x) > 2)
        self.assertEqual(s.to_list(), ["a", "bb"])


class FillTest(unittest.TestCase):
    def test_fill_entire_stream(self):
        s = Stream([1, 2, 3, 4, 5])
        self.assertEqual(s.fill(0).to_list(), [0, 0, 0, 0, 0])

    def test_fill_partial_stream(self):
        s = Stream([1, 2, 3, 4, 5])
        self.assertEqual(s.fill(0, 1, 4).to_list(), [1, 0, 0, 0, 5])

    def test_fill_start_only(self):
        s = Stream([1, 2, 3, 4, 5])
        self.assertEqual(s.fill(0, 2).to_list(), [1, 2, 0, 0, 0])

    def test_fill_with_end_exceeding_length(self):
        s = Stream([1, 2, 3, 4, 5])
        self.assertEqual(s.fill(0, 3, 10).to_list(), [1, 2, 3, 0, 0])

    def test_fill_with_negative_start(self):
        s = Stream([1, 2, 3, 4, 5])
        self.assertEqual(s.fill(0, -3, 3).to_list(), [0, 0, 0, 4, 5])

    def test_fill_start_greater_than_end(self):
        s = Stream([1, 2, 3, 4, 5])
        self.assertEqual(s.fill(0, 4, 2).to_list(), [1, 2, 3, 4, 5])

    def test_fill_with_string_elements(self):
        s = Stream(["a", "b", "c", "d", "e"])
        self.assertEqual(s.fill("z", 1, 4).to_list(), ["a", "z", "z", "z", "e"])

    def test_fill_with_mixed_elements(self):
        s = Stream([1, "a", 3, "b", 5])
        self.assertEqual(s.fill("x", 1, 4).to_list(), [1, "x", "x", "x", 5])


class ReduceTest(unittest.TestCase):
    def test_reduce_sum(self):
        s = Stream.range(10)
        self.assertEqual(s.reduce(lambda x, y: x + y), 45)

    def test_reduce_product(self):
        s = Stream.range(1, 5)
        self.assertEqual(s.reduce(lambda x, y: x * y), 24)

    def test_reduce_with_initial_value(self):
        s = Stream.range(10)
        self.assertEqual(s.reduce(lambda x, y: x + y, 10), 55)

    def test_reduce_empty_stream_with_initial(self):
        s = Stream([])
        self.assertEqual(s.reduce(lambda x, y: x + y, 0), 0)

    def test_reduce_empty_stream_without_initial(self):
        s = Stream([])
        with self.assertRaises(TypeError):
            s.reduce(lambda x, y: x + y)

    def test_reduce_single_element_without_initial(self):
        s = Stream([5])
        self.assertEqual(s.reduce(lambda x, y: x + y), 5)

    def test_reduce_single_element_with_initial(self):
        s = Stream([5])
        self.assertEqual(s.reduce(lambda x, y: x + y, 10), 15)

    def test_reduce_strings(self):
        s = Stream(["a", "b", "c"])
        self.assertEqual(s.reduce(lambda x, y: x + y), "abc")

    def test_reduce_strings_with_initial(self):
        s = Stream(["a", "b", "c"])
        self.assertEqual(s.reduce(lambda x, y: x + y, "z"), "zabc")

    def test_reduce_custom_objects(self):
        class Person:
            def __init__(self, age):
                self.age = age

        p1 = Person(10)
        p2 = Person(20)
        p3 = Person(30)
        s = Stream([p1, p2, p3])
        self.assertEqual(
            s.reduce(
                lambda x, y: x.age + y.age if isinstance(x, Person) else x + y.age
            ),
            60,
        )

    def test_reduce_custom_objects_with_initial(self):
        class Person:
            def __init__(self, age):
                self.age = age

        p1 = Person(10)
        p2 = Person(20)
        p3 = Person(30)
        s = Stream([p1, p2, p3])
        self.assertEqual(s.reduce(lambda x, y: x + y.age, 5), 65)

    def test_reduce_max(self):
        s = Stream.range(10)
        self.assertEqual(s.reduce(lambda x, y: x if x > y else y), 9)

    def test_reduce_min(self):
        s = Stream.range(10)
        self.assertEqual(s.reduce(lambda x, y: x if x < y else y), 0)

    def test_reduce_to_list(self):
        s = Stream.range(3)
        self.assertEqual(s.reduce(lambda x, y: x + [y], []), [0, 1, 2])

    def test_reduce_to_dict(self):
        s = Stream([("a", 1), ("b", 2), ("c", 3)])
        self.assertEqual(
            s.reduce(lambda x, y: {**x, y[0]: y[1]}, {}), {"a": 1, "b": 2, "c": 3}
        )

    def test_reduce_to_set(self):
        s = Stream.range(5)
        self.assertEqual(s.reduce(lambda x, y: x | {y}, set()), {0, 1, 2, 3, 4})

    def test_reduce_empty_with_initial_set(self):
        s = Stream([])
        self.assertEqual(s.reduce(lambda x, y: x | {y}, set()), set())

    def test_reduce_with_non_commutative_function(self):
        s = Stream([2, 3, 4])
        self.assertEqual(s.reduce(lambda x, y: x - y), -5)

    def test_reduce_floating_point(self):
        s = Stream([1.5, 2.5, 3.0])
        self.assertEqual(s.reduce(lambda x, y: x + y), 7.0)

    def test_reduce_mixed_types(self):
        s = Stream([1, "a", 2, "b"])
        with self.assertRaises(TypeError):
            s.reduce(lambda x, y: x + y)


class FindLastIndexTest(unittest.TestCase):
    def test_find_last_index_exists(self):
        s = Stream.range(10)
        self.assertEqual(s.find_last_index(lambda x: x == 5), 5)

    def test_find_last_index_not_exists(self):
        s = Stream.range(10)
        self.assertEqual(s.find_last_index(lambda x: x == 10), -1)

    def test_find_last_index_first_element(self):
        s = Stream([5, 1, 2, 3, 4, 5])
        self.assertEqual(s.find_last_index(lambda x: x == 5), 5)

    def test_find_last_index_last_element(self):
        s = Stream([1, 2, 3, 4, 5])
        self.assertEqual(s.find_last_index(lambda x: x == 5), 4)

    def test_find_last_index_with_non_integers(self):
        s = Stream(["apple", "banana", "cherry", "banana"])
        self.assertEqual(s.find_last_index(lambda x: x == "banana"), 3)

    def test_find_last_index_empty_stream(self):
        s = Stream([])
        self.assertEqual(s.find_last_index(lambda x: x == 5), -1)

    def test_find_last_index_multiple_matches(self):
        s = Stream([1, 2, 3, 2, 1])
        self.assertEqual(s.find_last_index(lambda x: x == 2), 3)

    def test_find_last_index_with_strings(self):
        s = Stream(["a", "b", "c", "a"])
        self.assertEqual(s.find_last_index(lambda x: x == "a"), 3)

    def test_find_last_index_with_complex_condition(self):
        s = Stream(["apple", "banana", "apricot", "blueberry"])
        self.assertEqual(s.find_last_index(lambda x: "a" in x), 2)

    def test_find_last_index_with_floats(self):
        s = Stream([1.1, 2.2, 3.3, 2.2])
        self.assertEqual(s.find_last_index(lambda x: x == 2.2), 3)

    def test_find_last_index_with_none(self):
        s = Stream([None, 1, None, 2])
        self.assertEqual(s.find_last_index(lambda x: x is None), 2)

    def test_find_last_index_with_custom_objects(self):
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

            def __repr__(self):
                return f"Person(name={self.name}, age={self.age})"

        p1 = Person("Alice", 30)
        p2 = Person("Bob", 30)
        p3 = Person("Alice", 40)
        s = Stream([p1, p2, p3])
        self.assertEqual(s.find_last_index(lambda x: x.name == "Alice"), 2)

    def test_find_last_index_with_lists(self):
        s = Stream([[1, 2], [3, 4], [1, 2]])
        self.assertEqual(s.find_last_index(lambda x: x == [1, 2]), 2)

    def test_find_last_index_with_tuples(self):
        s = Stream([(1, 2), (3, 4), (1, 2)])
        self.assertEqual(s.find_last_index(lambda x: x == (1, 2)), 2)

    def test_find_last_index_with_nested_structures(self):
        s = Stream([{"key": 1}, {"key": 2}, {"key": 1}])
        self.assertEqual(s.find_last_index(lambda x: x["key"] == 1), 2)

    def test_find_last_index_with_mixed_types(self):
        s = Stream([1, "a", 2, "a"])
        self.assertEqual(s.find_last_index(lambda x: x == "a"), 3)

    def test_find_last_index_with_booleans(self):
        s = Stream([True, False, True])
        self.assertEqual(s.find_last_index(lambda x: x is True), 2)

    def test_find_last_index_with_zero(self):
        s = Stream([0, 1, 0, 2])
        self.assertEqual(s.find_last_index(lambda x: x == 0), 2)

    def test_find_last_index_with_large_numbers(self):
        s = Stream([10**6, 10**7, 10**6])
        self.assertEqual(s.find_last_index(lambda x: x == 10**6), 2)


class TakeTest(unittest.TestCase):
    def test_take_first_few_elements(self):
        s = Stream.range(10).take(3)
        self.assertEqual(s.to_list(), [0, 1, 2])

    def test_take_more_than_length(self):
        s = Stream.range(5).take(10)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4])

    def test_take_zero_elements(self):
        s = Stream.range(5).take(0)
        self.assertEqual(s.to_list(), [])


class TakeWhileTest(unittest.TestCase):
    def test_take_while_less_than_5(self):
        s = Stream.range(10).take_while(lambda x: x < 5)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4])

    def test_take_while_all_elements(self):
        s = Stream.range(10).take_while(lambda x: x < 10)
        self.assertEqual(s.to_list(), list(range(10)))

    def test_take_while_none_elements(self):
        s = Stream.range(10).take_while(lambda x: x < 0)
        self.assertEqual(s.to_list(), [])

    def test_take_while_complex_condition(self):
        s = Stream(["a", "bb", "ccc", "dddd"]).take_while(lambda x: len(x) < 3)
        self.assertEqual(s.to_list(), ["a", "bb"])


class TakeRightTest(unittest.TestCase):
    def test_take_right_few_elements(self):
        s = Stream.range(10).take_right(3)
        self.assertEqual(s.to_list(), [7, 8, 9])

    def test_take_right_more_than_length(self):
        s = Stream.range(5).take_right(10)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4])

    def test_take_right_zero_elements(self):
        s = Stream.range(5).take_right(0)
        self.assertEqual(s.to_list(), [])

    def test_take_right_negative(self):
        s = Stream.range(5).take_right(-1)
        self.assertEqual(s.to_list(), [])


class TakeRightWhileTest(unittest.TestCase):
    def test_take_right_while_greater_than_5(self):
        s = Stream.range(10).take_right_while(lambda x: x > 5)
        self.assertEqual(s.to_list(), [6, 7, 8, 9])

    def test_take_right_while_all_elements(self):
        s = Stream(range(10, 20)).take_right_while(lambda x: x > 0)
        self.assertEqual(s.to_list(), list(range(10, 20)))

    def test_take_right_while_none_elements(self):
        s = Stream.range(10).take_right_while(lambda x: x < 0)
        self.assertEqual(s.to_list(), [])

    def test_take_right_while_complex_condition(self):
        s = Stream(["a", "bb", "ccc", "dddd"]).take_right_while(lambda x: len(x) > 2)
        self.assertEqual(s.to_list(), ["ccc", "dddd"])


class GroupByTest(unittest.TestCase):
    def test_group_by_first_letter(self):
        s = Stream(["apple", "banana", "apricot", "blueberry"])
        grouped = s.group_by(lambda x: x[0])
        self.assertEqual(
            grouped, {"a": ["apple", "apricot"], "b": ["banana", "blueberry"]}
        )

    def test_group_by_length(self):
        s = Stream(["a", "bb", "ccc", "dddd"])
        grouped = s.group_by(len)
        self.assertEqual(grouped, {1: ["a"], 2: ["bb"], 3: ["ccc"], 4: ["dddd"]})

    def test_group_by_identity(self):
        s = Stream([1, 2, 2, 3, 3, 3])
        grouped = s.group_by(lambda x: x)
        self.assertEqual(grouped, {1: [1], 2: [2, 2], 3: [3, 3, 3]})

    def test_group_by_modulo(self):
        s = Stream(range(10))
        grouped = s.group_by(lambda x: x % 3)
        self.assertEqual(grouped, {0: [0, 3, 6, 9], 1: [1, 4, 7], 2: [2, 5, 8]})

    def test_group_by_boolean(self):
        s = Stream([True, False, True, True, False])
        grouped = s.group_by(lambda x: x)
        self.assertEqual(grouped, {True: [True, True, True], False: [False, False]})

    def test_group_by_empty_stream(self):
        s = Stream([])
        grouped = s.group_by(lambda x: x)
        self.assertEqual(grouped, {})

    def test_group_by_nested(self):
        s = Stream([[1], [2], [1, 2], [3]])
        grouped = s.group_by(lambda x: len(x))
        self.assertEqual(grouped, {1: [[1], [2], [3]], 2: [[1, 2]]})

    def test_group_by_none(self):
        s = Stream([None, 1, None, 2])
        grouped = s.group_by(lambda x: x is None)
        self.assertEqual(grouped, {True: [None, None], False: [1, 2]})

    def test_group_by_custom_object(self):
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        p1 = Person("Alice", 30)
        p2 = Person("Bob", 30)
        p3 = Person("Alice", 40)
        s = Stream([p1, p2, p3])
        grouped = s.group_by(lambda x: x.name)
        self.assertEqual(grouped, {"Alice": [p1, p3], "Bob": [p2]})

    def test_group_by_dict_key(self):
        s = Stream([{"key": 1}, {"key": 2}, {"key": 1}])
        grouped = s.group_by(lambda x: x["key"])
        self.assertEqual(grouped, {1: [{"key": 1}, {"key": 1}], 2: [{"key": 2}]})


class PartitionByTest(unittest.TestCase):
    def test_partition_by_even_odd(self):
        s = Stream(range(10))
        even, odd = s.partition_by(lambda x: x % 2 == 0)
        self.assertEqual(even.to_list(), [0, 2, 4, 6, 8])
        self.assertEqual(odd.to_list(), [1, 3, 5, 7, 9])

    def test_partition_by_greater_than_5(self):
        s = Stream(range(10))
        greater, lesser = s.partition_by(lambda x: x > 5)
        self.assertEqual(greater.to_list(), [6, 7, 8, 9])
        self.assertEqual(lesser.to_list(), [0, 1, 2, 3, 4, 5])

    def test_partition_by_empty_stream(self):
        s = Stream([])
        true_part, false_part = s.partition_by(lambda x: x)
        self.assertEqual(true_part.to_list(), [])
        self.assertEqual(false_part.to_list(), [])

    def test_partition_by_all_true(self):
        s = Stream(range(5))
        true_part, false_part = s.partition_by(lambda x: True)
        self.assertEqual(true_part.to_list(), [0, 1, 2, 3, 4])
        self.assertEqual(false_part.to_list(), [])

    def test_partition_by_all_false(self):
        s = Stream(range(5))
        true_part, false_part = s.partition_by(lambda x: False)
        self.assertEqual(true_part.to_list(), [])
        self.assertEqual(false_part.to_list(), [0, 1, 2, 3, 4])

    def test_partition_by_none(self):
        s = Stream([None, 1, None, 2])
        true_part, false_part = s.partition_by(lambda x: x is None)
        self.assertEqual(true_part.to_list(), [None, None])
        self.assertEqual(false_part.to_list(), [1, 2])

    def test_partition_by_strings(self):
        s = Stream(["a", "bb", "ccc", "dddd"])
        short, long = s.partition_by(lambda x: len(x) > 2)
        self.assertEqual(short.to_list(), ["ccc", "dddd"])
        self.assertEqual(long.to_list(), ["a", "bb"])

    def test_partition_by_custom_object(self):
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        p1 = Person("Alice", 30)
        p2 = Person("Bob", 30)
        p3 = Person("Alice", 40)
        s = Stream([p1, p2, p3])
        above_30, below_30 = s.partition_by(lambda x: x.age > 30)
        self.assertEqual(above_30.to_list(), [p3])
        self.assertEqual(below_30.to_list(), [p1, p2])

    def test_partition_by_nested(self):
        s = Stream([[1], [2], [1, 2], [3]])
        one_element, more_than_one = s.partition_by(lambda x: len(x) > 1)
        self.assertEqual(one_element.to_list(), [[1, 2]])
        self.assertEqual(more_than_one.to_list(), [[1], [2], [3]])

    def test_partition_by_booleans(self):
        s = Stream([True, False, True, True, False])
        trues, falses = s.partition_by(lambda x: x)
        self.assertEqual(trues.to_list(), [True, True, True])
        self.assertEqual(falses.to_list(), [False, False])


class SkipTest(unittest.TestCase):
    def test_skip_first_few_elements(self):
        s = Stream(range(10)).skip(3)
        self.assertEqual(s.to_list(), [3, 4, 5, 6, 7, 8, 9])

    def test_skip_more_than_length(self):
        s = Stream(range(5)).skip(10)
        self.assertEqual(s.to_list(), [])

    def test_skip_zero_elements(self):
        s = Stream(range(5)).skip(0)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4])

    def test_skip_empty_stream(self):
        s = Stream([]).skip(3)
        self.assertEqual(s.to_list(), [])

    def test_skip_all_elements(self):
        s = Stream(range(5)).skip(5)
        self.assertEqual(s.to_list(), [])

    def test_skip_partial_elements(self):
        s = Stream(range(5)).skip(2)
        self.assertEqual(s.to_list(), [2, 3, 4])

    def test_skip_with_strings(self):
        s = Stream(["a", "b", "c", "d"]).skip(2)
        self.assertEqual(s.to_list(), ["c", "d"])

    def test_skip_with_custom_objects(self):
        class Person:
            def __init__(self, name):
                self.name = name

        p1 = Person("Alice")
        p2 = Person("Bob")
        p3 = Person("Charlie")
        s = Stream([p1, p2, p3]).skip(1)
        self.assertEqual(s.to_list(), [p2, p3])


class SkipWhileTest(unittest.TestCase):
    def test_skip_while_less_than_5(self):
        s = Stream(range(10)).skip_while(lambda x: x < 5)
        self.assertEqual(s.to_list(), [5, 6, 7, 8, 9])

    def test_skip_while_all_elements(self):
        s = Stream(range(10)).skip_while(lambda x: x < 10)
        self.assertEqual(s.to_list(), [])

    def test_skip_while_none_elements(self):
        s = Stream(range(10)).skip_while(lambda x: x < 0)
        self.assertEqual(s.to_list(), list(range(10)))

    def test_skip_while_complex_condition(self):
        s = Stream(["a", "bb", "ccc", "dddd"]).skip_while(lambda x: len(x) < 3)
        self.assertEqual(s.to_list(), ["ccc", "dddd"])

    def test_skip_while_empty_stream(self):
        s = Stream([]).skip_while(lambda x: x < 5)
        self.assertEqual(s.to_list(), [])

    def test_skip_while_all_true(self):
        s = Stream(range(5)).skip_while(lambda x: True)
        self.assertEqual(s.to_list(), [])

    def test_skip_while_all_false(self):
        s = Stream(range(5)).skip_while(lambda x: False)
        self.assertEqual(s.to_list(), [0, 1, 2, 3, 4])

    def test_skip_while_none(self):
        s = Stream([None, 1, None, 2]).skip_while(lambda x: x is None)
        self.assertEqual(s.to_list(), [1, None, 2])

    def test_skip_while_custom_object(self):
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        p1 = Person("Alice", 30)
        p2 = Person("Bob", 30)
        p3 = Person("Charlie", 40)
        s = Stream([p1, p2, p3]).skip_while(lambda x: x.age < 40)
        self.assertEqual(s.to_list(), [p3])


class SortedTest(unittest.TestCase):
    def test_sorted_natural_order(self):
        s = Stream([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])
        self.assertEqual(s.sorted().to_list(), [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9])

    def test_sorted_reverse_order(self):
        s = Stream([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])
        self.assertEqual(
            s.sorted(reverse=True).to_list(), [9, 6, 5, 5, 5, 4, 3, 3, 2, 1, 1]
        )

    def test_sorted_by_length(self):
        s = Stream(["banana", "apple", "pear", "kiwi"])
        self.assertEqual(
            s.sorted(key=len).to_list(), ["pear", "kiwi", "apple", "banana"]
        )

    def test_sorted_custom_objects(self):
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        p1 = Person("Alice", 30)
        p2 = Person("Bob", 25)
        p3 = Person("Charlie", 35)
        s = Stream([p1, p2, p3])
        self.assertEqual(s.sorted(key=lambda x: x.age).to_list(), [p2, p1, p3])

    def test_sorted_with_empty_stream(self):
        s = Stream([]).sorted()
        self.assertEqual(s.to_list(), [])

    def test_sorted_with_single_element(self):
        s = Stream([1]).sorted()
        self.assertEqual(s.to_list(), [1])

    def test_sorted_with_identical_elements(self):
        s = Stream([1, 1, 1]).sorted()
        self.assertEqual(s.to_list(), [1, 1, 1])

    def test_sorted_with_strings(self):
        s = Stream(["apple", "banana", "cherry"]).sorted()
        self.assertEqual(s.to_list(), ["apple", "banana", "cherry"])

    def test_sorted_with_mixed_case_strings(self):
        s = Stream(["apple", "Banana", "cherry"]).sorted()
        self.assertEqual(s.to_list(), ["Banana", "apple", "cherry"])

    def test_sorted_with_reverse_sorted_input(self):
        s = Stream([5, 4, 3, 2, 1]).sorted()
        self.assertEqual(s.to_list(), [1, 2, 3, 4, 5])


class FlatMapTest(unittest.TestCase):
    def test_flat_map_simple_lists(self):
        s = Stream([[1, 2], [3, 4], [5, 6]])
        self.assertEqual(s.flat_map(lambda x: x).to_list(), [1, 2, 3, 4, 5, 6])

    def test_flat_map_with_strings(self):
        s = Stream(["apple", "banana"]).flat_map(lambda x: list(x))
        self.assertEqual(
            s.to_list(), ["a", "p", "p", "l", "e", "b", "a", "n", "a", "n", "a"]
        )

    def test_flat_map_empty_lists(self):
        s = Stream([[], [], []]).flat_map(lambda x: x)
        self.assertEqual(s.to_list(), [])

    def test_flat_map_nested_lists(self):
        s = Stream([[1, [2, 3]], [4], [5, [6]]])
        self.assertEqual(s.flat_map(lambda x: x).to_list(), [1, [2, 3], 4, 5, [6]])

    def test_flat_map_with_none(self):
        s = Stream([None, [1, 2], None, [3, 4]]).flat_map(lambda x: x if x else [])
        self.assertEqual(s.to_list(), [1, 2, 3, 4])

    def test_flat_map_custom_objects(self):
        class Person:
            def __init__(self, name, friends):
                self.name = name
                self.friends = friends

        p1 = Person("Alice", ["Bob", "Charlie"])
        p2 = Person("Dave", ["Eve"])
        s = Stream([p1, p2]).flat_map(lambda x: x.friends)
        self.assertEqual(s.to_list(), ["Bob", "Charlie", "Eve"])

    def test_flat_map_with_tuples(self):
        s = Stream([(1, 2), (3, 4)]).flat_map(lambda x: x)
        self.assertEqual(s.to_list(), [1, 2, 3, 4])

    def test_flat_map_with_dicts(self):
        s = Stream([{"a": 1}, {"b": 2}]).flat_map(lambda x: x.items())
        self.assertEqual(s.to_list(), [("a", 1), ("b", 2)])

    def test_flat_map_empty_stream(self):
        s = Stream([]).flat_map(lambda x: x)
        self.assertEqual(s.to_list(), [])

    def test_flat_map_single_element(self):
        s = Stream([[1, 2]]).flat_map(lambda x: x)
        self.assertEqual(s.to_list(), [1, 2])


class CountTest(unittest.TestCase):
    def test_count_range(self):
        s = Stream(range(10))
        self.assertEqual(s.count(), 10)

    def test_count_empty(self):
        s = Stream([])
        self.assertEqual(s.count(), 0)

    def test_count_single_element(self):
        s = Stream([1])
        self.assertEqual(s.count(), 1)

    def test_count_duplicates(self):
        s = Stream([1, 1, 1])
        self.assertEqual(s.count(), 3)

    def test_count_strings(self):
        s = Stream(["apple", "banana", "cherry"])
        self.assertEqual(s.count(), 3)

    def test_count_mixed(self):
        s = Stream([1, "a", None, True])
        self.assertEqual(s.count(), 4)

    def test_count_custom_objects(self):
        class Person:
            def __init__(self, name):
                self.name = name

        p1 = Person("Alice")
        p2 = Person("Bob")
        s = Stream([p1, p2])
        self.assertEqual(s.count(), 2)

    def test_count_nested_lists(self):
        s = Stream([[1, 2], [3, 4], [5, 6]])
        self.assertEqual(s.count(), 3)

    def test_count_with_none(self):
        s = Stream([None, None, None])
        self.assertEqual(s.count(), 3)

    def test_count_booleans(self):
        s = Stream([True, False, True])
        self.assertEqual(s.count(), 3)


class ToDictTest(unittest.TestCase):
    def test_to_map_simple(self):
        s = Stream(["apple", "banana", "cherry"])
        result = s.to_dict(lambda x: x[0], lambda x: x)
        self.assertEqual(result, {"a": "apple", "b": "banana", "c": "cherry"})

    def test_to_map_custom_objects(self):
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        p1 = Person("Alice", 30)
        p2 = Person("Bob", 25)
        s = Stream([p1, p2])
        result = s.to_dict(lambda x: x.name, lambda x: x.age)
        self.assertEqual(result, {"Alice": 30, "Bob": 25})

    def test_to_map_with_duplicates(self):
        s = Stream(["apple", "apricot", "banana"])
        result = s.to_dict(lambda x: x[0], lambda x: x)
        self.assertEqual(result, {"a": "apricot", "b": "banana"})

    def test_to_map_empty(self):
        s = Stream([])
        result = s.to_dict(lambda x: x, lambda x: x)
        self.assertEqual(result, {})

    def test_to_map_single_element(self):
        s = Stream(["apple"])
        result = s.to_dict(lambda x: x[0], lambda x: x)
        self.assertEqual(result, {"a": "apple"})

    def test_to_map_with_none(self):
        s = Stream([None, "banana", "cherry"])
        result = s.to_dict(lambda x: "n" if x is None else x[0], lambda x: x)
        self.assertEqual(result, {"n": None, "b": "banana", "c": "cherry"})

    def test_to_map_nested_lists(self):
        s = Stream([[1, 2], [3, 4], [5, 6]])
        result = s.to_dict(lambda x: x[0], lambda x: x[1])
        self.assertEqual(result, {1: 2, 3: 4, 5: 6})

    def test_to_map_with_tuples(self):
        s = Stream([("a", 1), ("b", 2)])
        result = s.to_dict(lambda x: x[0], lambda x: x[1])
        self.assertEqual(result, {"a": 1, "b": 2})

    def test_to_map_custom_key_value(self):
        s = Stream(["apple", "banana", "cherry"])
        result = s.to_dict(lambda x: len(x), lambda x: x.upper())
        self.assertEqual(result, {5: "APPLE", 6: "CHERRY"})

    def test_to_map_with_floats(self):
        s = Stream([1.1, 2.2, 3.3])
        result = s.to_dict(lambda x: int(x), lambda x: x)
        self.assertEqual(result, {1: 1.1, 2: 2.2, 3: 3.3})


class ToSetTest(unittest.TestCase):
    def test_to_set_simple(self):
        s = Stream([1, 2, 2, 3, 4, 4, 5])
        self.assertEqual(s.to_set(), {1, 2, 3, 4, 5})

    def test_to_set_with_strings(self):
        s = Stream(["apple", "banana", "apple", "cherry"])
        self.assertEqual(s.to_set(), {"apple", "banana", "cherry"})

    def test_to_set_empty(self):
        s = Stream([])
        self.assertEqual(s.to_set(), set())

    def test_to_set_single_element(self):
        s = Stream([1])
        self.assertEqual(s.to_set(), {1})

    def test_to_set_with_none(self):
        s = Stream([None, 1, None, 2])
        self.assertEqual(s.to_set(), {None, 1, 2})

    def test_to_set_with_tuples(self):
        s = Stream([(1, 2), (3, 4), (1, 2)])
        self.assertEqual(s.to_set(), {(1, 2), (3, 4)})

    def test_to_set_custom_objects(self):
        class Person:
            def __init__(self, name):
                self.name = name

            def __hash__(self):
                return hash(self.name)

            def __eq__(self, other):
                return self.name == other.name

        p1 = Person("Alice")
        p2 = Person("Bob")
        p3 = Person("Alice")
        s = Stream([p1, p2, p3])
        self.assertEqual(s.to_set(), {p1, p2})

    def test_to_set_with_mixed_types(self):
        s = Stream([1, "a", 1, "a"])
        self.assertEqual(s.to_set(), {1, "a"})

    def test_to_set_with_booleans(self):
        s = Stream([True, False, True])
        self.assertEqual(s.to_set(), {True, False})


class DistinctByTest(unittest.TestCase):
    def test_distinct_by_simple(self):
        s = Stream([1, 2, 2, 3, 4, 4, 5])
        self.assertEqual(s.distinct_by(lambda x: x).to_list(), [1, 2, 3, 4, 5])

    def test_distinct_by_first_letter(self):
        s = Stream(["apple", "banana", "apricot", "blueberry"])
        self.assertEqual(s.distinct_by(lambda x: x[0]).to_list(), ["apple", "banana"])

    def test_distinct_by_length(self):
        s = Stream(["a", "bb", "ccc", "dd", "eee", "ffff"])
        self.assertEqual(s.distinct_by(len).to_list(), ["a", "bb", "ccc", "ffff"])

    def test_distinct_by_custom_object(self):
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

            def __repr__(self):
                return f"Person(name={self.name}, age={self.age})"

        p1 = Person("Alice", 30)
        p2 = Person("Bob", 25)
        p3 = Person("Alice", 40)
        s = Stream([p1, p2, p3])
        self.assertEqual(s.distinct_by(lambda x: x.name).to_list(), [p1, p2])

    def test_distinct_by_tuple_first_element(self):
        s = Stream([(1, "a"), (2, "b"), (1, "c"), (3, "d")])
        self.assertEqual(
            s.distinct_by(lambda x: x[0]).to_list(), [(1, "a"), (2, "b"), (3, "d")]
        )

    def test_distinct_by_empty_stream(self):
        s = Stream([])
        self.assertEqual(s.distinct_by(lambda x: x).to_list(), [])

    def test_distinct_by_none(self):
        s = Stream([None, 1, None, 2])
        self.assertEqual(s.distinct_by(lambda x: x).to_list(), [None, 1, 2])

    def test_distinct_by_boolean(self):
        s = Stream([True, False, True, False])
        self.assertEqual(s.distinct_by(lambda x: x).to_list(), [True, False])

    def test_distinct_by_float(self):
        s = Stream([1.1, 2.2, 1.1, 3.3])
        self.assertEqual(s.distinct_by(lambda x: x).to_list(), [1.1, 2.2, 3.3])

    def test_distinct_by_nested_list(self):
        s = Stream([[1, 2], [3, 4], [1, 2], [5, 6]])
        self.assertEqual(s.distinct_by(str).to_list(), [[1, 2], [3, 4], [5, 6]])


class TupleTest(unittest.TestCase):
    def test_to_tuple_simple(self):
        s = Stream([1, 2, 3, 4])
        self.assertEqual(s.to_tuple(), (1, 2, 3, 4))

    def test_to_tuple_empty(self):
        s = Stream([])
        self.assertEqual(s.to_tuple(), ())

    def test_to_tuple_single_element(self):
        s = Stream([1])
        self.assertEqual(s.to_tuple(), (1,))

    def test_to_tuple_with_strings(self):
        s = Stream(["a", "b", "c"])
        self.assertEqual(s.to_tuple(), ("a", "b", "c"))

    def test_to_tuple_mixed_types(self):
        s = Stream([1, "a", None, True])
        self.assertEqual(s.to_tuple(), (1, "a", None, True))

    def test_to_tuple_with_nested_lists(self):
        s = Stream([[1, 2], [3, 4]])
        self.assertEqual(s.to_tuple(), ([1, 2], [3, 4]))

    def test_to_tuple_with_custom_objects(self):
        class Person:
            def __init__(self, name):
                self.name = name

            def __repr__(self):
                return f"Person(name={self.name})"

        p1 = Person("Alice")
        p2 = Person("Bob")
        s = Stream([p1, p2])
        self.assertEqual(s.to_tuple(), (p1, p2))

    def test_to_tuple_after_filter(self):
        s = Stream([1, 2, 3, 4]).filter(lambda x: x > 2)
        self.assertEqual(s.to_tuple(), (3, 4))

    def test_to_tuple_after_map(self):
        s = Stream([1, 2, 3, 4]).map(lambda x: x * 2)
        self.assertEqual(s.to_tuple(), (2, 4, 6, 8))

    def test_to_tuple_after_chunk(self):
        s = Stream([1, 2, 3, 4]).chunk(2)
        self.assertEqual(s.to_tuple(), ([1, 2], [3, 4]))


class FileTest(unittest.TestCase):
    def setUp(self):
        self.mock_file_data = "line1\nline2\nline3\nline4"

    @patch(
        "pathlib.Path.open",
        new_callable=mock_open,
        read_data="line1\nline2\nline3\nline4",
    )
    @patch("pathlib.Path.is_file", return_value=True)
    def test_file_reads_correctly(self, mock_is_file, mock_file):
        s = Stream.file("dummy_path")
        self.assertEqual(s.to_list(), ["line1\n", "line2\n", "line3\n", "line4"])

    @patch(
        "pathlib.Path.open",
        new_callable=mock_open,
        read_data="line1\nline2\nline3\nline4",
    )
    @patch("pathlib.Path.is_file", return_value=True)
    def test_file_with_pathlib_path(self, mock_is_file, mock_file):
        path = pathlib.Path("dummy_path")
        s = Stream.file(path)
        self.assertEqual(s.to_list(), ["line1\n", "line2\n", "line3\n", "line4"])

    @patch("pathlib.Path.is_file", return_value=False)
    def test_file_not_found(self, mock_is_file):
        path = pathlib.Path("non_existent_path")
        with self.assertRaises(FileNotFoundError):
            Stream.file(path)

    @patch("pathlib.Path.open", new_callable=mock_open, read_data="")
    @patch("pathlib.Path.is_file", return_value=True)
    def test_file_empty(self, mock_is_file, mock_file):
        s = Stream.file("dummy_path")
        self.assertEqual(s.to_list(), [])

    @patch("pathlib.Path.open", new_callable=mock_open, read_data="single_line")
    @patch("pathlib.Path.is_file", return_value=True)
    def test_file_single_line(self, mock_is_file, mock_file):
        s = Stream.file("dummy_path")
        self.assertEqual(s.to_list(), ["single_line"])

    @patch(
        "pathlib.Path.open",
        new_callable=mock_open,
        read_data="line1\nline2\nline3\nline4",
    )
    @patch("pathlib.Path.is_file", return_value=True)
    def test_file_with_limit(self, mock_is_file, mock_file):
        s = Stream.file("dummy_path").limit(2)
        self.assertEqual(s.to_list(), ["line1\n", "line2\n"])

    @patch(
        "pathlib.Path.open",
        new_callable=mock_open,
        read_data="line1\nline2\nline3\nline4",
    )
    @patch("pathlib.Path.is_file", return_value=True)
    def test_file_with_filter(self, mock_is_file, mock_file):
        s = Stream.file("dummy_path").filter(lambda line: "2" in line)
        self.assertEqual(s.to_list(), ["line2\n"])

    @patch(
        "pathlib.Path.open",
        new_callable=mock_open,
        read_data="line1\nline2\nline3\nline4",
    )
    @patch("pathlib.Path.is_file", return_value=True)
    def test_file_with_map(self, mock_is_file, mock_file):
        s = Stream.file("dummy_path").map(lambda line: line.strip())
        self.assertEqual(s.to_list(), ["line1", "line2", "line3", "line4"])

    @patch(
        "pathlib.Path.open",
        new_callable=mock_open,
        read_data="line1\nline2\nline3\nline4",
    )
    @patch("pathlib.Path.is_file", return_value=True)
    def test_file_with_concat(self, mock_is_file, mock_file):
        s1 = Stream.file("dummy_path")
        s2 = Stream(["line5", "line6"])
        self.assertEqual(
            s1.chain(s2).to_list(),
            ["line1\n", "line2\n", "line3\n", "line4", "line5", "line6"],
        )

    @patch(
        "pathlib.Path.open",
        new_callable=mock_open,
        read_data="line1\nline2\nline3\nline4",
    )
    @patch("pathlib.Path.is_file", return_value=True)
    def test_file_with_chunk(self, mock_is_file, mock_file):
        s = Stream.file("dummy_path").chunk(2)
        self.assertEqual(s.to_list(), [["line1\n", "line2\n"], ["line3\n", "line4"]])
