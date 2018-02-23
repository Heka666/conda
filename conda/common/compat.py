# -*- coding: utf-8 -*-
# Try to keep compat small because it's imported by everything
# What is compat, and what isn't?
# If a piece of code is "general" and used in multiple modules, it goes here.
# If it's only used in one module, keep it in that module, preferably near the top.
# This module should contain ONLY stdlib imports.
from __future__ import absolute_import, division, print_function, unicode_literals

from itertools import chain
from operator import methodcaller
import sys

on_win = bool(sys.platform == "win32")

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
FILESYSTEM_ENCODING = sys.getfilesystemencoding()


# #############################
# equivalent commands
# #############################

if PY3:  # pragma: py2 no cover
    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes
    input = input
    range = range

elif PY2:  # pragma: py3 no cover
    from types import ClassType
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, ClassType)
    text_type = unicode
    binary_type = str
    input = raw_input
    range = xrange


# #############################
# equivalent imports
# #############################

if PY3:  # pragma: py2 no cover
    from io import StringIO
    from itertools import zip_longest
    if sys.version_info[1] >= 5:
        from json import JSONDecodeError
        JSONDecodeError = JSONDecodeError
    else:
        JSONDecodeError = ValueError
elif PY2:  # pragma: py3 no cover
    from cStringIO import StringIO
    from itertools import izip as zip, izip_longest as zip_longest
    JSONDecodeError = ValueError

StringIO = StringIO
zip = zip
zip_longest = zip_longest


# #############################
# equivalent functions
# #############################

if PY3:  # pragma: py2 no cover
    def iterkeys(d, **kw):
        return iter(d.keys(**kw))

    def itervalues(d, **kw):
        return iter(d.values(**kw))

    def iteritems(d, **kw):
        return iter(d.items(**kw))

    viewkeys = methodcaller("keys")
    viewvalues = methodcaller("values")
    viewitems = methodcaller("items")

    from collections import Iterable
    def isiterable(obj):
        return not isinstance(obj, string_types) and isinstance(obj, Iterable)

elif PY2:  # pragma: py3 no cover
    def iterkeys(d, **kw):
        return d.iterkeys(**kw)

    def itervalues(d, **kw):
        return d.itervalues(**kw)

    def iteritems(d, **kw):
        return d.iteritems(**kw)

    viewkeys = methodcaller("viewkeys")
    viewvalues = methodcaller("viewvalues")
    viewitems = methodcaller("viewitems")

    def isiterable(obj):
        return (hasattr(obj, '__iter__')
                and not isinstance(obj, string_types)
                and type(obj) is not type)


# #############################
# other
# #############################

from collections import OrderedDict as odict  # NOQA
odict = odict  # lgtm [py/redundant-assignment]

from io import open as io_open  # NOQA


def open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True):
    if 'b' in mode:
        return io_open(ensure_fs_path_encoding(file), str(mode), buffering=buffering,
                       errors=errors, newline=newline, closefd=closefd)
    else:
        return io_open(ensure_fs_path_encoding(file), str(mode), buffering=buffering,
                       encoding=encoding or 'utf-8', errors=errors, newline=newline,
                       closefd=closefd)


def with_metaclass(Type, skip_attrs=set(('__dict__', '__weakref__'))):
    """Class decorator to set metaclass.

    Works with both Python 2 and Python 3 and it does not add
    an extra class in the lookup order like ``six.with_metaclass`` does
    (that is -- it copies the original class instead of using inheritance).

    """

    def _clone_with_metaclass(Class):
        attrs = dict((key, value) for key, value in iteritems(vars(Class))
                     if key not in skip_attrs)
        return Type(Class.__name__, Class.__bases__, attrs)

    return _clone_with_metaclass



NoneType = type(None)
primitive_types = tuple(chain(string_types, integer_types, (float, complex, bool, NoneType)))


def _init_stream_encoding(stream):
    # PY2 compat: Initialize encoding for an IO stream.
    # Python 2 sets the encoding of stdout/stderr to None if not run in a
    # terminal context and thus falls back to ASCII.
    if getattr(stream, "encoding", True):
        # avoid the imports below if they are not necessary
        return stream
    from codecs import getwriter
    from locale import getpreferredencoding
    encoding = getpreferredencoding()
    try:
        encoder = getwriter(encoding)
    except LookupError:
        encoder = getwriter("UTF-8")
    base_stream = getattr(stream, "buffer", stream)
    return encoder(base_stream)


def init_std_stream_encoding():
    sys.stdout = _init_stream_encoding(sys.stdout)
    sys.stderr = _init_stream_encoding(sys.stderr)


def ensure_binary(value):
    try:
        return value.encode('utf-8')
    except AttributeError:  # pragma: no cover
        # AttributeError: '<>' object has no attribute 'encode'
        # In this case assume already binary type and do nothing
        return value


def ensure_text_type(value):
    try:
        return value.decode('utf-8')
    except AttributeError:  # pragma: no cover
        # AttributeError: '<>' object has no attribute 'decode'
        # In this case assume already text_type and do nothing
        return value
    except UnicodeDecodeError:  # pragma: no cover
        try:
            from chardet import detect
        except ImportError:
            try:
                from requests.packages.chardet import detect
            except ImportError:  # pragma: no cover
                from pip._vendor.requests.packages.chardet import detect
        encoding = detect(value).get('encoding') or 'utf-8'
        return value.decode(encoding)
    except UnicodeEncodeError:  # pragma: no cover
        # it's already text_type, so ignore?
        # not sure, surfaced with tests/models/test_match_spec.py test_tarball_match_specs
        # using py27
        return value


def ensure_unicode(value):
    try:
        return value.decode('unicode_escape')
    except AttributeError:  # pragma: no cover
        # AttributeError: '<>' object has no attribute 'decode'
        # In this case assume already unicode and do nothing
        return value


def ensure_fs_path_encoding(value):
    try:
        return value.decode(FILESYSTEM_ENCODING)
    except AttributeError:
        return value
