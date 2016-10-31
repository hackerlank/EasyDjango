EasyDjango
==========

Introduction
------------

EasyDjango is an thin overlay of the Django Python web framework for quickly building websites that are ready to deploy.
Its main features are:

  * easy to develop: a single command line generates a fully working base project (with complete templates), that you can modify step-by-step,
    with dedicated development settings,
  * easy to deploy: ready to be packaged, with separated simple config (.ini) files, without requiring to maintain duplicated config files (prod and dev),
  * allowing offline computation (computation in separated processes or dedicated machines) and two-way communication link between the server side and the JavaScript world via websockets.

Of course, everything that is provided by default by EasyDjango can be overriden (like the default templates that are based on the well-known Bootstrap 3 css).


EasyDjango in a nutshell
------------------------

.. code-block:: bash

  pip install easydjango[extra]
  easydjango-createproject
  | Your new project name [MyProject]
  | Python package name [myproject]
  | Initial version [0.1]
  | Root project path [.] test
  cd test
  python setup.py develop
  myproject-django migrate
  myproject-django collectstatic --noinput
  myproject-django runserver
  myproject-django worker


Overview:

:doc:`installation`
    How to install EasyDjango and its dependencies

:doc:`newproject`
    Create a new EasyDjango-based project

:doc:`settings`
    Settings system

:doc:`features`
    Complete feature list

:doc:`api/index`
    The complete API documentation, organized by modules


Full table of contents
======================

.. toctree::
   :maxdepth: 4

   installation
   newproject
   settings
   features
   api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
