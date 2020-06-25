from django.db.models import BooleanField, CharField, DateTimeField, ManyToManyField, Model, PositiveIntegerField


class User(Model):
    """
    user_id - Steam64ID
    user_name - user's steam name
    hours_played - number of hours user has played Rust
    is_banned - is user banned from being displayed in top rankings
    friends - ManyToMany relationship to other User models
    account_created - the time when user's profile was created

    avatar - user's profile picture in the format
    https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/<avatar>
    f7/f750a203f97fc5e3f21a06ce1d1fe574330ffe6f_full.jpg

    last_successful_update - The last time user's profile was successfully
    updated. Used for caching, and determaining when to delete user's profile
    due to inactivity.

    last_attempted_update - The last time there was an attempt to update
    user's profile. Includes failed and successful updates. Always
    updates when mode.save() is called.

    friends_last_updated - The last time user's friend list was updated.
    """

    user_id = CharField(max_length=20, primary_key=True, unique=True)
    user_name = CharField(max_length=32)
    friends = ManyToManyField("self", blank=True)
    avatar = CharField(max_length=100)
    account_created = DateTimeField(null=True, default=None)
    hours_played = PositiveIntegerField(default=0)
    is_banned = BooleanField(default=False)
    last_successful_update = DateTimeField(blank=True, null=True)
    last_attempted_update = DateTimeField(auto_now=True)
    friends_last_updated = DateTimeField(blank=True, null=True)

    # User's stats
    arrows_fired = PositiveIntegerField(default=0)
    arrows_hit_bears = PositiveIntegerField(default=0)
    arrows_hit_boars = PositiveIntegerField(default=0)
    arrows_hit_buildings = PositiveIntegerField(default=0)
    arrows_hit_chickens = PositiveIntegerField(default=0)
    arrows_hit_deer = PositiveIntegerField(default=0)
    arrows_hit_entities = PositiveIntegerField(default=0)
    arrows_hit_horses = PositiveIntegerField(default=0)
    arrows_hit_players = PositiveIntegerField(default=0)
    arrows_hit_wolfs = PositiveIntegerField(default=0)
    arrows_shot = PositiveIntegerField(default=0)

    blocks_upgraded = PositiveIntegerField(default=0)
    placed_blocks = PositiveIntegerField(default=0)

    headshots = PositiveIntegerField(default=0)
    bullets_fired = PositiveIntegerField(default=0)
    bullets_hit_bears = PositiveIntegerField(default=0)
    bullets_hit_boars = PositiveIntegerField(default=0)
    bullets_hit_buildings = PositiveIntegerField(default=0)
    bullets_hit_corpses = PositiveIntegerField(default=0)
    bullets_hit_deer = PositiveIntegerField(default=0)
    bullets_hit_entities = PositiveIntegerField(default=0)
    bullets_hit_horses = PositiveIntegerField(default=0)
    bullets_hit_player_corpses = PositiveIntegerField(default=0)
    bullets_hit_players = PositiveIntegerField(default=0)
    bullets_hit_signs = PositiveIntegerField(default=0)
    bullets_hit_wolfs = PositiveIntegerField(default=0)
    rockets_fired = PositiveIntegerField(default=0)

    cold_exposure_duration = PositiveIntegerField(default=0)
    comfort_exposure_duration = PositiveIntegerField(default=0)
    overheated_exposure_duration = PositiveIntegerField(default=0)
    radiation_exposure_duration = PositiveIntegerField(default=0)

    deaths = PositiveIntegerField(default=0)
    deaths_to_bears = PositiveIntegerField(default=0)
    deaths_to_entities = PositiveIntegerField(default=0)
    deaths_to_fall = PositiveIntegerField(default=0)
    deaths_to_selfinflicted = PositiveIntegerField(default=0)
    deaths_to_wolf = PositiveIntegerField(default=0)

    gathered_cloth = PositiveIntegerField(default=0)
    gathered_leather = PositiveIntegerField(default=0)
    gathered_lowgrade = PositiveIntegerField(default=0)
    gathered_metal_ore = PositiveIntegerField(default=0)
    gathered_scrap = PositiveIntegerField(default=0)
    gathered_stone = PositiveIntegerField(default=0)
    gathered_wood = PositiveIntegerField(default=0)
    
    horse_distance_ridden = PositiveIntegerField(default=0)
    horse_distance_ridden_km = PositiveIntegerField(default=0)

    instruments_full_keyboard_mode = PositiveIntegerField(default=0)
    instruments_notes_played = PositiveIntegerField(default=0)
    instruments_notes_played_binds = PositiveIntegerField(default=0)

    kill_bears = PositiveIntegerField(default=0)
    kill_boars = PositiveIntegerField(default=0)
    kill_chickens = PositiveIntegerField(default=0)
    kill_deer = PositiveIntegerField(default=0)
    kill_horses = PositiveIntegerField(default=0)
    kill_players = PositiveIntegerField(default=0)
    kill_scientists = PositiveIntegerField(default=0)
    kill_wolfs = PositiveIntegerField(default=0)

    melee_strikes = PositiveIntegerField(default=0)
    melee_throws = PositiveIntegerField(default=0)

    shotgun_bullets_hit_building = PositiveIntegerField(default=0)
    shotgun_bullets_hit_entities = PositiveIntegerField(default=0)
    shotgun_bullets_hit_player = PositiveIntegerField(default=0)
    shotgun_bullets_hit_horse = PositiveIntegerField(default=0)
    shotguns_fired = PositiveIntegerField(default=0)

    wounded = PositiveIntegerField(default=0)
    wounded_assisted = PositiveIntegerField(default=0)
    wounded_healed = PositiveIntegerField(default=0)

    picked_up_food_items = PositiveIntegerField(default=0)
    items_dropped = PositiveIntegerField(default=0)
    items_examined = PositiveIntegerField(default=0)

    water_consumed = PositiveIntegerField(default=0)
    calories_consumed = PositiveIntegerField(default=0)

    cargoship_bridge_visits = PositiveIntegerField(default=0)
    oilrig_helipad_landings = PositiveIntegerField(default=0)

    crafting_menu_opened = PositiveIntegerField(default=0)
    inventory_opened = PositiveIntegerField(default=0)
    cupboards_opened = PositiveIntegerField(default=0)
    map_opened = PositiveIntegerField(default=0)
    
    recycled_cans = PositiveIntegerField(default=0)

    destroyed_barrels = PositiveIntegerField(default=0)

    blueprints_learned = PositiveIntegerField(default=0)

    topology_road_duration = PositiveIntegerField(default=0)

    voice_chat_seconds = PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.user_id) + " | " + str(self.user_name)
