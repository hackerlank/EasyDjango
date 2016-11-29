Working with signals
====================

DjangoFloor let you to define signals in both server (Python) and client (JavaScript) sides.
Signals are just a name (a string) with some code related to it. When a signal is triggered by its name, each function is called elsewhere (in another process).
You can attach JavaScript or Python code to your signal name, and you can call this can from the server side as well as from the JS side.

However, Python and JavaScript sides are not symmetrical:

  * there is a single Python side for executing signals (even if there are multiple processes or threads executing it) that is called “SERVER”,
  * there a multiple JavaScript clients. All of them have a unique identifier and some other properties (any Python object, like "property1" or User("username")). Two-way communication are based on websockets.


Defining Python signals
-----------------------

The Python code corresponding to a signal must be a function taking `window_info` as first argument, prefixed by the `djangofloor.decorators.signal` decorator.
Of course, you can attach multiple functions to the same signal. All codes will be run.

.. code-block:: python

    @signal(is_allowed_to=everyone, path='demo.slow_signal', queue='slow')
    def slow_signal(window_info, content=''):

  * `path` is the name of the signal,
  * `queue` is the (optional) name Celery queue. It allows to dispatch computations to specialized queues: one for interactive functions (allowing short response times) and one for slow functions (real background tasks).
    `queue` can be a `callable` for dynamically choose the Celery queue.
    Given `queue(path, window_info, original_kwargs)`, it should return a string (corresponding to the Celery queue).
  * `is_allowed_to`



Using signals from Python
-------------------------

Defining JS signals
-------------------

Using signals from JS
---------------------

