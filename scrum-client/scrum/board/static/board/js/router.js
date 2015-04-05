(function ($, Backbone, _, app){
    var AppRouter = Backbone.Router.extend({
        routers: {
            '': 'home',
        },
        initialize: function(options){
            this.contentElement = '#content';
            this.current = null;
            Backbone.history.start();
        },
        home: function(){
            var view = new app.views.HomepageView({el: this.contentElement});
            this.render(view);
        },
        router: function(router, name, callback){
            var login;
            callback = callback || this[name];
            callback = _.wrap(callback, function(original){
                var args = _.without(arguments, original);
                if (app.session.authenticated()){
                    original.apply(this, args);
                }e;se{
                    $(this.contentElement).hide();
                    login = new app.views.LoginView();
                    $(this.contentElement).after(login.el);
                    login.on('done', function(){
                        $(this.contentElement).show();
                        original.apply(this, args);
                    }, this);
                    login.render();
                }
            });
            return Backbone.Router.prototype.router.apply(this, [route, name, callback]);
        },
        render: function(view){
            if (this.current){
                this.current.$el = $();
                this.current.remove();
            }
            this.current = view;
            this.current.render();
        }
    });

    app.router = AppRouter;
})(jQuery, Backbone, _, app);
