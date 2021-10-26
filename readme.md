```python

```

# PipeChain

## Motivation

PipeChain is a utility library for creating functional pipelines.
Let's start with a motivating example.
We have a list of Australian phone numbers from our users.
We need to clean this data before we insert it into the database.
With PipeChain, you can do this whole process in one neat pipeline:



```python
from pipechain import PipeChain, PLACEHOLDER as _

nums = [
    "493225813",
    "0491 570 156",
    "55505488",
    "Barry",
    "02 5550 7491",
    "491570156",
    "",
    "1800 975 707"
]

PipeChain(
    nums
).pipe(
    # Remove spaces
    map, lambda x: x.replace(" ", ""), _
).pipe(
    # Remove non-numeric entries
    filter, lambda x: x.isnumeric(), _
).pipe(
    # Add the mobile code to the start of 8-digit numbers
    map, lambda x: "04" + x if len(x) == 8 else x, _
).pipe(
    # Add the 0 to the start of 9-digit numbers
    map, lambda x: "0" + x if len(x) == 9 else x, _
).pipe(
    # Convert to a set to remove duplicates
    set
).eval()
```




    {'0255507491', '0455505488', '0491570156', '0493225813', '1800975707'}



Without PipeChain, we would have to horrifically nest our code, or else use a lot of temporary variables:


```python
set(
    map(
        lambda x: "0" + x if len(x) == 9 else x,
        map(
            lambda x: "04" + x if len(x) == 8 else x,
            filter(
                lambda x: x.isnumeric(),
                map(
                    lambda x: x.replace(" ", ""),
                    nums
                )
            )
        )
    )
)
```




    {'0255507491', '0455505488', '0491570156', '0493225813', '1800975707'}



## Installation

```bash
pip install pipechain
```

## Usage
### Basic Usage

PipeChain has only two exports: `PipeChain`, and `PLACEHOLDER`.

`PipeChain` is a class that defines a pipeline.
You create an instance of the class, and then call `.pipe()` to add another function onto the pipeline:


```python
from pipechain import PipeChain, PLACEHOLDER
PipeChain(1).pipe(str)
```




    PipeChain(arg=1, pipes=[functools.partial(<class 'str'>)])



Finally, you call `.eval()` to run the pipeline and return the result:


```python
PipeChain(1).pipe(str).eval()
```




    '1'



You can "feed" the pipe at either end, either during construction (`PipeChain("foo")`), or during evaluation `.eval("foo")`:


```python
PipeChain().pipe(str).eval(1)
```




    '1'



Each call to `.pipe()` takes a function, and any additional arguments you provide, both positional and keyword, will be forwarded to the function:


```python
PipeChain(["b", "a", "c"]).pipe(sorted, reverse=True).eval()
```




    ['c', 'b', 'a']



### Argument Position
By default, the previous value is passed as the first positional argument to the function:


```python
PipeChain(2).pipe(pow, 3).eval()
```

The only magic here is that if you use the `PLACEHOLDER` variable as an argument to `.pipe()`, then the pipeline will replace it with the output of the previous pipe at runtime:


```python
PipeChain(2).pipe(pow, 3, PLACEHOLDER).eval()
```

Note that you can rename `PLACEHOLDER` to something more usable using Python's import statement, e.g.


```python
from pipechain import PLACEHOLDER as _
PipeChain(2).pipe(pow, 3, _).eval()

```

### Methods
It might not see like methods will play that well with this pipe convention, but after all, they are just functions:


```python
"".join(["a", "b", "c"])
```




    'abc'




```python
PipeChain(["a", "b", "c"]).pipe(str.join, "", _).eval()
```




    'abc'



### Operators

The same goes for operators, such as `+`, `*`, `[]` etc.
We just have to use the `operator` module in the standard library:


```python
from operator import add, mul, getitem

PipeChain(5).pipe(mul, 3).eval()
```




    15




```python
PipeChain(5).pipe(add, 3).eval()
```




    8




```python
PipeChain(["a", "b", "c"]).pipe(getitem, 1).eval()
```




    'b'


