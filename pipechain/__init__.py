import typing
from dataclasses import dataclass, field
from functools import partial

PLACEHOLDER = object()
NO_INPUT = object()

TPipeChain = typing.TypeVar("TPipeChain", bound="PipeChain")
TPipeInput = typing.TypeVar("TPipeInput")
TPipeOutput = typing.TypeVar("TPipeOutput")

TNewPipeOutput = typing.TypeVar("TNewPipeOutput")


@dataclass
class PipeChain(typing.Generic[TPipeInput, TPipeOutput]):
    """
    A pipeline of functions that will be applied one after the other
    """
    #: Optionally, the argument to use to start the pipeline
    arg: TPipeInput

    # The list of functions compiled so far in the pipeline
    pipes: typing.List[partial]

    def __init__(self, arg: TPipeInput = NO_INPUT, pipes: typing.List[partial]=None):
        self.arg = arg
        self.pipes = pipes or []

    def pipe(self, func: typing.Callable[[TPipeOutput, ...], TNewPipeOutput], *args, **kwargs) -> TPipeChain[
        TPipeInput,
        TNewPipeOutput
    ]:
        """
        Add a new function to the end of the pipeline
        :param func: The function to call
        :param args: Additional positional arguments to the function, other
            than the main pipeline argument
        :param kwargs: Additional keyword arguments to the function, other
            than the main pipeline argument
        :return: A copy of this PipeChain, but with a new function appended to
            the chain
        """
        part = partial(func, *args, **kwargs)
        cls = type(self)
        return cls(arg=self.arg, pipes=self.pipes + [part])

    @staticmethod
    def hydrate_partial(liquid: typing.Any, part: partial) -> partial:
        """
        Converts a partial with missing arguments to a partial with complete
        arguments, that can be called as-is
        :param liquid: The value to provide for missing arguments. If
        PLACEHOLDER was used anywhere, it will be replaced by `liquid`. If not,
        `liquid` will become the new first argument
        :param part: The partial to hydrate
        :return: A hydrated version of `part`
        """
        found_placeholder = False
        args = list(part.args)
        for i, value in enumerate(args):
            if value is PLACEHOLDER:
                found_placeholder = True
                args[i] = liquid
        kwargs = part.keywords.copy()
        for key, value in kwargs.items():
            if value is PLACEHOLDER:
                found_placeholder = True
                kwargs[key] = liquid
        if not found_placeholder:
            # If we didn't find the placeholder, assume it's the first argument
            args = [liquid] + args
        return partial(part.func, *args, **kwargs)

    def eval(self, arg: typing.Optional[TPipeInput] = None) -> TPipeOutput:
        """
        Evaluates the pipe chain.
        :param arg: Optionally, an argument to feed into the pipe. If the pipe
            chain already had an argument, this will be used to replace it
        :return: The return value from the pipeline
        """
        # Ensure we can feed the pipe
        if arg is not None:
            current_arg = arg
        elif self.arg is not None:
            current_arg = self.arg
        else:
            raise Exception("You must provide an argument for the pipeline either during definition or execution")

        # Apply each partial one at a time
        for part in self.pipes:
            hydrated = self.hydrate_partial(current_arg, part)
            current_arg = hydrated()

        return current_arg
