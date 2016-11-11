Working with signals
====================

EasyDjango let you to define signals in both server (Python) and client (JavaScript) sides.
Signals are just a name (a string) with some code related to it. When a signal is triggered by its name, each function is called elsewhere (in other processes).
The same signal name can be attached to JavaScript and Python code, and called from JavaScript and Python code.

Python and JavaScript are not symmetrical:

  * there is a single Python code (even if there are multiple processes or threads executing it) that is called “SERVER”,
  * there a multiple JavaScript clients. All of them have a unique identifier and some other properties (any Python object, like "property1" or User("username")).

You can