import json, logging
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.shortcuts import render
from django.contrib.auth import logout
from django.db.models import F
from .forms import SearchUser
from .models import User
from .user_data import create_user_data, update_user_data, get_top_rankings, update_tracked_friends


logger = logging.getLogger("rust_stats")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def my_profile(request):
    try:
        user_id = str(request.user.social_auth.get(provider='steam').uid)
    except Exception:
        return HttpResponseRedirect('/login/steam')
    else:
        return HttpResponseRedirect('/rust-stats/user/' + user_id)


def index(request):
    top_users = get_top_rankings()
    if request.method == 'POST':
        form = SearchUser(request.POST)
        if form.is_valid():
            try:
                search_q = form.cleaned_data["search_q"]
                return HttpResponseRedirect('/rust-stats/user/' + search_q)
            except Exception:
                return render(request, 'rust_stats/index.html', {'form': form, 'top': top_users})
    else:
        form = SearchUser()
    return render(request, 'rust_stats/index.html', {'form': form, 'top': top_users})


def user_profile(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        user_name = user.user_name
        avatar = user.avatar
        title = f"{user_name}'s Rust Stats | View anyone's Rust stats"
        ogp_title = f"{user_name}'s Rust Stats"
    except Exception:
        title = f"Rust Stats | View anyone's Rust stats"
        ogp_title = title
        avatar = ""
        

    if request.method == 'POST':
        form = SearchUser(request.POST)
        if form.is_valid():
            try:
                search_q = form.cleaned_data["search_q"]
                return HttpResponseRedirect('/rust-stats/user/' + search_q)
            except Exception:
                return render(request, 'rust_stats/user_profile.html', {'form': form, 'title': title, 'ogp_title': ogp_title, 'avatar': avatar})
    else:
        form = SearchUser()
    return render(request, 'rust_stats/user_profile.html', {'form': form, 'title': title, 'ogp_title': ogp_title, 'avatar': avatar}) 


def user_stats(request, user_id):
    """
    Steam's API takes a while to respond. This mean that users would have to wait
    for long periods of times before the webpage is shown. In order to avoid this,
    show user a page with no stats. Then in the frontend download the data in a json
    format while showing a loading screen. When data is downloaded, render it on
    the screen.
    Returns {"success": False} if failed to get user's stats when the user does 
    not exist or the profile is private. Otherwise, returns {"success": True} +
    **{user stats}.
    """
    logger.debug(f"Received a request for user_stats data for user_id {user_id}")
    try:
        user = User.objects.get(pk=user_id)
        last_successful_update = user.last_successful_update

        # Update user's information if the user has never been successfully recorded and last update attempt was longer than 30 seconds ago.
        # Or last successful update was more than 30 minutes ago and last attempted update was more than 30 seconds ago.
        last_attempted_update = user.last_attempted_update
        if last_successful_update is None or last_successful_update + timezone.timedelta(minutes=30) < timezone.now():
            if last_attempted_update + timezone.timedelta(seconds=30) < timezone.now():
                logger.debug(f"Updating user_stats data (30 seconds) for user_id {user_id}. \
                last_successful_update {last_successful_update}, \
                last_attempted_update {last_attempted_update}")
                update_user_data(user)
        elif last_attempted_update + timezone.timedelta(minutes=30) < timezone.now():
                logger.debug(f"Updating user_stats data (30 minutes) for user_id {user_id}. \
                last_successful_update {last_successful_update}, \
                last_attempted_update {last_attempted_update}")
                update_user_data(user)

    except Exception:
        logger.debug(f"user_stats() caused a caught exception. user_id {user_id}", exc_info=True)
        if create_user_data(str(user_id)) is None:
            return JsonResponse({"success": False})
        user = User.objects.get(pk=user_id)
    # Convert model data into json response
    try:
        user_data = serializers.serialize("json", [user])
        user_data = json.loads(user_data)
        user_data = user_data[0]["fields"]
        del user_data["friends"]
        user_data["success"] = True
    except Exception:
        logger.exception("An exception occurred while trying to get user_stats request and convert it into json")
        return JsonResponse({"success": False})
    logger.debug(f"Successfully returning user_stats data for user_id {user_id}")
    return JsonResponse(user_data)


def user_friends(request, user_id):
    """
    Returns a list of friends for <user_id> that are tracked on the website.
    This function is executed after user_stats is returned.
    """
    logger.debug(f"Received a request for user_friends data for user_id {user_id}")
    try:
        user = User.objects.get(pk=user_id)
        last_successful_update = user.last_successful_update
        last_attempted_update = user.last_attempted_update
        last_friends_update = user.friends_last_updated

        # If last stats update was never and last friend update was more than 29 minutes ago then update
        if last_successful_update is None:
            if last_friends_update is None and last_attempted_update + timezone.timedelta(seconds=28) < timezone.now():
                update_tracked_friends(user_id)
            elif last_friends_update is None and last_friends_update is None:
                pass
            elif last_friends_update + timezone.timedelta(minutes=29) < timezone.now():
                update_tracked_friends(user_id)
        # If last stats update was less than 10 seconds ago and 
        # (last friend update was never OR last friend update was more than 29 minutes ago) then update
        elif timezone.now() < last_successful_update + timezone.timedelta(seconds=10):
            if last_friends_update is None:
                update_tracked_friends(user_id)
            elif last_friends_update + timezone.timedelta(minutes=29) < timezone.now():
                update_tracked_friends(user_id)
                    
    except Exception:
        logger.exception(f"An exception occurred while trying to get user_friends request and convert it into json. user_id {user_id}")
        return JsonResponse({"success": False})

    friends_data = {"friends": []}
    friend_list = []

    try:
        user = User.objects.get(pk=user_id)
        friends = user.friends.all()
        for friend in friends:
            friend_list.append({
                "user_id": friend.user_id,
                "user_name": friend.user_name,
                "avatar": friend.avatar,
                "hours_played": friend.hours_played,
            })
        friends_data["success"] = True
        friends_data["friends"] = friend_list
        friends_data["last_updated"] = user.friends_last_updated
    except Exception:
        logger.exception(f"An exception occurred while trying to convert user_friends into json. user_id {user_id}")
        return JsonResponse({"success": False})
    return JsonResponse(friends_data)


def ban_user(request):
    if not request.user.is_staff:
        return JsonResponse({"success": False})
    if request.method != 'POST' and not request.is_ajax:
        return JsonResponse({"success": False})
    try:
        user_id = request.POST["user_id"]
        ban_status = request.POST["ban_status"]
    except Exception:
        return JsonResponse({"success": False})


    if ban_status == "ban":
        try:
            user = User.objects.get(pk=user_id)
            user.is_banned = True
            user.save()
            return JsonResponse({"success": True, "response_message": "Banned the user"})
        except:
            pass
    elif ban_status == "unban":
        try:
            user = User.objects.get(pk=user_id)
            user.is_banned = False
            user.save()
            return JsonResponse({"success": True, "response_message": "Unbanned the user"})
        except:
            pass

    return JsonResponse({"success": False})


def delete_user(request):
    if not request.user.is_staff:
        return JsonResponse({"success": False})
    if request.method != 'POST' and not request.is_ajax:
        return JsonResponse({"success": False})
    try:
        user_id = request.POST["user_id"]
    except Exception:
        return JsonResponse({"success": False})

    try:
        user = User.objects.get(pk=user_id)
        user.delete()
        return JsonResponse({"success": True, "response_message": "User was deleted"})
    except:
        return JsonResponse({"success": False})


def delete_inactive_users(request):
    if not request.user.is_staff:
        return JsonResponse({"success": False})
    try:
        users = User.objects.filter(
            last_successful_update__isnull=True, 
            last_attempted_update__lte=timezone.now()-timezone.timedelta(hours=3),
            is_banned=False  # Prevers banned users even if they have a private account
        )
        count = users.count()
        users.delete()
        return JsonResponse({"response": f"Successfully deleted {count} users"})
    except Exception:
        return JsonResponse({"success": False})


def discord_bot_page(request):
    return render(request, 'rust_stats/discord_bot.html')


def page_not_found(request, exception):
    return render(request, 'rust_stats/404.html', status=404)