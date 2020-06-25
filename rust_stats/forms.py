from django import forms
from .user_data import resolve_vanity_url
import re


steam_url_regex = r"(?:https?:\/\/)?steamcommunity\.com\/((?:profiles|id))\/([a-zA-Z0-9-_]+)"
steam_uid_regex = r"^([a-zA-Z0-9-_]+)$"
steam_steam_64_id_regex = r"^([0-9]+)$"
error_msg = "Error! Please enter full link to a Steam profile, or the Steam id."


class SearchUser(forms.Form):
    search_q = forms.CharField(label="Search users", max_length=250, required=True, widget=forms.TextInput(attrs={'placeholder': 'steamcommunity.com/id/your_profile/'}))

    def clean_search_q(self):
        search_q = self.cleaned_data["search_q"]

        matches_url = re.search(steam_url_regex, search_q)
        matches_uid = re.search(steam_uid_regex, search_q)

        if not(matches_url or matches_uid):
            raise forms.ValidationError(error_msg)

        if matches_url:
            if matches_url.group(1):
                if matches_url.group(1) == "profiles":  # Url with steam id 64, return steam id
                    return matches_url.group(2)
                else:  # Url with vanity id, resolve steam id 64 and return it
                    resolved_steam_id = resolve_vanity_url(matches_url.group(2))
                    if not resolved_steam_id:
                        raise forms.ValidationError(error_msg)
                    else:
                        return resolved_steam_id
        
        if matches_uid:
            uid = matches_uid.group(1)
            matches_steam_64_id = re.search(steam_steam_64_id_regex, uid)
            if matches_steam_64_id:  # If matches steam id 64, return it
                return uid
            else:
                resolved_steam_id = resolve_vanity_url(uid)
                if not resolved_steam_id:
                    raise forms.ValidationError(error_msg)
                else:
                    return resolved_steam_id
        raise forms.ValidationError("Unknown error has occurred! Please try again.")