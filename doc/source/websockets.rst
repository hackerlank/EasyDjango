Websockets
==========


Installing uwsgi
----------------

First, you must be sure that uwsgi is compiled with the support of SSL (required for websockets, even if HTTPS is not required!).
If the openssl headers are not easily found by the compiler, you can specify their location:

.. code-block:: bash

  CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip install uwsgi -Iv --no-cache-dir