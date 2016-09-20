(function($) {

    $.ed.notification = function (style, level, content, title, icon, timeout) {
        var notificationId = "edMessage" + $.ed._notificationId++;
        if (timeout === undefined) {
            timeout = 0;
        }
        if (style === "banner") {
            var htmlContent = "<div class=\"notify " + level + " banner\" id=\"" + notificationId + "\">";
            htmlContent += "<span class=\"notify-closer\" onclick=\"$(this.parentNode).fadeOut();\"></span>";
            if (title) { htmlContent += "<span class=\"notify-title\">" + title + "</span>"; }
            if (content) { htmlContent += "<span class=\"notify-text\">" + content + "</span></div>"; }
            htmlContent += "</div>";
            var messages = $('#messages');
            messages.prepend(htmlContent);
            if (timeout > 0) { setTimeout(function () { $.ed._closeHTMLNotification(notificationId); }, timeout); }
        }
        else if (style === "notification") {
            var keepOpen = (timeout === 0);
            $.Notify({caption: title, content: content, icon: icon, type: level, timeout: 0, keepOpen: true});
        }
//        else if (style === "modal") {
//            var htmlContent = "<div data-role=\"dialog\" id=\"" + notificationId + "\">";
//            if (title) { htmlContent += "<h2>" + title + "</h2>"; }
//            if (content) { htmlContent += "<p>" + content + "</p>"; }
//            htmlContent += "</div>";
//            var messages = $('#messages');
//            messages.prepend(htmlContent);
//            $('#' + notificationId).attr('data-role', 'dialog');
//            window.showMetroDialog('#' + notificationId, undefined);
//        }
        else if (style === "system") {
            $.ed._systemNotification(notificationId, level, content, title, icon, timeout);
        }
    };
}(jQuery));