(function($) {
    $.ed = {};
    $.ed._wsToken = null;
    $.ed._wsConnection = null;
    $.ed._notificationId = 1;
    $.ed._notificationClosers = {};
    $.ed._signalIds = {};
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
                $.ed.call(msg.signal, msg.opts, msg.id)
            };
        };
        $.ed._wsConnection.onerror = function(e) {
            console.error(e);
        };
        $.ed._wsConnection.onclose = function(e) {
            console.log("connection closed");
            $.ed._wsConnect(url);
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
    $.ed.call = function (signal, opts, id) {
        "use strict";
        var i;
        console.warn("call: " + signal + opts + "id: " + id);
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
        console.warn("connect: " + signal);
        if ($.ed._registered_signals[signal] === undefined) {
            $.ed._registered_signals[signal] = [];
        }
        $.ed._registered_signals[signal].push(fn);
    };
}(jQuery));