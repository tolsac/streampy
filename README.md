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

> **Benefits**
> - Laziness
> - Small memory footprint even for massive data sets
> - Automatic and configurable parallelization
> - Smart concurrent pool management

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

> stream == ['YOU', 'SHALL', 'PASS']
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
```

**map(self, predicate)**
```
Stream.range(1).map(lambda x: x*x)
```
