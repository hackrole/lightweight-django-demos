(function($, Backbone, _, app){

    function csrfSafeMethod(method){
        return (/^(GET|HEAD|OPTIONS|TRACE)$/i.test(method));
    }

    function getCookie(name){
        var cookieValue = null;
        if (document.cookie && document.cookie != ''){
            var cookies = document.cookie.split(';');
            for (var i=0; i < cookies.length; i++){
                var cookie = $.trim(cookies[i]);

                if(cookie.substring(0, name.length + 1) == (name + '=')){
                    cookieValue = decodeURLComponent(cookie.substring(name.length+1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $.ajaxPrefilter(function(settings, originalOptions, xhr){
        var csfrtoken;
        if(!csfrSafeMethod(settings.type) && !this.crossDomian){
            csrftoken = getCookie('csrftoken');
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
    });

    var seesion = Backbone.Model.extend({
        defaults: {
            token: null
        },
        initial: function(options){
            this.options = options;
            $.ajaxPrefilter($.proxy(this._setupAuth, this));
            this.load();
        },
        load: function(){
            var token = localStorage.apiToken;
            if(token){
                this.set('token', token);
            }
        },
        save: function(token){
            this.set('token', token);
            if(token === null){
                localStorage.removeItem('apiToken');
            }else{
                localStorage.apiToken = token;
            }
        },
        delete: function(){
            this.save(null);
        },
        authenticated: function(){
            return this.get('token') != null;
        },
        _setupAUth: function(settings, originalOptions, xhr){
            if(this.authenticated()){
                xhr.setRequestHeader(
                    'Authorization',
                    'Token ' + this.get('token')
                );
            }
        }
    });

    app.session = new Session();
})(jQuery, Backbone, _, app);
