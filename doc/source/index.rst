DjangoFloor
===========

Introduction
------------

DjangoFloor is an thin overlay of the Django Python web framework for quickly building websites that are ready to deploy.
Its main features are:

  * easy to develop: a single command line generates a fully working base project (with complete templates), that you can modify step-by-step,
    with dedicated development settings,
  * easy to deploy: ready to be packaged, with separated simple config (.ini) files, without requiring to maintain duplicated config files (prod and dev),
  * allowing offline computation (computation in separated processes or dedicated machines) and two-way communication link between the server side and the JavaScript world via websockets.

Of course, everything that is provided by default by DjangoFloor can be overriden (like the default templates that are based on the well-known Bootstrap 3 css).

Requirements
------------

DjangoFloor assumes that some requirements are available:

  * Python 3.4+,
  * Django 1.8+,
  * Redis for caching, sessions, websocket management and celery broker,
  * a reverse proxy like nginx.

DjangoFloor in a nutshell
-------------------------

.. code-block:: bash

  pip install djangofloor[extra]
  djangofloor-createproject
  | Your new project name [MyProject]
  | Python package name [myproject]
  | Initial version [0.1]
  | Root project path [.] test
  cd test
  python setup.py develop
  myproject-django migrate
  myproject-django collectstatic --noinput
  myproject-django runserver
  # open a new terminal window
  myproject-celery worker


Overview:

:doc:`installation`
    How to install DjangoFloor and its dependencies

:doc:`newproject`
    Create a new DjangoFloor-based project

:doc:`settings`
    Settings configuration and inheritance

:doc:`provided-settings`
    Settings specific to DjangoFloor

:doc:`signals`
    Working with signals

:doc:`monitoring`
    Default monitoring view

:doc:`notification`
    Simple user notification system

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
   provided-settings
   signals
   features
   api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
