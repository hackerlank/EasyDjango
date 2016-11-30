Settings system
===============

By default, Django uses a single Python file for all settings.
However, these settings should be split into three groups:

  * settings that are very common and that can be kept as-is for any project (`USE_TZ = True` or `MEDIA_URL = '/media/'`),
  * settings that are specific to your project but common to all instances of your project (like `INSTALLED_APPS`),
  * settings that are installation-dependent (`DATABASE_PASSWORD`, …)

You usually have to maintain at least two versions of the same file (dev and prod, or one that is versionned and the other one for prod), with the risk of desynchronized files.

On the contrary, DjangoFloor allows to dynamically merge several files to define your settings:

  * `DjangoFloor.conf.defaults` that aims at providing good default values,
  * `yourproject.defaults` for your project-specific settings,
  * `/etc/yourproject/settings.py` for installation-dependent settings.

You can define a list of settings that are read from a text configuration file (a `.ini` file).
DjangoFloor also searches for `local_config.py` and `local_config.ini` setting files in the working directory.


You should define your project-wide settings in `yourproject.defaults` and the list of installation-specific settings in `yourproject.iniconf`.
Development-specific settings (`DEBUG = True`!) can be written into `local_config.py` and added to your source.

The complete list of used config files can be displayed using the following command:

.. code-block:: bash

  yourproject-django config python -v 2 | less
  # --------------------------------------------------------------------------------
  # Djangofloor version 1.0.0
  # Configuration providers:
  #  - Python module "djangofloor.conf.defaults"
  #  - Python module "yourproject.defaults"
  #  - .ini file "/home/user/.virtualenvs/yourproject/etc/yourproject/settings.ini"
  #  - Python file "/home/user/.virtualenvs/yourproject/etc/yourproject/settings.py"
  #  - .ini file "/home/user/.virtualenvs/yourproject/etc/yourproject/django.ini"
  #  - Python file "/home/user/.virtualenvs/yourproject/etc/yourproject/django.py"
  #  - .ini file "./local_config.ini"
  #  - Python file "./local_config.py"
  # --------------------------------------------------------------------------------

You can also display the corresponding .ini files:

.. code-block:: bash

  yourproject-django config ini -v 2 | less
  #  - .ini file "/Users/flanker/.virtualenvs/easydjango35/etc/easydemo/settings.ini"
  #  - .ini file "/Users/flanker/.virtualenvs/easydjango35/etc/easydemo/django.ini"
  #  - .ini file "/Users/flanker/Developer/Github/EasyDjango/EasyDemo/local_config.ini"
  [global]
  admin_email = admin@localhost
  data = django_data
  language_code = fr-fr
  listen_address = localhost:9000
  secret_key = secret_key
  server_url = http://localhost:9000/
  time_zone = Europe/Paris
  log_remote_url =