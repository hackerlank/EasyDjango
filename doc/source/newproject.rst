Creating a new project
======================

Expected archicture
-------------------

By default, EasyDjango assumes several architectural choices:

  * your application server (gunicorn or uwsgi) is behind a reverse proxy (nginx or apache),
  * offline computation are passed to Celery,
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


Project structure
-----------------

THe structure of this project closely follows the Django classical one.
EasyDjango only provides default code or values for some parts, so you do not have to write them (but you can override them if you want):

  * instead of writing a complete `myproject.settings` module, you only have to override some values in a `myproject.defaults` module,
  * a valid `ROOT_URLCONF` is provided (with admin views as well as static and media files), you can only add some views in a list in `myproject.url.urlpatterns`,
  * a base template, based on Bootstrap 3,
  * a minimal mapping for some settings in a configuration file,
  * a WSGI app is also provided.

Deploying your project
----------------------

If your project is uploaded to Pypi:


.. code-block:: bash

  pip install myproject --upgrade

Of course, you can deploy it in a virtualenv.
The configuration of your deployment should be in .ini-like files. The list of configuration files, as well as default values, are shown with the following command line:

.. code-block:: bash

  myproject-ctl config  ini -v 2

After the configuration, you can migrate the database and deploy the static files (CSS or JS):

.. code-block:: bash

  myproject-ctl collectstatic --noinput
  myproject-ctl migrate

Running the servers (in two different processes):

.. code-block:: bash

  myproject-ctl server-dev
  myproject-ctl worker

Sample nginx configuration
--------------------------

location / {
    include uwsgi_params;
    uwsgi_pass 127.0.0.1:3031;
}

uwsgi --socket 127.0.0.1:3031 --wsgi-file foobar.py --master --processes 4 --threads 2 --stats 127.0.0.1:9191

uwsgi --socket 127.0.0.1:3031 --wsgi-file myproject/wsgi.py --master --processes 4 --threads 2 --stats 127.0.0.1:9191


Sample systemd configuration
----------------------------

Common admin tasks
------------------

Django and Celery both provide some commands for admin tasks.

.. code-block:: bash

  myproject-ctl shell
  myproject-ctl dbshell
  myproject-ctl dumpdata
  myproject-ctl loaddata
  myproject-ctl createsuperuser
  myproject-ctl changepassword
  myproject-ctl config
  myproject-ctl check
  myproject-ctl sendtestmail
  myproject-ctl queue-status
  myproject-ctl queue-events
  myproject-ctl purge-queue


Deploying on Ubuntu or Debian
-----------------------------

  * debtools