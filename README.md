[![Build Status](https://travis-ci.org/tolsac/streampy.svg?branch=master)](https://travis-ci.org/tolsac/streampy) [![PyPI version](https://badge.fury.io/py/streampy.svg)](https://badge.fury.io/py/streampy)
Welcome to streampy documentation!
===================


**streampy** is a Stream Java8 like API written in Python. 

----------

Examples
-------------
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
