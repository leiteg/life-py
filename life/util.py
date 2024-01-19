# Copyright 2024 Gustavo Leite
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from collections.abc import Iterable, Mapping
from typing import TypeVar

from iterfzf import iterfzf as _iterfzf

# ==============================================================================
# FUNCTIONS
# ==============================================================================

T = TypeVar("T")


def dictfzf(mapping: Mapping[str, T], **kwargs) -> T | None:
    choice = _iterfzf(mapping.keys(), **kwargs)
    if choice is None:
        return None
    assert isinstance(choice, str) and choice in mapping
    return mapping[choice]


def iterfzf(iterable: Iterable[str], **kwargs) -> str:
    choice = _iterfzf(iterable, **kwargs)
    assert isinstance(choice, str)
    return choice


def multifzf(iterable: Iterable[str], **kwargs) -> list[str]:
    choices = _iterfzf(iterable, multi=True, **kwargs)
    assert isinstance(choices, list) and all(isinstance(item, str) for item in choices)
    return choices
