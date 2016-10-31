Comprehensive feature list
==========================

Settings system
---------------

EasyDjango allows to merge several files to define your settings:

  * `easydjango.conf.defaults` that aims at providing good default values,
  * `yourproject.defaults` for your project-specific settings,
  * `/etc/yourproject/settings.ini` and `/etc/yourproject/settings.py` for installation-dependent settings,
  * `./local_config.py` and `./local_config.ini` setting files in the working directory.


You should define your project-wide settings in `yourproject.defaults` and the list of installation-specific settings in `yourproject.iniconf`.
Development-specific settings (`DEBUG = True`!) can be written into `local_config.py` and added to your source.

