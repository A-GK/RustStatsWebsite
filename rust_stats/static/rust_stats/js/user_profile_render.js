function shuffleArray(a) {
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}


function hideElementById(elementId) {
    document.getElementById(elementId).classList.add("hide");
}


var userStats = new Vue({
    el: '#user-stats',
    delimiters: ['!{', '}'],  // Django uses {{ }}
    data: {
        steamid: window.location.pathname.replace("/rust-stats/user/", ""),
        user: null,
        friends: null,
        last_update: null,
        last_attempt: null,
        isSearchActive: false,
        friendsNum: 0,
        // Variables that are seconds and should be formatted differently
        time_variables: ["cold_exposure_duration", "comfort_exposure_duration", "overheated_exposure_duration", "radiation_exposure_duration", "voice_chat_seconds"],
    },

    methods: {
        humanizeNumbers: function (num) {
            if (num > 999999) {  // > 999,999
                return numeral(num).format('0.00a');
            } else if (num > 99999) { // > 99,999
                return numeral(num).format('0.0a');
            } else {
                return numeral(num).format('0,0');
            }
        },

        getFriends: function () {
            // Load user friends and set <friends> with the response
            var _this = this;  // because => function binds this to itself
            $.getJSON('/rust-stats/user-friends/' + _this.steamid, function (json) {
                _this.friends = json;
                _this.friends.friends = shuffleArray(json.friends);
                _this.friendsNum = json.friends.length;
                _this.friends.friends.forEach(function(friend) {
                    if (friend.hours_played == 0) return;
                    friend.hours_played = _this.humanizeNumbers(friend.hours_played);
                });
            });
        },

        addSpecialVariables: function () {
            if (this.user.account_created){
                this.user.account_created = moment(this.user.account_created).format("LL");
            } else {
                this.user.account_created = "Private";
            }
            if (this.user.hours_played == 0){
                this.user.hours_played = "Private"
            }
            this.last_attempt = moment.duration(moment().diff(this.user.last_attempted_update)).humanize({ss:1});
            this.last_update = moment.duration(moment().diff(this.user.last_successful_update)).humanize();

            // Was profile ever public and we have a record of it but now is private
            this.wasPublicIsPrivate = moment.duration(moment().diff(userStats.user.last_successful_update)).asMinutes() > 30;
            this.user.horse_distance_ridden_mi = Math.round(this.user.horse_distance_ridden_km / 1.609);
            this.user.KDR = Math.round(this.user.kill_players / this.user.deaths * 100)/100;

            if (this.user.bullets_fired == 0 || this.user.bullets_hit_players == 0) {
                this.user.bullets_hit_players_percentage = "0%"
                this.user.headshot_percentage = "0%"
            } else {
                this.user.bullets_hit_players_percentage = Math.round(this.user.bullets_hit_players / this.user.bullets_fired * 10000) / 100 + "%"
                this.user.headshot_percentage = Math.round(this.user.headshots / this.user.bullets_hit_players * 10000) / 100 + "%"
            }
        },

        formatVariables: function () {
            // Format variables into a more human friendly manner, adds commas and time units
            var _this = this; // because => function binds 'this' to itself
            Object.keys(_this.user).forEach(function(key) {
                // console.log(key, _this.user[key]);
                if (Number.isInteger(_this.user[key])){ 
                    if (_this.time_variables.includes(key)) {
                            _this.user[key] = moment.duration(_this.user[key], "seconds").humanize({h:99999, s:0});
                            return;
                    }
                    _this.user[key] = _this.humanizeNumbers(_this.user[key]);
                }
            });
        },

        banUser: function (event, ban_status) {
            _this = this;
            $.ajax({
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", document.querySelector('[name=csrfmiddlewaretoken]').value);
                },
                type: "POST",
                url: "/rust-stats/ban-user",
                data: {
                    "user_id": _this.steamid,
                    "ban_status": ban_status,  // Either "ban" or "unban"
                },
                dataType: "json",
                success: function (data) {
                    if (data && data.success && data.response_message) {
                        alert(data.response_message);
                        _this.user.is_banned = !_this.user.is_banned;  // Dynamically changes the ban button to ban/unban
                    } else {
                        alert("Failed to process ban request");
                    }
                }
            });
        },

        deleteUser: function (event) {
            _this = this;
            $.ajax({
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", document.querySelector('[name=csrfmiddlewaretoken]').value);
                },
                type: "POST",
                url: "/rust-stats/delete-user",
                data: {
                    "user_id": _this.steamid,
                },
                dataType: "json",
                success: function (data) {
                    if (data && data.success && data.response_message) {
                        alert(data.response_message);
                    } else {
                        alert("Failed to process deletion request");
                    }
                }
            });
        },

    },

    created: function () {
        // Load user stats and set <user> with the response
        var _this = this;  
        $.getJSON('/rust-stats/user-stats/' + _this.steamid, function (json) {
            _this.user = json; 

            _this.addSpecialVariables();
            _this.formatVariables();
            hideElementById("animation-cover");
            if (json.success){
                // If the profile was never seen before then it won't have user's name in the title
                // so we do it in here
                document.title = json.user_name + "'s Rust Stats | View anyone's Rust stats";
                _this.getFriends();
            } else {
                hideElementById("footer-disclaimers");
            }

        });
    }
})