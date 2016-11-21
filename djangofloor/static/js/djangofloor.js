(function($) {
    $.df = {};
    $.dfws = {};
    $.df._wsToken = null;
    $.df._wsConnection = null;
    $.df._notificationId = 1;
    $.df._wsFunctionCallId = 1;
    $.df._notificationClosers = {};
    $.df._signalIds = {};
    $.df._functionCallPromises = {};
    $.df._registered_signals = {};
    $.df._wsBuffer = [];
    $.df._closeHTMLNotification = function (id) {
        $("#" + id).fadeOut(400, "swing", function () { $("#" + id).remove()});
        delete $.df._notificationClosers[id];
    }
    $.df._systemNotification = function (notificationId, level, content, title, icon, timeout) {
        "use strict";
        var createNotification = function (level, content, title, icon, timeout) {
            var notification = new Notification(title, {body: content, icon: icon});
            $.df._notificationClosers[notificationId] = function () {
                notification.close();
                delete $.df._notificationClosers[notificationId];
            };
            if (timeout > 0) {
                if (timeout > 0) { setTimeout(function () { $.df._notificationClosers[notificationId](); }, timeout); }
            }
        }
        if (!("Notification" in window)) { $.df.notification("notification", level, content, title, icon, timeout); }
        else if (Notification.permission === "granted") { createNotification(level, content, title, icon, timeout); }
        else if (Notification.permission !== 'denied') {
            Notification.requestPermission(function (permission) {
                if(!('permission' in Notification)) { Notification.permission = permission; }
                if (permission === "granted") { createNotification(level, content, title, icon, timeout); }
                else { $.df.notification("notification", level, content, title, icon, timeout); }
            });
        }
    };
    $.df._wsConnect = function (dfWsUrl) {
        "use strict";
        var url = dfWsUrl;
        var connection = new WebSocket(dfWsUrl);
        connection.onopen = function() {
            $.df._wsConnection = connection;
            console.log("websocket connected");
            for(var i=0; i < $.df._wsBuffer.length; i++) {
                connection.send($.df._wsBuffer[i]);
            }
            $.df._wsBuffer = [];
        };
        connection.onmessage = function(e) {
            console.log("Received: " + e.data);
            if (e.data == $.df._heartbeatMessage) {
                $.df._wsConnection.send(e.data);
            } else {
                var msg = JSON.parse(e.data);
                if (msg.signal && msg.signal_id) {
                    $.df.call(msg.signal, msg.opts, msg.signal_id);
                }
                else if((msg.result_id) && (msg.exception)) {
                    $.df._functionCallPromises[msg.result_id][1](msg.exception);
                    delete $.df._functionCallPromises[msg.result_id];
                }
                else if(msg.result_id) {
                    $.df._functionCallPromises[msg.result_id][0](msg.result);
                    delete $.df._functionCallPromises[msg.result_id];
                }
            };
        };
        connection.onerror = function(e) {
            console.error(e);
        };
        connection.onclose = function(e) {
            console.log("connection closed");
            $.df._wsConnection = null;
            setTimeout(function () {$.df._wsConnect(url);}, 3000);
        }
    }
    $.df._wsSignalConnect = function (signal) {
        "use strict";
        var wrapper = function (opts, id) {
            if (id) {
                return;
            }
            var msg = JSON.stringify({signal: signal, opts: opts});
            if ($.df._wsConnection) {
                $.df._wsConnection.send(msg);
            } else {
                $.df._wsBuffer.push(msg);
            }
        };
        $.df.connect(signal, wrapper);
    };
    $.df._wsCallFunction = function (func, opts) {
        "use strict";
        var callId = 'f' + ($.df._wsFunctionCallId++);
        if (opts === undefined) {
            opts = {};
        }
        $.df._wsConnection.send(JSON.stringify({func: func, opts: opts, result_id: callId}));
        var promise = new Promise(function(resolve, reject) {
            $.df._functionCallPromises[callId] = [resolve, reject];
            });
        return promise;
    };
    $.df.call = function (signal, opts, id) {
        "use strict";
        var i;
        if ($.df._registered_signals[signal] === undefined) {
            return false;
        }
        else if ((id !== undefined) && ($.df._signalIds[id] !== undefined)) {
            return false;
        } else if (id !== undefined) {
            $.df._signalIds[id] = true;
        }
        for (i = 0; i < $.df._registered_signals[signal].length; i += 1) {
            $.df._registered_signals[signal][i](opts, id);
        }
        return false;
    };
    $.df.connect = function (signal, fn) {
        "use strict";
        if ($.df._registered_signals[signal] === undefined) {
            $.df._registered_signals[signal] = [];
        }
        $.df._registered_signals[signal].push(fn);
    };
    /**
     * add the CSRF token to a form as a hidden input. Always returns True so you can use it as onsubmit attribute;
     <form onsubmit="return df.add_csrf_to_form(this);" method="POST" >;
    */
    $.df.CsrfForm = function (form) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrfmiddlewaretoken';
        input.value = $.df.csrfTokenValue;
        form.appendChild(input);
        return true;
    };

}(jQuery));