odoo.define('web_auto_reload.web_auto_reload',function (require) {
    var ViewManager = require('web.ViewManager');

    ViewManager.include({
        switch_mode: function(view_type, view_options) {
            var self = this;
            var view = this.views[view_type];
            var old_view = this.active_view;

            if (!view || this.currently_switching) {
                return $.Deferred().reject();
            } else {
                this.currently_switching = true;  // prevent overlapping switches
            }

            // Ensure that the fields_view has been loaded
            var views_def;
            if (!view.fields_view) {
                views_def = this.load_views(view.require_fields);
            }

            return $.when(views_def).then(function () {
                if (view.multi_record) {
                    self.view_stack = [];
                } else if (self.view_stack.length > 0 && !(_.last(self.view_stack).multi_record)) {
                    // Replace the last view by the new one if both are mono_record
                    self.view_stack.pop();
                }
                self.view_stack.push(view);

             // Hide active view (at first rendering, there is no view to hide)
                if (this.active_view && this.active_view !== view) {
                    if (this.active_view.controller) this.active_view.controller.do_hide();
                    if (this.active_view.$container) this.active_view.$container.hide();
                }
                
                self.active_view = view;
                self.set_auto_refresh(view);//change

                if (!view.loaded) {
                    if (!view.controller) {
                        view.controller = self.create_view(view, view_options);
                    }
                    view.$fragment = $('<div>');
                    view.loaded = view.controller.appendTo(view.$fragment).done(function () {
                        // Remove the unnecessary outer div
                        view.$fragment = view.$fragment.contents();
                        self.trigger("controller_inited", view.type, view.controller);
                    });
                }

                // Call do_search on the searchview to compute domains, contexts and groupbys
                if (self.search_view_loaded &&
                        self.flags.auto_search &&
                        view.controller.searchable !== false) {
                    self.active_search = $.Deferred();
                    $.when(self.search_view_loaded, view.loaded).done(function() {
                        self.searchview.do_search();
                    });
                }

//                return $.when(view.created, this.active_search).then(function () {
//                    return self._display_view(view_options, old_view).then(function () {
//                        self.trigger('switch_mode', view_type, no_store, view_options);
//                    });
//                });

                return $.when(view.loaded, self.active_search)
                    .then(function() {
                        return self._display_view(view_options, old_view).then(function() {
                            self.trigger('switch_mode', view_type, view_options);
                        });
                    }).fail(function(e) {
                        if (!(e && e.code === 200 && e.data.exception_type)) {
                            self.do_warn(_t("Error"), view.controller.display_name + _t(" view couldn't be loaded"));
                        }
                        // Restore internal state
                        self.active_view = old_view;
                        self.view_stack.pop();
                    });
            }).always(function () {
                self.currently_switching = false;
            });
        },
        set_auto_refresh: function(view){
            var self = this;
            if(self.action && self.action.auto_refresh){
               setTimeout(function(){
                    $.when(self.search_view_loaded, view.loaded).done(function() {
                        self.searchview.do_search();
                    });
                    self.set_auto_refresh(view)
                }, self.action.auto_refresh);
            }
        },
    });
});
