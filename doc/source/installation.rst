Installing
==========

There are several ways to install EasyDjango.

Installing from pip
-------------------

.. code-block:: bash

  pip install easydjango

Installing from source
----------------------

If you prefer install directly from the source:

.. code-block:: bash

  git clone https://github.com/d9pouces/EasyDjango.git EasyDjango
  cd EasyDjango
  python setup.py install

Dependencies
------------

Of course, EasyDjango is not a standalone library and requires several (pure-Python) packages:

  * django >= 1.8,
  * celery,
  * gunicorn,
  * django-bootstrap3,
  * redis,
  * pip,
  * funcsigs (if Python < 3.3).

Several other dependencies are not mandatory but are really useful:

  * django-pipeline,
  * django-debug-toolbar,
  * django-redis-sessions,
  * psutil.

You can install these optional dependencies:

.. code-block:: bash

  pip install easydjango[extra]


Virtualenvs
-----------

You really should consider using `virtualenvs <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_, allowing
to create several isolated Python environments (each virtualenv having its own set of libraries).