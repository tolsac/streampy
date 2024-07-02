import functools
import itertools
import pathlib
from collections import defaultdict
from typing import (
    Iterable,
    Iterator,
    List,
    Optional,
    Callable,
    Any,
    TypeVar,
    Tuple,
    Dict,
    Set,
    Union,
)

from functions import _chunk, _compact, _chainer

T = TypeVar("T")


class Stream:
    """
    Stream class for functional-style operations on sequences.
    """

    __iterator: Iterator[T]

    def __init__(self, *iterable: Iterable[T]) -> None:
        """
        Initialize the Stream with an iterable.

        Args:
            iterable: An iterable to be processed by the Stream. Only one iterable is allowed.

        Raises:
            TypeError: If more than one iterable is provided or if the provided iterable is None.
        """
        if len(iterable) == 1:
            if iterable[0] is None:
                raise TypeError("Argument is None")
            self.__iterator = iter(iterable[0])
        elif len(iterable) > 1:
            raise TypeError("Takes only one argument")
        else:
            self.__iterator = iter([])

    def __iter__(self) -> Iterator[T]:
        """
        Return the iterator for the Stream.

        Returns:
            Iterator[T]: The iterator of the Stream.
        """
        return iter(self.__iterator)

    def __len__(self) -> int:
        """
        Return the length of the Stream by consuming the iterator.

        Returns:
            int: The number of elements in the Stream.
        """
        return sum(1 for _ in self.__iterator)

    def __getitem__(self, position: int) -> T:
        """
        Return the item at the specified position.

        Args:
            position: The index of the item.

        Raises:
            IndexError: If the index is out of range.

        Returns:
            T: The item at the specified position.
        """
        for idx, item in enumerate(self.__iterator):
            if idx == position:
                return item
        raise IndexError("Stream index out of range")

    def __enter__(self) -> "Stream":
        """
        Enter the runtime context related to the Stream.

        Returns:
            Stream: The Stream itself.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the runtime context related to the Stream.
        """
        pass

    def next(self) -> T:
        """
        Return the next item from the iterator.

        Raises:
            StopIteration: If there are no more items.

        Returns:
            T: The next item from the iterator.
        """
        return next(self.__iterator)

    def size(self) -> int:
        """
        Return the size of the Stream by consuming the iterator.

        Returns:
            int: The number of elements in the Stream.
        """
        return self.__len__()

    def chunk(self, chunk_size: int) -> "Stream":
        """
        Split the Stream into chunks of the specified size.

        Args:
            chunk_size: The size of each chunk.

        Returns:
            Stream: A new Stream of chunks.
        """
        return self.__class__(_chunk(self.__iterator, chunk_size))

    def compact(self) -> "Stream":
        """
        Remove falsy values from the Stream.

        Returns:
            Stream: A new Stream without falsy values.
        """
        return self.__class__(_compact(self.__iterator))

    def chain(self, *iterables: Iterable[T]) -> "Stream":
        """
        Chain multiple iterables together into a single Stream.

        Args:
            iterables: Multiple iterables to be chained.

        Returns:
            Stream: A new Stream with the chained iterables.
        """
        return self.__class__(_chainer(self.__iterator, *iterables))

    def concat(self) -> "Stream":
        """
        Concatenate multiple sub-iterables into a single Stream.

        Returns:
            Stream: A new Stream with the concatenated sub-iterables.
        """
        return self.__class__(_chainer(*self.__iterator))

    def to_list(self) -> List[T]:
        """
        Convert the Stream to a list.

        Returns:
            List[T]: A list of elements in the Stream.
        """
        return list(self.__iterator)

    def to_tuple(self) -> Tuple[T, ...]:
        """
        Convert the Stream to a tuple.

        Returns:
            Tuple[T]: A list of elements in the Stream.
        """
        return tuple(self.__iterator)

    def first(self) -> Optional[T]:
        """
        Return the first item of the Stream, or None if the Stream is empty.

        Returns:
            Optional[T]: The first item or None.
        """
        try:
            return next(self.__iterator)
        except StopIteration:
            return None

    def last(self) -> Optional[T]:
        """
        Return the last item of the Stream, or None if the Stream is empty.

        Returns:
            Optional[T]: The last item or None.
        """
        item = None
        for item in self.__iterator:
            pass
        return item

    def filter(self, predicate: Callable[[T], bool]) -> "Stream":
        """
        Filter items in the Stream based on a predicate function.

        Args:
            predicate: A function to filter items.

        Returns:
            Stream: A new Stream with filtered items.
        """
        return self.__class__(filter(predicate, self.__iterator))

    def peek(self, action: Callable[[T], Any]) -> "Stream":
        """
        Perform an action on each item in the Stream without modifying it.

        Args:
            action: A function to perform on each item.

        Returns:
            Stream: The same Stream after performing the action.
        """

        def gen():
            for item in self.__iterator:
                action(item)
                yield item

        return self.__class__(gen())

    def min(self, key: Optional[Callable[[T], Any]] = None) -> Optional[T]:
        """
        Return the minimum item of the Stream based on a key function.

        Args:
            key: A function to extract a comparison key from each item.

        Returns:
            Optional[T]: The minimum item or None if the Stream is empty.
        """
        try:
            return min(self.__iterator, key=key)
        except ValueError:
            return None

    def max(self, key: Optional[Callable[[T], Any]] = None) -> Optional[T]:
        """
        Return the maximum item of the Stream based on a key function.

        Args:
            key: A function to extract a comparison key from each item.

        Returns:
            Optional[T]: The maximum item or None if the Stream is empty.
        """
        try:
            return max(self.__iterator, key=key)
        except ValueError:
            return None

    def exclude(self, predicate: Callable[[T], bool]) -> "Stream":
        """
        Exclude items in the Stream based on a predicate function.

        Args:
            predicate: A function to exclude items.

        Returns:
            Stream: A new Stream with excluded items.
        """
        return self.__class__((item for item in self.__iterator if not predicate(item)))

    def map(self, function: Callable[[T], Any]) -> "Stream":
        """
        Apply a function to each item in the Stream.

        Args:
            function: A function to apply to each item.

        Returns:
            Stream: A new Stream with the mapped items.
        """
        return self.__class__(map(function, self.__iterator))

    def sort(
        self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False
    ) -> "Stream":
        """
        Sort items in the Stream based on a key function.

        Args:
            key: A function to extract a comparison key from each item.
            reverse: Whether to sort in descending order.

        Returns:
            Stream: A new Stream with sorted items.
        """
        return self.__class__(sorted(self.__iterator, key=key, reverse=reverse))

    def limit(self, count: int) -> "Stream":
        """
        Limit the number of items in the Stream.

        Args:
            count: The maximum number of items.

        Returns:
            Stream: A new Stream with limited items.
        """
        return self.__class__(itertools.islice(self.__iterator, count))

    def any(self, predicate: Callable[[T], bool]) -> bool:
        """
        Check if any item in the Stream matches the predicate function.

        Args:
            predicate: A function to test each item.

        Returns:
            bool: True if any item matches the predicate, False otherwise.
        """
        return any(predicate(item) for item in self.__iterator)

    def all(self, predicate: Callable[[T], bool]) -> bool:
        """
        Check if all items in the Stream match the predicate function.

        Args:
            predicate: A function to test each item.

        Returns:
            bool: True if all items match the predicate, False otherwise.
        """
        return all(predicate(item) for item in self.__iterator)

    def find_index(self, predicate: Callable[[T], bool]) -> int:
        """
        Find the index of the first item in the Stream that matches the predicate function.

        Args:
            predicate: A function to test each item.

        Returns:
            int: The index of the first matching item, or -1 if no match is found.
        """
        for idx, item in enumerate(self.__iterator):
            if predicate(item):
                return idx
        return -1

    def find_last_index(self, predicate: Callable[[T], bool]) -> int:
        """
        Find the index of the last element in the Stream that satisfies the predicate.

        Args:
            predicate: A function to test each element.

        Returns:
            int: The index of the last matching element, or -1 if no match is found.
        """
        last_index = -1
        for idx, item in enumerate(self.__iterator):
            if predicate(item):
                last_index = idx
        return last_index

    def take(self, count: int) -> "Stream":
        """
        Take the first 'count' elements from the Stream.

        Args:
            count: The number of elements to take.

        Returns:
            Stream: A new Stream with the taken elements.
        """
        return self.__class__(itertools.islice(self.__iterator, count))

    def take_while(self, predicate: Callable[[T], bool]) -> "Stream":
        """
        Take elements from the Stream while the predicate is true.

        Args:
            predicate: A function to test each element.

        Returns:
            Stream: A new Stream with the taken elements while the predicate is true.
        """
        return self.__class__(itertools.takewhile(predicate, self.__iterator))

    def take_right(self, count: int) -> "Stream":
        """
        Take the last 'count' elements from the Stream.

        Args:
            count: The number of elements to take from the end.

        Returns:
            Stream: A new Stream with the taken elements from the end.
        """

        def gen():
            cache = []
            for item in self.__iterator:
                cache.append(item)
                if len(cache) > count:
                    cache.pop(0)
            for item in cache:
                yield item

        return self.__class__(gen())

    def take_right_while(self, predicate: Callable[[T], bool]) -> "Stream":
        """
        Take elements from the end of the Stream while the predicate is true.

        Args:
            predicate: A function to test each element.

        Returns:
            Stream: A new Stream with the taken elements from the end while the predicate is true.
        """

        def gen():
            cache = []
            for item in self.__iterator:
                cache.append(item)
            for item in reversed(cache):
                if predicate(item):
                    yield item
                else:
                    break

        return self.__class__(reversed(list(gen())))

    def flatten(self) -> "Stream":
        """
        Flatten a Stream of iterables into a single Stream.

        Returns:
            Stream: A new Stream with flattened items.
        """
        return self.__class__(item for sublist in self.__iterator for item in sublist)

    def flatten_deep(self) -> "Stream":
        """
        Recursively flatten a Stream of nested iterables into a single Stream.

        Returns:
            Stream: A new Stream with all nested iterables flattened.
        """

        def gen(iterator):
            for item in iterator:
                if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                    yield from gen(item)
                else:
                    yield item

        return self.__class__(gen(self.__iterator))

    def join(self, separator: str) -> str:
        """
        Join the items in the Stream into a single string with a separator.

        Args:
            separator: The separator string.

        Returns:
            str: The joined string.
        """
        return separator.join(map(str, self.__iterator))

    def remove(self, predicate: Callable[[T], bool]) -> "Stream":
        """
        Remove items from the Stream that match the predicate function.

        Args:
            predicate: A function to test each item.

        Returns:
            Stream: A new Stream with items removed.
        """
        return self.__class__(item for item in self.__iterator if not predicate(item))

    def distinct(self, predicate: Optional[Callable[[T], Any]] = None) -> "Stream":
        """
        Remove duplicate elements from the Stream, preserving order.
        If a predicate is provided, it is used to determine uniqueness.

        Args:
            predicate: A function to determine the uniqueness of elements.

        Returns:
            Stream: A new Stream with unique elements.
        """
        seen = set()

        def gen():
            for item in self.__iterator:
                key = predicate(item) if predicate else item
                if key not in seen:
                    seen.add(key)
                    yield item

        return self.__class__(gen())

    def distinct_by(self, key_function: Callable[[T], Any]) -> "Stream":
        """
        Remove duplicate elements from the Stream based on a key function, preserving order.

        Args:
            key_function: A function to extract the key for determining uniqueness.

        Returns:
            Stream: A new Stream with unique elements based on the key function.
        """
        seen = set()

        def gen():
            for item in self.__iterator:
                key = key_function(item)
                if key not in seen:
                    seen.add(key)
                    yield item

        return self.__class__(gen())

    def drop(self, count: int) -> "Stream":
        """
        Drop the first 'count' elements from the Stream.

        Args:
            count: The number of elements to drop.

        Returns:
            Stream: A new Stream with the elements dropped.
        """
        return self.__class__(itertools.islice(self.__iterator, count, None))

    def drop_while(self, predicate: Callable[[T], bool]) -> "Stream":
        """
        Drop elements from the Stream while the predicate is true.

        Args:
            predicate: A function to test each element.

        Returns:
            Stream: A new Stream with the elements dropped while the predicate is true.
        """

        def gen():
            iterator = iter(self.__iterator)
            for item in iterator:
                if not predicate(item):
                    yield item
                    break
            for item in iterator:
                yield item

        return self.__class__(gen())

    def drop_right(self, count: int) -> "Stream":
        """
        Drop the last 'count' elements from the Stream.

        Args:
            count: The number of elements to drop from the end.

        Returns:
            Stream: A new Stream with the elements dropped from the end.
        """

        def gen():
            iterator = iter(self.__iterator)
            cache = []
            for item in iterator:
                cache.append(item)
                if len(cache) > count:
                    yield cache.pop(0)

        return self.__class__(gen())

    def drop_right_while(self, predicate: Callable[[T], bool]) -> "Stream":
        """
        Drop elements from the end of the Stream while the predicate is true.

        Args:
            predicate: A function to test each element.

        Returns:
            Stream: A new Stream with the elements dropped from the end while the predicate is true.
        """

        def gen():
            cache = []
            for item in self.__iterator:
                cache.append(item)
            while cache and predicate(cache[-1]):
                cache.pop()
            for item in cache:
                yield item

        return self.__class__(gen())

    def fill(self, value: T, start: int = 0, end: Optional[int] = None) -> "Stream":
        """
        Fills elements of the Stream with value from start up to, but not including, end.

        Args:
            value: The value to fill the Stream with.
            start: The start index to begin filling.
            end: The end index to stop filling (exclusive). If None, fills to the end of the Stream.

        Returns:
            Stream: A new Stream with the elements filled.
        """

        def gen():
            iterator = iter(self.__iterator)
            for idx, item in enumerate(iterator):
                if idx >= start and (end is None or idx < end):
                    yield value
                else:
                    yield item

        return self.__class__(gen())

    def reduce(self, function: Callable[[T, T], T], initial: Optional[T] = None) -> T:
        """
        Reduce the Stream to a single value using a binary function and an optional initial value.

        Args:
            function: A binary function to apply to the elements.
            initial: An optional initial value to start the reduction.

        Returns:
            T: The reduced value.
        """
        if initial is None:
            return functools.reduce(function, self.__iterator)
        else:
            return functools.reduce(function, self.__iterator, initial)

    def group_by(self, key_function: Callable[[T], Any]) -> Dict[Any, List[T]]:
        """
        Group elements of the Stream by a specified key function.

        Args:
            key_function: A function to extract the key for grouping.

        Returns:
            Dict[Any, List[T]]: A dictionary where keys are the results of applying the key function,
                                and values are lists of elements corresponding to those keys.
        """
        grouped = defaultdict(list)
        for item in self.__iterator:
            key = key_function(item)
            grouped[key].append(item)
        return dict(grouped)

    def partition_by(self, predicate: Callable[[T], bool]) -> Tuple["Stream", "Stream"]:
        """
        Partition elements of the Stream into two Streams based on a predicate.

        Args:
            predicate: A function to test each element.

        Returns:
            Tuple[Stream, Stream]: A tuple of two Streams, the first containing elements that match the predicate,
                                   and the second containing elements that do not.
        """
        true_part, false_part = [], []
        for item in self.__iterator:
            (true_part if predicate(item) else false_part).append(item)
        return self.__class__(iter(true_part)), self.__class__(iter(false_part))

    def skip(self, count: int) -> "Stream":
        """
        Skip the first 'count' elements from the Stream.

        Args:
            count: The number of elements to skip.

        Returns:
            Stream: A new Stream with the elements skipped.
        """
        return self.__class__(itertools.islice(self.__iterator, count, None))

    def skip_while(self, predicate: Callable[[T], bool]) -> "Stream":
        """
        Skip elements from the Stream while the predicate is true.

        Args:
            predicate: A function to test each element.

        Returns:
            Stream: A new Stream with the elements skipped while the predicate is true.
        """

        def gen():
            iterator = iter(self.__iterator)
            for item in iterator:
                if not predicate(item):
                    yield item
                    break
            for item in iterator:
                yield item

        return self.__class__(gen())

    def sorted(
        self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False
    ) -> "Stream":
        """
        Sort elements of the Stream based on a key function and order.

        Args:
            key: A function to extract a comparison key from each element.
            reverse: Whether to sort in descending order.

        Returns:
            Stream: A new Stream with sorted elements.
        """
        return self.__class__(sorted(self.__iterator, key=key, reverse=reverse))

    def flat_map(self, function: Callable[[T], Iterable[Any]]) -> "Stream":
        """
        Apply a function to each element and flatten the result.

        Args:
            function: A function to apply to each element.

        Returns:
            Stream: A new Stream with flattened results.
        """

        def gen():
            for item in self.__iterator:
                for result in function(item):
                    yield result

        return self.__class__(gen())

    def count(self) -> int:
        """
        Count the number of elements in the Stream.

        Returns:
            int: The number of elements in the Stream.
        """
        return self.size()

    def to_dict(
        self, key_function: Callable[[T], Any], value_function: Callable[[T], Any]
    ) -> Dict[Any, Any]:
        """
        Convert the Stream to a dictionary.

        Args:
            key_function: A function to extract the key for each element.
            value_function: A function to extract the value for each element.

        Returns:
            Dict[Any, Any]: A dictionary with keys and values generated from the Stream elements.
        """
        return {key_function(item): value_function(item) for item in self.__iterator}

    def to_set(self) -> Set[T]:
        """
        Convert the Stream to a set.

        Returns:
            Set[T]: A set of elements in the Stream.
        """
        return set(self.__iterator)

    @classmethod
    def range(cls, *args: int) -> "Stream":
        """
        Create a Stream from a range of numbers.

        Args:
            args: Arguments to pass to the range function.

        Returns:
            Stream: A new Stream with the range of numbers.
        """
        return cls(range(*args))

    @classmethod
    def file(cls, path: Union[str, pathlib.Path]) -> "Stream":
        """
        Create a Stream from a file, reading it line by line.

        Args:
            path: The path to the file.

        Returns:
            Stream: A new Stream with lines from the file.
        """
        if isinstance(path, str):
            path = pathlib.Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"The path {path} does not exist or is not a file.")
        return cls(path.open())
