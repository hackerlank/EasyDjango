(function(jQ) {
    jQ("#body").on('hidden.bs.modal', function () {
        "use strict";
        var baseModal = $('#edModal');
        baseModal.removeData('bs.modal');
        baseModal.find(".modal-content").html('');
    });

    notification = function (style, level, content, title, icon, timeout) {
        var notificationId = "edMessage" + jQ.ed._notificationId++;
        if (timeout === undefined) { timeout = 0; }
        if (style === undefined) { style = "notification"; }
        if (level === undefined) { level = "info"; }
        if (style === "banner") {
            var messages = $('#edMessages');
            content = '<div id="' + notificationId + '" class="alert alert-' + level + ' fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>' + content + '</div>'
            messages.prepend(content);
            messages.slideDown();
            if (timeout > 0) { setTimeout(function () { $.ed._closeHTMLNotification(notificationId); }, timeout); }
        }
        else if (style === "notification") {
            var keepOpen = (timeout === 0);
            $.notify({message: content, title: title, icon: icon},
                {type: level, delay: timeout});
        }
        else if (style === "modal") {
            var htmlContent = '<div class="modal-header btn-' + level + '" style="border-top-left-radius: inherit; border-top-right-radius: inherit;"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>';
            if (title) {
                htmlContent += '<h4 class="modal-title">' + title + '</h4>';
            }
            htmlContent += '</div>';
            if (content) {
                htmlContent += '<div class="modal-body"><p>' + content + '</p></div>';
            }
            $.ed.call('modal.show', {html: htmlContent});
            if (timeout > 0) {
                setTimeout(function () { $.ed.call('modal.hide'); }, timeout);
            }
       }
        else if (style === "system") {
            $.ed._systemNotification(notificationId, level, content, title, icon, timeout);
        }
    };

    jQ.ed.connect("notify", function (opts, id) {
        notification(opts.style, opts.level, opts.content, opts.title, opts.icon, opts.timeout);
    });

    jQ.ed.connect('modal.show', function (options) {
        "use strict";
        var baseModal = $('#edModal');
        if (baseModal[0] === undefined) {
            $('body').append('<div class="modal fade" id="edModal" tabindex="-1" role="dialog" aria-labelledby="edModal" aria-hidden="true"><div class="modal-dialog"><div class="modal-content "></div></div></div>');
            baseModal = $('#edModal');
        }
        baseModal.find(".modal-content").html(options.html);
        if (options.width) {
            baseModal.find(".modal-dialog").attr("style", "width: " + options.width);
        } else {
            baseModal.find(".modal-dialog").removeAttr("style");
        }
        baseModal.modal('show');
    });

    jQ.ed.connect('modal.hide', function () {
        "use strict";
        var baseModal = $('#edModal');
        baseModal.modal('hide');
        baseModal.removeData('bs.modal');
    });

    jQ.ed.validateForm = function (form, fn) {
        $.edws[fn]({data: $(form).serializeArray()}).then(function(data) {
            var index, formGroup, formInput, key, helpText;
            var errors = data.errors, helpTexts = data.help_texts;
            $(form).find('.form-group').each(function (index, formGroup) {
                formInput = $(formGroup).find(':input').first()[0];
                if (formInput) {
                    key = formInput ? formInput.name : undefined;
                    if (key) {
                        var addedCls = (errors[key] === undefined) ? 'has-success' : 'has-error';
                        var removedCls = (errors[key] === undefined) ? 'has-error' : 'has-success';
                        helpText = "";
                        if (helpTexts[key] !== undefined) {
                            helpText += helpTexts[key];
                        }
                        if (errors[key] !== undefined) {
                            for(value in errors[key]) {
                                helpText += ' ' + errors[key][value].message;
                            }
                        }
                        $(formGroup).addClass(addedCls);
                        $(formGroup).removeClass(removedCls);
                        if($(formGroup).find('.help-block').length === 0) {
                            $(formGroup).append('<span class="help-block"></span>');
                        }
                        $(formGroup).find('.help-block').empty().html(helpText);
                    }
                }
            });
            if(data.valid) {
                $(form).find('input[type=submit]').removeAttr("disabled");
            } else {
                $(form).find('input[type=submit]').attr("disabled", "disabled");
            }
        });
    };
}(jQuery));