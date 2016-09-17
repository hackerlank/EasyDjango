(function($) {

    $.ed.notification = function (style, level, content, title, icon, timeout) {
        var messageId = "edMessage" + $.ed.messageId++;
        console.info(messageId);
        if (timeout === undefined) {
            timeout = 0;
        }
        if (style === "banner") {
            var htmlContent = "<div class=\"notify " + level + " banner\" id=\"" + messageId + "\">";
            htmlContent += "<span class=\"notify-closer\" onclick=\"$(this.parentNode).fadeOut();\"></span>";
            if (title) {
                htmlContent += "<span class=\"notify-title\">" + title + "</span>";
            }
            if (content) {
                htmlContent += "<span class=\"notify-text\">" + content + "</span></div>";
            }
            htmlContent += "</div>";
            var messages = $('#messages');
            messages.prepend(htmlContent);
            if (timeout > 0) { setTimeout(function () { $("#" + messageId).fadeOut(); }, timeout); }
        }
        else if (style === "notification") {
            var keepOpen = (timeout === 0);
            $.Notify({caption: title, content: content, icon: icon, type: level, timeout: timeout, keepOpen: keepOpen});
        }
        return messageId;
    };
}(jQuery));