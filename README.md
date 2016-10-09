EasyDjango
==========

  * npm
    npm install yuglify -g

  * extensible config system

  * create favicon
  * images @2x retina
  * language
  * cache (server/client-side): new decorator?
  * responsive
  * minification
  * HTTP2 ?
  * websockets: built-in
  * templates for Bootstrap 3 & Font Awesome
  * REST API: Django REST Framework
  * nginx or apache configuration
  * uwsgi or gunicorn
  * build de .deb
  
  * admin page:
    * last internal checks
    * state of all components
    * Nagios checks
    
  * notification messages for all users
    
  * using reverse proxies
  * logs
  * easy initial conf

python3-redis - Persistent key-value database with network interface (Python 3 library)
python3-aioredis - asyncio (PEP 3156) Redis support
python3-hiredis - redis protocol reader for Python using hiredis

base templates:
    - login button
    - search button
    - create account window
    - logout button
    - messages
    - logo
    - footer
    
New (production-ready) log system
    
WebSocket:
  - on génère un ID de fenêtre avec une liste de topics associés et une expiration
  - chaque topic à une liste d'ID
  - le websocket communique sur la file associée à cet ID
  pb : un message est envoyé à topic1 et topic2, un client est abonné aux deux ; comment dédoubler ? cache de 20 ou 30 derniers messages avec id unique ?
  - à la réception d'un event sur une websocket -> on génère une tâche Celery (toujours la même, qui va traiter le signal (ou les signaux ?))
  - comment générer la request à partir de l'ID de fenêtre ? les infos doivent être en RAM (petit cache) ou en dans Redis
  - une seule fonction pour ajouter des événements aux websockets via du pubsub
  