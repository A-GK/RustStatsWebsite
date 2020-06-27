from django.conf import settings
from .models import User


def insert_delimiters(stats_unit):
    return "!{user." + str(stats_unit) + "}"


def get_delimeters_and_names(stats):
    """
    Returns new list of lists of dictionaries in a form of
    [ [{value: !{value}, verbose_name: "Some Statistic"}], [{...}], [{...}] ]
    """
    return_values = []
    for stats_unit in stats:
        return_values.append({
            "value": insert_delimiters(stats_unit[0]),
            "verbose_name": stats_unit[1]
        })
    return return_values


def categories(request):
    categories = [
        {
            "topic": "Player vs Player",
            "isWide": True,
            "stats": get_delimeters_and_names([
                ["kill_players", "Kills"],
                ["KDR", "KDR"],
                ["bullets_hit_players", "Bullets hit"],
                ["headshots", "Headshots"],
                ["deaths", "Deaths"],
                ["bullets_fired", "Bullets fired"],
                ["bullets_hit_players_percentage", "Bullets hit %"],
                ["headshot_percentage", "Headshot %"],
            ])
        },
        {
            "topic": "Bullets Hit",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["bullets_hit_players", "Players"],
                ["bullets_hit_buildings", "Buildings"],
                ["bullets_hit_signs", "Signs"],
                ["bullets_hit_wolfs", "Wolfs"],
                ["bullets_hit_bears", "Bears"],
                ["bullets_hit_boars", "Boars"],
                ["bullets_hit_deer", "Deer"],
                ["bullets_hit_horses", "Horses"],
                ["bullets_hit_player_corpses", "Dead players"],
                ["bullets_hit_entities", "Other"],
            ])
        },
        {
            "topic": "Kills",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["kill_players", "Players"],
                ["kill_scientists", "Scientists"],
                ["kill_bears", "Bears"],
                ["kill_boars", "Boars"],
                ["kill_wolfs", "Wolfs"],
                ["kill_deer", "Deer"],
                ["kill_chickens", "Chickens"],
                ["kill_horses", "Horses"],
            ])
        },
        {
            "topic": "Bow Hits",
            "isWide": True,
            "stats": get_delimeters_and_names([
                ["arrows_fired", "Shots fired"],
                ["arrows_hit_players", "Players"],
                ["arrows_hit_buildings", "Buildings"],
                ["arrows_hit_bears", "Bears"],
                ["arrows_hit_boars", "Boars"],
                ["arrows_hit_deer", "Deer"],
                ["arrows_hit_horses", "Horses"],
            ])
        },
        {
            "topic": "Shotgun Hits",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["shotguns_fired", "Shots fired"],
                ["shotgun_bullets_hit_player", "Players"],
                ["shotgun_bullets_hit_building", "Buildings"],
                ["shotgun_bullets_hit_entities", "Other"],
            ])
        },
        {
            "topic": "Deaths",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["deaths", "Total"],
                ["deaths_to_selfinflicted", "Selfinflicted"],
                ["deaths_to_fall", "Fall"],
                ["deaths_to_entities", "Other"],
            ])
        },
        {
            "topic": "Wounds",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["wounded", "Wounded"],
                ["wounded_assisted", "Assisted"],
                ["wounded_healed", "Self-Healed"],
            ])
        },
        {
            "topic": "Menus Opened",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["inventory_opened", "Inventory"],
                ["map_opened", "Map"],
                ["crafting_menu_opened", "Crafting"],
                ["cupboards_opened", "Cupboard"],
            ])
        },
        {
            "topic": "Gathered",
            "isWide": True,
            "stats": get_delimeters_and_names([
                ["gathered_metal_ore", "Metal ore"],
                ["gathered_stone", "Stone"],
                ["gathered_wood", "Wood"],
                ["gathered_scrap", "Scrap"],
                ["gathered_cloth", "Cloth"],
                ["gathered_lowgrade", "Low grade"],
                ["gathered_leather", "Leather"],
            ])
        },
        {
            "topic": "Building Blocks",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["placed_blocks", "Placed"],
                ["blocks_upgraded", "Upgraded"],
            ])
        },
        {
            "topic": "Horse Distance Ridden",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["horse_distance_ridden_km", "Kilometers"],
                ["horse_distance_ridden_mi", "Miles"],
            ])
        },
        {
            "topic": "Melee",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["melee_strikes", "Strikes"],
                ["melee_throws", "Throws"],
            ])
        },
        {
            "topic": "Consumed",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["calories_consumed", "Calories"],
                ["water_consumed", "Water"],
            ])
        },
        {
            "topic": "Exposure to",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["comfort_exposure_duration", "Comfort"],
                ["radiation_exposure_duration", "Radiation"],
                ["cold_exposure_duration", "Cold"],
                ["overheated_exposure_duration", "Heat"],
            ])
        },
        {
            "topic": "Instruments",
            "isWide": False,
            "stats": get_delimeters_and_names([
                ["instruments_notes_played", "Notes played"],
                ["instruments_notes_played_binds", "Note binds"],
                ["instruments_full_keyboard_mode", "Full Keyboard"],
            ])
        },
        {
            "topic": "Other",
            "isWide": True,
            "stats": get_delimeters_and_names([
                ["rockets_fired", "Rockets fired"],
                ["items_examined", "Items inspected"],
                ["items_dropped", "Items dropped"],
                ["destroyed_barrels", "Barrels destroyed"],
                ["voice_chat_seconds", "Voicechat Time"],
                ["blueprints_learned", "Blueprints Learned"],
                ["oilrig_helipad_landings", "Oilrig Helipad Pilot Landings"],
            ])
        },
    ]

    return {
        'categories': categories,
    }
