from services.report_services import *
from services.image_services import *
from models.models import *


# Queries
def get_all_sport_themes():     # works
    """returns list of sport theme object"""
    sport_themes_query = SportTheme.query()
    sport_themes = sport_themes_query.fetch()
    return sport_themes


def get_all_sport_themes_with_images():     # works
    """returns list of tuples (sport_theme, image_url)"""
    sport_themes_query = SportTheme.query()
    sport_themes = sport_themes_query.fetch()
    sport_themes_with_images = []
    for st in sport_themes:
        image_url = get_an_image_for_theme(st.key)
        tup = (st, image_url)
        sport_themes_with_images.append(tup)
    return sport_themes_with_images


def get_this_users_theme_names(creator):     # works

    # query gets all themes this user subscribes to
    sport_theme_keys = creator.subscribed_sport_themes
    if sport_theme_keys:
        sport_themes = []
        for stk in sport_theme_keys:
            sport_themes.append(stk.get().name)
    else:
        sport_themes = []
    return sport_themes


def get_themes_images(location_reports):  # needs testing
    """returns list of theme_image urls"""
    image_urls = []
    for lr in location_reports:
        image_urls.append(lr.image_url)
    return image_urls


# Creates or Gets
def create_or_get_sport_theme(sport_theme_name):    # works

    # check if sport_theme already exists
    sport_theme_query = SportTheme.query()
    sport_themes = sport_theme_query.fetch()
    is_new = True
    for st in sport_themes:

        # if it does, save the found sport_theme into sport_theme
        if st.name == sport_theme_name:
            is_new = False
            sport_theme = st
            break

    # else, create a new sport_theme
    if is_new:
        sport_theme = SportTheme()
        sport_theme.name = sport_theme_name
        sport_theme.put()

    return sport_theme


def add_subscribed_sport_themes_to_creator(creator, sport_theme_names):     # works
    del creator.subscribed_sport_themes

    new_sport_themes = []
    for stn in sport_theme_names:
        new_sport_themes.append(create_or_get_sport_theme(stn))

    for nst in new_sport_themes:
        creator.subscribed_sport_themes.append(nst.key)
    creator.put()
