(function($) {
    $.ed = {};
    $.edws = {};
    $.ed._wsToken = null;
    $.ed._wsConnection = null;
    $.ed._notificationId = 1;
    $.ed._wsFunctionCallId = 1;
    $.ed._notificationClosers = {};
    $.ed._signalIds = {};
    $.ed._functionCallPromises = {};
    $.ed._registered_signals = {};
    $.ed._closeHTMLNotification = function (id) {
        $("#" + id).fadeOut(400, "swing", function () { $("#" + id).remove()});
        delete $.ed._notificationClosers[id];
    }
    $.ed._systemNotification = function (notificationId, level, content, title, icon, timeout) {
        "use strict";
        var createNotification = function (level, content, title, icon, timeout) {
            var notification = new Notification(title, {body: content, icon: icon});
            $.ed._notificationClosers[notificationId] = function () {
                notification.close();
                delete $.ed._notificationClosers[notificationId];
            };
            if (timeout > 0) {
                if (timeout > 0) { setTimeout(function () { $.ed._notificationClosers[notificationId](); }, timeout); }
            }
        }
        if (!("Notification" in window)) { $.ed.notification("notification", level, content, title, icon, timeout); }
        else if (Notification.permission === "granted") { createNotification(level, content, title, icon, timeout); }
        else if (Notification.permission !== 'denied') {
            Notification.requestPermission(function (permission) {
                if(!('permission' in Notification)) { Notification.permission = permission; }
                if (permission === "granted") { createNotification(level, content, title, icon, timeout); }
                else { $.ed.notification("notification", level, content, title, icon, timeout); }
            });
        }
    };
    $.ed._wsConnect = function (edWsUrl) {
        "use strict";
        var url = edWsUrl;
        $.ed._wsConnection = new WebSocket(edWsUrl);
        $.ed._wsConnection.onopen = function() {
            console.log("websocket connected");
        };
        $.ed._wsConnection.onmessage = function(e) {
            console.log("Received: " + e.data);
            if (e.data == $.ed._heartbeatMessage) {
                $.ed._wsConnection.send(e.data);
            } else {
                var msg = JSON.parse(e.data);
                if (msg.signal && msg.signal_id) {
                    $.ed.call(msg.signal, msg.opts, msg.signal_id);
                }
                else if((msg.result_id) && (msg.exception)) {
                    $.ed._functionCallPromises[msg.result_id][1](msg.exception);
                    delete $.ed._functionCallPromises[msg.result_id];
                }
                else if(msg.result_id) {
                    $.ed._functionCallPromises[msg.result_id][0](msg.result);
                    delete $.ed._functionCallPromises[msg.result_id];
                }
            };
        };
        $.ed._wsConnection.onerror = function(e) {
            console.error(e);
        };
        $.ed._wsConnection.onclose = function(e) {
            console.log("connection closed");
            setTimeout(function () {$.ed._wsConnect(url);}, 5000);
        }
    }
    $.ed._wsSignalConnect = function (signal) {
        "use strict";
        var wrapper = function (opts, id) {
            if (id) {
                return;
            }
            $.ed._wsConnection.send(JSON.stringify({signal: signal, opts: opts}));
        };
        $.ed.connect(signal, wrapper);
    };
    $.ed._wsCallFunction = function (func, opts) {
        "use strict";
        var callId = 'f' + ($.ed._wsFunctionCallId++);
        if (opts === undefined) {
            opts = {};
        }
        $.ed._wsConnection.send(JSON.stringify({func: func, opts: opts, result_id: callId}));
        var promise = new Promise(function(resolve, reject) {
            $.ed._functionCallPromises[callId] = [resolve, reject];
            });
        return promise;
    };

    $.ed.call = function (signal, opts, id) {
        "use strict";
        var i;
        if ($.ed._registered_signals[signal] === undefined) {
            return false;
        }
        else if ((id !== undefined) && ($.ed._signalIds[id] !== undefined)) {
            return false;
        } else if (id !== undefined) {
            $.ed._signalIds[id] = true;
        }
        for (i = 0; i < $.ed._registered_signals[signal].length; i += 1) {
            $.ed._registered_signals[signal][i](opts, id);
        }
        return false;
    };
    $.ed.connect = function (signal, fn) {
        "use strict";
        if ($.ed._registered_signals[signal] === undefined) {
            $.ed._registered_signals[signal] = [];
        }
        $.ed._registered_signals[signal].push(fn);
    };
    /**
     * add the CSRF token to a form as a hidden input. Always returns True so you can use it as onsubmit attribute;
     <form onsubmit="return df.add_csrf_to_form(this);" method="POST" >;
    */
    $.ed.CsrfForm = function (form) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrfmiddlewaretoken';
        input.value = $.ed.csrfTokenValue;
        form.appendChild(input);
        return true;
    };

}(jQuery));