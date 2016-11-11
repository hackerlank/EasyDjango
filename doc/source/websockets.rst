Websockets
==========

By design, websockets require to keep an alive connection between the client (using JavaScript code) and the server.
Currently, you can use either Gunicorn or uwsgi, but both solutions require a thread for each connected client, and at least one thread handling the classical HTTP requests. Due to this limitation, you need to evaluate the average number of pages open at the same time for setting the number of threads.
You must set a reasonnably long timeout value for the application server: when this timeout is reached, the websocket is reset (but automatically reconnected).
Typically, threads used by websockets spend most of their time to wait data from client and consume a few CPU times, requiring long timeout values. On the contrary, threads used by HTTP requests should be computation-heavy but fast.
If you expect a lot of clients, it can be a good idea to start two application servers, listening on different sockets and with different timeout/thread/processes profiles.

Installing uwsgi
----------------

uwsgi is more performant than Gunicorn, but require compilation and is a bit less easy to deploy than Gunicorn.
First, you must be sure that uwsgi is compiled with the support of SSL (required for websockets, even if HTTPS is not required!).
If the openssl headers are not easily found by the compiler, you can specify their location:

.. code-block:: bash

  CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip install uwsgi -Iv --no-cache-dir