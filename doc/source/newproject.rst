Creating a new project
======================

Expected archicture
-------------------

By default, DjangoFloor assumes several architectural choices:

  * your application server (aiohttp) is behind a reverse proxy (nginx or apache),
  * offline computation are processed by Celery queues,
  * Redis is used as Celery broker, session store and cache database.

Preparing the environment
-------------------------

* install redis

* create a virtualenv dedicated to your project

.. code-block:: bash

  pip install virtualenv
  cd myproject
  virtualenv venv -p `which python3.5`
  source venv/bin/activate

* install DjangoFloor:

.. code-block:: bash

  pip install djangofloor

* create the base of your project

.. code-block:: bash

  djangofloor-createproject
  | Your new project name [MyProject]
  | Python package name [myproject]
  | Initial version [0.1]
  | Root project path [.] .

* install scripts in your path. Five scripts will be installed:

  * myproject-django: access to all Django admin commands,
  * myproject-celery: run any Celery command,
  * myproject-aiohttp: run a webserver with aiohttp.

.. code-block:: bash

  python setup.py develop

* prepare the database and collect static files

.. code-block:: bash

  myproject-django migrate
  myproject-django collectstatic --noinput

* Now, you just have to run the following two processes (so you need two terminal windows):

.. code-block:: bash

  myproject-django runserver
  myproject-celery worker


Project structure
-----------------

THe structure of this project closely follows the Django classical one.
DjangoFloor only provides default code or values for some parts, so you do not have to write them (but you can override them if you want):

  * instead of writing a complete `myproject.settings` module, you only have to override some values in a `myproject.defaults` module,
  * a valid `ROOT_URLCONF` is provided (with admin views as well as static and media files), you can only add some views in a list in `myproject.url.urlpatterns`,
  * a base template, based on Bootstrap 3,
  * a minimal mapping for some settings in a configuration file,
  * multiple WSGI apps are also provided.

Deploying your project
----------------------

If your project is uploaded to Pypi:


.. code-block:: bash

  pip install myproject --upgrade

Of course, you can deploy it in a virtualenv.
The configuration of your deployment should be in .ini-like files. The list of configuration files, as well as default values, are shown with the following command line:

.. code-block:: bash

  myproject-django config ini -v 2

After the configuration, you can migrate the database and deploy the static files (CSS or JS):

.. code-block:: bash

  myproject-django collectstatic --noinput
  myproject-django migrate

Running the servers (in two different processes):

.. code-block:: bash

  myproject-django runserver  # for dev
  myproject-aiohttp  # for prod
  myproject-celery worker
