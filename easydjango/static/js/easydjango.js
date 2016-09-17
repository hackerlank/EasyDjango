(function($) {
    $.ed = {};
    $.ed.messageId = 1;
    $.ed.systemNotification = function (level, content, title, icon, timeout) {
        var createNotification = function (level, content, title, icon, timeout) {
            var notification = new Notification(title, {body: content, icon: icon});
            if (timeout > 0) {
                if (timeout > 0) { setTimeout(function () { notification.close(); }, timeout); }
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
    }
}(jQuery));