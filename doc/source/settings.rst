Settings system
===============

By default, Django uses a single Python file for all settings.
Settings can be split into three groups:

  * settings that are very common and that can be kept as-is for any project (`USE_TZ = True` or `MEDIA_URL = '/media/'`),
  * settings that are specific to your project but common to all instances of your project (like `INSTALLED_APPS`),
  * settings that are installation-dependent (`DATABASE_PASSWORD`, …)

You usually have to maintain at least two versions of the same file (dev and prod), with the risk of desynchronized files.


On the contrary, DjangoFloor allows to merge several files to define your settings:

  * `DjangoFloor.conf.defaults` that aims at providing good default values,
  * `yourproject.defaults` for your project-specific settings,
  * `/etc/yourproject/settings.py` for installation-dependent settings.

You can define a list of settings that are read from a text configuration file (a `.ini` file).
DjangoFloor also searches for `local_config.py` and `local_config.ini` setting files in the working directory.


You should define your project-wide settings in `yourproject.defaults` and the list of installation-specific settings in `yourproject.iniconf`.
Development-specific settings (`DEBUG = True`!) can be written into `local_config.py` and added to your source.

