Creating a new project
======================

Preparing the environment
-------------------------

* install redis

* create a virtualenv dedicated to your project

.. code-block:: bash

  pip install virtualenv
  cd myproject
  virtualenv venv -p `which python3.5`
  source venv/bin/activate

* install easydjango:

.. code-block:: bash

  pip install easydjango

* create the base of your project

.. code-block:: bash

  easydjango-createproject
  | Your new project name [MyProject]
  | Python package name [myproject]
  | Initial version [0.1]
  | Root project path [.] .


* install scripts in your path. Five scripts will be installed:

  * myproject-django: access to all Django admin commands,
  * myproject-celery: run any Celery command,
  * myproject-gunicorn: run Gunicorn (HTTP server that does not allow websockets but in pure-Python),
  * myproject-uwsgi: run the UWSGI HTTP server (required for websockets, but requires compilation)
  * myproject-ctl: direct access to the most common commands.

.. code-block:: bash

  python setup.py develop

* prepare the database and collect static files

.. code-block:: bash

  myproject-ctl migrate
  myproject-ctl collectstatic --noinput

* Now, you just have to run the following two processes (so you need two terminal windows):

.. code-block:: bash

  myproject-ctl server-dev
  myproject-ctl worker


Deploying on Ubuntu or Debian
-----------------------------

  * debtools