EasyDjango
==========

  * npm
    npm install yuglify -g

  * extensible config system

  * create favicon
  * images @2x retina
  * language
  * cache (server/client-side): new decorator?
  * push notifications https://developer.mozilla.org/fr/docs/Web/API/notification
  * responsive
  * minification
  * HTTP2
  * websockets: django-websocket-redis
  * templates for Bootstrap 3, Metro, Admin, Font Awesome
  * REST API: Django REST Framework
   
  * websockets behavior:
    * send message to users with a given property
    * send message to windows with a given property
    * code for checking requested properties
    
  * nginx or apache configuration
  * uwsgi or gunicorn
  
  * admin page:
    * last internal checks
    * state of all components
    * Nagios checks
    
  * notification messages for all users
    
  * affichage de toutes les vues avec les décorateurs (cache, login_required, …)
  * using reverse proxies
  * logs
  * easy initial conf
  
  * abonnement aux files websocket 
    le code HTML fait une liste de topics et signe le tout + ID de session
    à l'abonnement, on vérifie la signature 

python3-redis - Persistent key-value database with network interface (Python 3 library)
python3-django-websocket-redis - Websockets for Django applications using Redis (Python3 version)
python3-aioredis - asyncio (PEP 3156) Redis support
python3-hiredis - redis protocol reader for Python using hiredis

base templates:
    - login button
    - create account window
    - logout button
    - messages
    - logo
    - footer
    
WebSocket:
  - on génère un ID de fenêtre avec une liste de topics associés et une expiration
  - chaque topic à une liste d'ID
  - le websocket communique sur la file associée à cet ID
  pb : un message est envoyé à topic1 et topic2, un client est abonné aux deux ; comment dédoubler ? cache de 20 ou 30 derniers messages avec id unique ?
  - à la réception d'un event sur une websocket -> on génère une tâche Celery (toujours la même, qui va traiter le signal (ou les signaux ?))
  - comment générer la request à partir de l'ID de fenêtre ? les infos doivent être en RAM (petit cache) ou en dans Redis
  - une seule fonction pour ajouter des événements aux websockets via du pubsub
  