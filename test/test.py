from pipechain import PipeChain, PLACEHOLDER as _
from itertools import chain
import operator


def test_notebook():
    # Ensure the notebook succeds
    from nbconvert.nbconvertapp import main
    main(['--to', 'markdown', '--execute', '--stdout', '../readme.ipynb'])


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
