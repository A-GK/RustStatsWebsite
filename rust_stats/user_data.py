import requests, logging, re
from sys import argv
from cachetools import cached, TTLCache
from django.utils import timezone
from django.db.models import Max
from .models import User
from credentials import steam_api_key
from .user_stats_names import user_stats_names_map, top_categories
from datetime import datetime
from better_profanity import profanity


logger = logging.getLogger("rust_stats")

is_test = 'test' in argv
if is_test:
    from .mock_test_data import *

############################# BEGIN USER STATS ############################# 
def get_raw_user_stats(steamid):
    """
    Get raw user stats from Steam API.
    Calls Steam API and returns data in format of [{'name': 'stats_name', 'value': 0000},{},{},...]
    Returns None if profile is private or an error is encountered.
    """
    logger.debug(f"Attempting to get raw user stats. steamid {steamid}")
    if not is_test:
        try:
            user_stats = requests.get("http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002?", 
            params={"key": steam_api_key, "appid": "252490", "steamid": str(steamid)})
            logger.debug(f"Successfully got raw user stats. steamid {steamid}")
        except Exception:
            logger.debug(f"Encountered a caught exception while trying to get raw user stats. steamid {steamid}", exc_info=True)
            return None

        if user_stats.status_code == 500:  # Profile is private
            logger.debug(f"Encountered a caught exception while trying to get raw user stats. The profile is private. steamid {steamid}", exc_info=True)
            return None
            
        if user_stats.status_code == 400:  # User does not own rust
            logger.debug(f"Encountered a caught exception while trying to get raw user stats. The user does not own rust. steamid {steamid}", exc_info=True)
            return None
        elif user_stats.status_code != 200:  # Something went wrong
            logger.warning(f"Encountered a caught exception while trying to get raw user stats. Response is not 200. steamid {steamid}", exc_info=True)
            return None
        user_stats = user_stats.json()
    else:
        user_stats = steam_raw_game_stats_request
    try:
        user_stats = user_stats["playerstats"]["stats"]
        logger.debug(f"Finished get_raw_user_stats() successfully.")
        return user_stats
    except Exception:
        logger.warning(f"Encountered a caught exception while tryting to remove useless information from user_stats \
        (unknown format of the returned api response?). steamid {steamid}", exc_info=True)
        return None


def parse_raw_user_stats(raw_user_stats):
    """
    Convert Steam's response of user stats into a usable format.
    From [{'name': 'stats_name', 'value': 0000},{},{},...]
    to   {'stats_name': 0000, '': 0000,...}
    """
    user_stats = {}
    for statistics in raw_user_stats:
        try:
            # int() is used to round some floats for easier database storage
            user_stats[statistics["name"].lower()] = int(statistics["value"])  
        except Exception:
            logger.warning(f"Encountered a caught exception while trying parse raw user stats.", exc_info=True)
    return user_stats


def remove_user_stats_duplicates(user_stats):
    """
    There are stats like harvest.cloth and harvested_cloth which are presumably
    the same thing but are separated. Add them together and return the new
    user_stats with duplicates summed up to '_' stats.
    """
    user_stats["harvested_cloth"] = user_stats.get("harvested_cloth", 0) + user_stats.get("harvest.cloth", 0)
    user_stats["harvested_stones"] = user_stats.get("harvested_stones", 0) + user_stats.get("harvest.stones", 0)
    user_stats["harvested_wood"] = user_stats.get("harvested_wood", 0) + user_stats.get("harvest.wood", 0)
    user_stats["death_selfinflicted"] = user_stats.get("death_selfinflicted", 0) + user_stats.get("death_suicide", 0)
    user_stats.pop('harvest.cloth', None)
    user_stats.pop('harvest.stones', None)
    user_stats.pop('harvest.wood', None)
    user_stats.pop('death_suicide', None)
    return user_stats


def convert_stats_names(user_stats):
    """
    Convert's steam's stats names to more user-friendly names.
    """
    new_user_stats = {}
    for key, value in user_stats.items():
        new_name = user_stats_names_map.get(key, None)
        if new_name is None:
            logger.info(f"Encountered a new statistics value named {key}")
            continue
        new_user_stats[new_name] = value
    return new_user_stats


def get_user_stats(steamid):
    """
    Get the user's stats from Steam
    """
    raw_data = get_raw_user_stats(steamid)
    if raw_data is None:
        return None
    user_data = parse_raw_user_stats(raw_data)
    user_data = remove_user_stats_duplicates(user_data)
    user_data = convert_stats_names(user_data)
    return user_data
############################# END USER STATS #############################


def get_user_name_and_avatar(steamid):
    if not is_test:
        try:
            user_info = requests.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/", 
            params={"key": steam_api_key, "steamids": str(steamid)})
        except Exception:
            logger.warning(f"Encountered a caught exception while trying to get user's profile summary. steamid {steamid}", exc_info=True)
            return None
        if user_info.status_code != 200:
            logger.warning(f"Encountered a caught exception while trying to get user's profile summary. Response is not 200. steamid {steamid}", exc_info=True)
            return None
        user_info = user_info.json()
    else:
        user_info = steam_user_name_and_avatar_raw_response
    try:
        user_info = user_info["response"]["players"]

        if user_info == []:  # Check if user exists
            return None
        user_info = user_info[0]

        user_name = profanity.censor(user_info["personaname"])[:32]
        user_name = re.sub(r"(http(s)?:\/\/.)?(www\.)?([-a-zA-Z0-9@:%._\+~#=]{2,256})\.(com|net|io)\b([-a-zA-Z0-9@:%_\+.~#? &//=]*)", "****", user_name)

        user_data = {
        "user_name": user_name, 
        "avatar": user_info["avatarfull"].replace("https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/", ""),
        }
        account_created = user_info.get("timecreated", None)
        if account_created:
            user_data["account_created"] = timezone.make_aware(datetime.fromtimestamp(account_created), timezone.get_current_timezone())
        return user_data
    except Exception:
        logger.warning(f"Encountered a caught exception while tryting to exctract avatar & user_name \
        (unknown format of the returned api response?). steamid {steamid}", exc_info=True)
        return None


def get_user_hours_played(steamid):
    """
    Returns user's hours played as an int.
    Returns None if profile is private or user doesn't have Rust.
    """
    if not is_test:
        try:
            games_played = requests.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/", 
            params={"key": steam_api_key, "steamid": str(steamid)})
        except Exception:
            logger.warning(f"Encountered a caught exception while trying to get user's hours played. steamid {steamid}", exc_info=True)
            return None
        if games_played.status_code != 200:
            logger.debug(f"Encountered a caught exception while trying to get user's profile summary. Response is not 200. steamid {steamid}", exc_info=True)
            return None
        games_played = games_played.json()
    else:
        games_played = steam_get_user_hours_raw_response
    try:
        games_played = games_played["response"]
        if games_played is None:  # Profile is private
            return None
        try:
            for game in games_played["games"]:
                if game["appid"] == 252490:
                    hours_played = int(game["playtime_forever"] / 60)
                    return hours_played
            return None
        except Exception:
            return None
        
    except Exception:
        logger.warning(f"Encountered a caught exception while tryting to exctract hours played \
        (unknown format of the returned api response?). steamid {steamid}", exc_info=True)
        return None


def create_user_data(steamid):
    """
    Creates user model based on the Steam API data.
    """
    logger.debug(f"Attempting to create user_data. steamid {steamid}")
    steamid = str(steamid)
    user_data = {}
    user_data["user_id"] = steamid

    user_name_and_avatar = get_user_name_and_avatar(steamid)
    if user_name_and_avatar is None:  # User does not exist
        logger.debug(f"While creating user_data, user_name_and_avatar returned None. steamid {steamid}")
        return None
    user_data.update(user_name_and_avatar)
    logger.debug(f"While creating user_data, successfully received user_name_and_avatar. steamid {steamid}")

    user_hours_played = get_user_hours_played(steamid)
    if user_hours_played is None:  # User's profile is set to private, etc.
        logger.debug(f"While creating user_data, user_hours_played returned None. steamid {steamid}")
        user_data["hours_played"] = 0
    else:
        user_data["hours_played"] = user_hours_played
    logger.debug(f"While creating user_data, successfully received user_hours_played. steamid {steamid}")

    user_stats = get_user_stats(steamid)
    if user_stats is None:  # User's profile is set to private, etc.
        logger.debug(f"While creating user_data, user_stats returned None. steamid {steamid}")
        user = User(**user_data)
        user.save()
        return True

    logger.debug(f"While creating user_data, successfully received user_stats. steamid {steamid}")
    user_data.update(user_stats)
    user_data["last_successful_update"] = timezone.now()
    user = User(**user_data)
    user.save()
    return True
    logger.debug(f"While creating user_data, successfully created user and added said user to the database. steamid {steamid}")


def update_user_model(user, new_data):
    """
    Updates user with **new_data dictionary.
    Key is the name of model attribute and value is that model attribute's value.
    {"model_attribute": new_value}
    """
    for attribute_name in new_data:
        setattr(user, attribute_name, new_data[attribute_name])
    user.save()


def update_user_data(user):
    """
    Update's user model with new data from Steam's API.
    """
    logger.debug(f"Started updating user_data. user_id {user.user_id}")
    steamid = user.user_id
    user_data = {}

    user_name_and_avatar = get_user_name_and_avatar(steamid)
    if user_name_and_avatar is None:  # User does not exist
        logger.debug(f"While updating user_data, user_name_and_avatar returned None. user_id {user.user_id}")
        return None
    user_data.update(user_name_and_avatar)
    logger.debug(f"While updating user_data, successfully received user_name_and_avatar. user_id {user.user_id}")

    user_hours_played = get_user_hours_played(steamid)
    if user_hours_played is None:  # User's profile is set to private, etc.
        update_user_model(user, user_data)
        logger.debug(f"While updating user_data, user_hours_played returned None. user_id {user.user_id}")
        user_data["hours_played"] = 0
    else:
        user_data["hours_played"] = user_hours_played
    logger.debug(f"While updating user_data, successfully received user_hours_played. user_id {user.user_id}")

    user_stats = get_user_stats(steamid)
    if user_stats is None:  # User's profile is set to private, etc.
        logger.debug(f"While updating user_data, user_stats returned None. user_id {user.user_id}")
        update_user_model(user, user_data)
        return None
    logger.debug(f"While updating user_data, successfully returned user_stats. user_id {user.user_id}")
    
    user_data.update(user_stats)
    user_data["last_successful_update"] = timezone.now()
    update_user_model(user, user_data)
    logger.debug(f"While updating user_data, successfully updated user_data. user_id {user.user_id}")


def resolve_vanity_url(vanity_url):
    try:
        user_info = requests.get("https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/", 
        params={"key": steam_api_key, "vanityurl": vanity_url})
    except Exception:
        logger.warning(f"Encountered a caught exception while trying to resolve vanity url. vanity_url {vanity_url}", exc_info=True)
        return None
    if user_info.status_code != 200:
        logger.warning(f"Encountered a caught exception while trying to resolve vanity url. Response code not 200. vanity_url {vanity_url}", exc_info=True)
        return None
    try:
        user_info = user_info.json()
        user_info = user_info["response"]

        if user_info == [] or user_info["success"] == 42:  # Check if vanity url exists
            return None
        return user_info["steamid"]
    except Exception:
        logger.warning(f"Encountered a caught exception while trying to resolve vanity url \
        (unknown format of the returned api response?). vanity_url {vanity_url}", exc_info=True)
        return None


def get_human_number_format(num):
    if num > 999999:
        round_to = 2
    elif num > 99999:
        round_to = 1
    else:
        return '{:,}'.format(int(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num = round(num / 1000.0, round_to)
    return '{:.{}f}{}'.format(round(num, round_to), round_to, ['', 'k', 'm', 'b', 't', 'p'][magnitude])


def get_human_time_format(num):
    return num / 3600


def get_category_top_users(category, users):
    """
    Returns top <users> for <category>. Users can't be banned and had to have
    their profile stats updated at least once.
    """
    try:
        args = User.objects.filter(is_banned=False, last_successful_update__isnull=False).order_by(f"-{category}")[:users]
        top_users = list(args.values("user_id", "user_name", "avatar", category))
        for top_user in top_users:
            top_user["top_value"] = top_user.pop(category)
            top_user["avatar"] = top_user["avatar"].replace("_full", "_medium")
        if [ele for ele in ["duration", "second"] if(ele in category)]:
            for top_user in top_users:
                top_user["top_value"] = top_user["top_value"] / 3600  # Get hours instead of seconds
                top_user["top_value"] = get_human_number_format(top_user["top_value"])
                top_user["top_value"] = top_user["top_value"] + " hours"

        else:
            for top_user in top_users:
                top_user["top_value"] = get_human_number_format(top_user["top_value"])
                
        return top_users
    except Exception:
        logger.exception(f"An error occurred when attempting to get_top_users. category {category}, users {users}")


@cached(cache=TTLCache(maxsize=1, ttl=300))
def get_top_rankings():
    """
    Returns a dictionary of lists for the top users for categories 
    mentioned in user_stats_names.top_categories.
    Cached every 300 seconds (5 minutes).
    """
    top_rankings = {}
    for category in top_categories:
        top_users = get_category_top_users(category[0], 25)
        if top_users:
            top_rankings[category[1]] = top_users
    return top_rankings


def get_users_friends(user_id):
    """Get a list of user's friends steam ids"""
    try:
        user_info = requests.get("http://api.steampowered.com/ISteamUser/GetFriendList/v0001/", 
        params={"key": steam_api_key, "steamid": user_id, "relationship": "friend"})
    except Exception:
        logger.warning(f"Encountered a caught exception while trying to get user's friends. user_id {user_id}", exc_info=True)
        return []
    if user_info.status_code != 200:
        logger.info(f"Encountered a caught exception while trying to get user's friends. Response code is not 200. user_id {user_id}", exc_info=True)
        return []
    try:
        user_info = user_info.json()

        if user_info == {}:
            return []
        user_info = user_info["friendslist"]["friends"]
        friend_list = []
        for friend in user_info:
            friend_list.append(friend["steamid"])
        return friend_list
    except Exception:
        logger.warning(f"Encountered a caught exception while trying to get user's friends \
        (unknown format of the returned api response?). user_id {user_id}", exc_info=True)
        return []


def update_tracked_friends(user_id):
    """Set friends of the user that are tracked on this website."""
    try:
        user = User.objects.get(pk=user_id)
    except Exception:
        return

    tracked_friends = []
    friend_list = get_users_friends(user_id)
    if friend_list != []:
        friends = User.objects.filter(user_id__in=friend_list)
        for friend in friends:
            tracked_friends.append(friend)
        # Clears <friends> relations and then sets them to new relations
        user.friends.set(tracked_friends, clear=True)
    user.friends_last_updated = timezone.now()
    user.save()