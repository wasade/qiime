#!/usr/bin/env python

from functools import update_wrapper
from collections import Iterable, defaultdict

# thank you Flask project...
_missing = object()

class Workflow(object):
    """Arbitrary worflow support structure"""
    def __init__(self, ShortCircuit=True, **kwargs):
        """Build thy self

        ShortCiruit : if True, enables ignoring function groups when a given
            item has failed

        kwargs are stored as self.Options. Support for arbitrary Stats is 
        implicit
        """
        self.Options = kwargs
        self.Stats = defaultdict(int)
        self.ShortCircuit = ShortCircuit
        self.Failed = False
        self.FinalState = None

    def _assign_function_groups(self, **kwargs):
        """Determine what function groups will be used

        A function group is simply a function that subsequently calls the
        methods of interested. For instance, you may have a _process_seqs 
        function group, that then calls _check_length, _split_sequence, etc.
        """
        raise NotImplementedError("Must be implemented")

    def __call__(self, it, success_callback=None, failed_callback=None, **kwargs):
        """Operate on all the data

        it : an iterator
        success_callback : method to call on a successful item prior to 
            yielding
        failed_callback : method to call on a failed item prior to yielding
        kwargs : these will get passed to the iterator constructor and to the
            the method that determines the function groups
        """
        if success_callback is None:
            success_callback = lambda x: x.FinalState

        function_groups = self._assign_function_groups(**kwargs)

        # note: can also implement a peek and prune approach where only the
        # methods that execute on the first item (w/o short circuiting) are
        # subsequently left in the workflow. The functions can then be
        # chained as well. this reduces the number of function calls, but
        # likely adds a little more complexity into using this object

        for item in it:
            self.Failed = False
            self.FinalState = None
            
            for f in function_groups:
                f(item)

            if self.Failed and failed_callback is not None:
                yield failed_callback(self)
            else:
                yield success_callback(self)

class requires(object):
    """Decorator that executes a function if requirements are met"""
    def __init__(self, IsValid=True, Option=None, Values=None):
        """
        IsValid : execute the function if self.Failed is False
        Option : a required option
        Values : required values associated with an option
        """
        # self here is the requires object
        self.IsValid = IsValid
        self.Option = Option
        self.Values = Values

        if not isinstance(self.Values, set):
            if isinstance(self.Values, Iterable):
                self.Values = set(self.Values)
            else:
                self.Values = set([self.Values])
    
        if _missing in self.Values:
            raise ValueError("_missing cannot be in Values!")

    def doShortCircuit(self, wrapped):
        if self.IsValid and (wrapped.Failed and wrapped.ShortCircuit):
            return True
        else:
            return False

    def __call__(self, f):
        """Wrap a function

        f : the function to wrap
        """
        # outer_self is the requires object
        # self is expected to be a Workflow object
        def decorated_with_option(dec_self, *args, **kwargs):
            """A decorated function that has an option to validate

            dec_self : this is "self" for the decorated function
            """
            if self.doShortCircuit(dec_self):
                return

            value = dec_self.Options.get(self.Option, _missing)
            if value in self.Values:
                f(dec_self, *args, **kwargs)
        
        def decorated_without_option(dec_self, *args, **kwargs):
            """A decorated function that does not have an option to validate

            dec_self : this is "self" for the decorated function
            """
            if self.doShortCircuit(dec_self):    
                return

            f(dec_self, *args, **kwargs)

        if self.Option is None:
            return update_wrapper(decorated_without_option, f)
        else:
            return update_wrapper(decorated_with_option, f)
