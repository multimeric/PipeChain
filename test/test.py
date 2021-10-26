from pipechain import PipeChain, PLACEHOLDER as _
from itertools import chain
import operator


def test_example():
    from pipechain import PipeChain, PLACEHOLDER as _

    nums = [
        "493225813",
        "0491 570 156",
        "55505488",
        "Barry",
        "02 5550 7491",
        "491570156",
        "",
        "1800 975 707",
    ]

    assert PipeChain(nums).pipe(
        # Remove spaces
        map,
        lambda x: x.replace(" ", ""),
        _,
    ).pipe(
        # Remove non-numeric entries
        filter,
        lambda x: x.isnumeric(),
        _,
    ).pipe(
        # Add the mobile code to the start of 8-digit numbers
        map,
        lambda x: "04" + x if len(x) == 8 else x,
        _,
    ).pipe(
        # Add the 0 to the start of 9-digit numbers
        map,
        lambda x: "0" + x if len(x) == 9 else x,
        _,
    ).pipe(
        # Convert to a set to remove duplicates
        set
    ).eval() == {
        "0491570156",
        "0255507491",
        "0493225813",
        "1800975707",
        "0455505488",
    }


def test_pipe_builtins():
    # Test the pipe using only built-in functions
    res = (
        PipeChain(range(5))
        .pipe(
            # Select only even numbers
            filter,
            lambda it: it % 2 == 0,
            _,
        )
        .pipe(
            # Convert to strings
            map,
            str,
            _,
        )
        .pipe(
            # Prepend "X" to each item
            map,
            lambda it: "X" + it,
            _,
        )
        .pipe(
            # Append "Y" to the list
            chain,
            ["Y"],
        )
        .pipe(
            # Convert to list
            list
        )
        .eval()
    )
    assert res == ["X0", "X2", "X4", "Y"]


def test_pipe_numpy():
    import numpy as np

    ret = (
        PipeChain(5)
        .pipe(
            # Make a vector of five 1s
            np.ones
        )
        .pipe(
            # Multiply by two
            operator.mul,
            2,
        )
        .pipe(
            # Transpose for no reason
            np.transpose
        )
        .pipe(np.sum)
        .pipe(int)
        .eval()
    )
    assert ret == 10


def test_with_partial():
    # Test for compatibility with `with_partial`, a library that simplifies
    # the creation of partials
    from with_partial import PartialContext

    with PartialContext() as p:
        ret = (
            PipeChain(range(5))
            .pipe(p.map(lambda x: x ** 2, _))
            .pipe(p.filter(lambda x: x % 4 == 0, _))
            .pipe(list)
            .eval()
        )
        assert ret == [0, 4, 16]


def test_pipetools():
    # Test for compatibility with pipetools magic X function
    from pipetools import X

    ret = (
        PipeChain(range(5))
        .pipe(list)
        .pipe(
            # Duplicate each element
            ~(X * 2)
        )
        .pipe(
            # Check how many 3s there are
            ~X.count(3)
        )
        .eval()
    )
    # There should be 2
    assert ret == 2
