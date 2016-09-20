(function($) {
    $.ed = {};
    $.ed._notificationId = 1;
    $.ed._notificationClosers = {}
    $.ed._closeHTMLNotification = function (id) {
        $("#" + id).fadeOut(400, "swing", function () { $("#" + id).remove()});
        delete $.ed._notificationClosers[id];
    }
    $.ed._systemNotification = function (notificationId, level, content, title, icon, timeout) {
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
}(jQuery));