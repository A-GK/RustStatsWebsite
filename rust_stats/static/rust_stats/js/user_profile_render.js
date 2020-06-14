
var displayStats = new Vue({
    el: '#user-stats',
    delimiters: ['!{', '}'], // Because Django is using {{ }}
    data: {
      user: null,
    },
    created: function () {
        // Load user stats and set <user> with the response
        var _this = this;
        var steamid = window.location.pathname.replace("/rust-stats/user/", "");
        $.getJSON('/rust-stats/user-stats/' + steamid, function (json) {
            _this.user = json;
        });
    }
})