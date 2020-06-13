import json, logging
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from .models import User
from .user_data import create_user_data, update_user_data


logger = logging.getLogger("rust_stats")


def index(request):
    return HttpResponse("Index page")


def user_profile(request, user_id):
    return HttpResponse("user profile for id " + str(user_id))


def user_stats(request, user_id):
    """
    Steam's API takes a while to respond. This mean that users would have to wait
    for long periods of times before the webpage is shown. In order to avoid this,
    show user a page with no stats. Then in the frontend download the data in a json
    format while showing a loading screen. When data is downloaded, render it on
    the screen.
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

    except ObjectDoesNotExist:
        logger.debug(f"user_stats() caused a caught exception ObjectDoesNotExist. user_id {user_id}", exc_info=True)
        create_user_data(str(user_id))
        user = User.objects.get(pk=user_id)
    # Convert model data into json response
    try:
        user_data = serializers.serialize("json", [user])
        user_data = json.loads(user_data)
        user_data = user_data[0]["fields"]
        user_data["success"] = True
    except Exception:
        logger.exception("An exception occurred while trying to get user_stats request and convert it into json")
        return JsonResponse({"success": False})
    logger.debug(f"Successfully returning user_stats data for user_id {user_id}")
    return JsonResponse(user_data)