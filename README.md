[![Build Status](https://travis-ci.org/tolsac/streampy.svg?branch=master)](https://travis-ci.org/tolsac/streampy) [![PyPI version](https://badge.fury.io/py/streampy.svg)](https://badge.fury.io/py/streampy)

Welcome to streampy documentation!
===================


**streampy** is a Stream Java8 like API written in Python. 

----------

Installation
============

```
pip install streampy
```

Description
===========

**streampy** is meant to be used to manipulate a data flow through a pipeline. The ```Stream``` object takes an iterable at initialization, it supports the python iteration protocol.

Why using streampy?
-------------------

Firstly you have to be aware that streampy is using laziness as far as it can. There are two type of stream operation:

- Operations thats doest **not** consume data. These operators just stacks operations on your stream data. Operations will be processed when a **consumer** operation occurs. Each of theses operators returns a **Stream** object
	- map
	- filter
	- chain
	- exclude
	- peek
	- sort
	- limit
	- chunk
	- substream
	- distinct

- Operators that consume the data. They will consume the **Stream** object returning the desired value.
	- list
	- size
	- foreach
	- reduce
	- min
	- max
	- any
	- all
	- last
	- first


**Benefits**
 - Laziness 
 - Small memory footprint even for massive data sets
 - Automatic and configurable parallelization
 - Smart concurrent pool management

Examples
========

Use it with **iterable** content
```
from streampy import Stream

stream = Stream(['You', 'shall', 'not', 'pass'])
			.map(lambda x: x.upper())
            .exclude(lambda x: x == 'NOT')
            .exclude(lambda x: x == 'PASS')
            .chain(["pass"])
            .map(lambda x: x.upper())
            .list()

>>> stream == ['YOU', 'SHALL', 'PASS']
True
```

It supports **parallelization**, as you want, when you want. 

If **parallel** is not used, the library will use the default **sequential** workflow using only the program main thread.
```
# use it with 2 threads
stream = Stream.range(100)
			.parallel(thread=2)
			.map(lambda x: x**x)

# or let the library decide. Under the cover it uses 
# multiprocessing.cpu_count()
stream = Stream.range(100)
			.parallel(thread=True)
			.map(lambda x: x**x)

# use it with processes
stream = Stream.range(100)
			.parallel(process=True)
			.map(lambda x: x**x)

# use both of it
stream = Stream.range(100)
			.parallel(thread=True)
			.map(lambda x: x**x)
			.parallel(process=True)
			.map(lambda x: x**x)

# or get back to the initial sequential workflow
stream = Stream.range(100)
			.parallel(thread=True)
			.map(lambda x: x**x)
			.sequential()
			.map(lambda x: x**x)

```

Documentation
=============

**Stream(iterable)**
```
Stream(some_iterable)
Stream([1, 2, 3])
Stream((1, 2, 3))
Stream(range(10))

def gen():
    for i in range(3):
        yield i

Stream(gen)
```

**map(self, predicate)**

```
Stream.range(1).map(lambda x: x*x)

def what_the_hell_you_want(item):
	# awesome treatments
	return item
	
Stream.range(10).map(what_the_hell_you_want)
```
**filter(self, predicate)**
```
stream = Stream.range(10).filter(lambda x: x > 8)
# because Stream is an iterable you can loop on it
for item in stream:
    print item
> 9
```
**chain(self, iterable)**
```
stream = Stream([1, 2, 3]).chain([4, 5, 6])
stream.list() == [1, 2, 3, 4, 5, 6]
> True

stream = Stream([1, 2, 3]).chain(Stream([4, 5, 6]))
stream.list() == [1, 2, 3, 4, 5, 6]
> True
```
**exclude(self, predicate)**
```
stream = Stream.range(10).exclude(lambda x: x < 5)
stream.list() == [6, 7, 8, 9]
> True
```

**peek(self, function)**
```
# peek is a bit tricky. It calls a function on your stream but without modifying it. 
stream = Stream.range(2).peek(logger.debug)
> [DEBUG] 0
> [DEBUG] 1
> [DEBUG] 2
stream.list == [0, 1, 2]
> True
```

**chunk(self, chunk_size)**
```
def make_some_api_call(item):
	# request
	return True

stream = Stream(some_huge_list).chunk(100).map(make_some_api_call)
for response in stream:
	# deal with it
```
