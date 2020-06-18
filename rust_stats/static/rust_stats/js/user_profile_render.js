var displayFriends = new Vue({
    el: '#user-friends',
    delimiters: ['!{', '}'], // Because Django is using {{ }}
    data: {
      friends: null,
    },
    methods: {
        getFriends: function () {
            // Load user friends and set <friends> with the response
            var _this = this;
            var steamid = window.location.pathname.replace("/rust-stats/user/", "");
            $.getJSON('/rust-stats/user-friends/' + steamid, function (json) {
                _this.friends = json;
            });
        }
    }
})



var displayStats = new Vue({
    el: '#user-stats',
    delimiters: ['!{', '}'],
    data: {
      user: null,
    },
    created: function () {
        // Load user stats and set <user> with the response
        var _this = this;
        var steamid = window.location.pathname.replace("/rust-stats/user/", "");
        $.getJSON('/rust-stats/user-stats/' + steamid, function (json) {
            _this.user = json;
            displayFriends.getFriends();
        });
    }
})