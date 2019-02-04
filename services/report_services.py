from google.appengine.api import search

from services.theme_services import *
from services.creator_services import *
from services.tag_services import *


# Queries
def get_all_location_reports():             # works
    """returns list of all LocationReport objects in datastore"""
    location_reports_query = LocationReport.query().order(-LocationReport.date)
    location_reports = location_reports_query.fetch()
    return location_reports


def get_this_users_created_reports(user_email):    # works
    """returns list of LocationReports that a certain user created"""
    location_reports_query = LocationReport.query(LocationReport.user_email == user_email).order(-LocationReport.date)
    location_reports = location_reports_query.fetch()
    return location_reports


def get_this_users_subscribed_reports(user_email):  # works
    """returns list of LocationReports that have a SportTheme that a certain user is subscribed to"""
    creator = create_or_get_creator(user_email)
    location_reports = []
    if creator.subscribed_sport_themes != []:
        creators_subscriptions = creator.subscribed_sport_themes
        all_location_reports = get_all_location_reports()
        for lr in all_location_reports:
            if lr.sport_theme in creators_subscriptions:
                location_reports.append(lr)
    return location_reports


def get_subscribed_reports_addresses(location_reports):  # workds
    """returns list of string addresses for given LocationReports"""
    addresses = []
    for lr in location_reports:
        addresses.append(lr.address)
    return addresses


def get_subscribed_reports_addresses_names_imageurls(location_reports):     # needs testing
    """returns list of lists containing [image_url, name, address, SportTheme.name]"""
    location_report_lists = []
    for lr in location_reports:
        image_url = lr.image_url
        name = lr.name
        address = lr.address
        sport_theme_name = lr.sport_theme.get().name
        location_report_lists.append([image_url, name, address, sport_theme_name])
    return location_report_lists


def get_location_reports_by_theme(theme_name):  # works
    """returns a list of LocationReports that have a certain SportTheme"""
    theme = create_or_get_sport_theme(theme_name).key
    location_report_query = LocationReport.query(LocationReport.sport_theme == theme)
    location_reports = location_report_query.fetch()
    return location_reports


def search_location_reports_by_tags(tag_name_list):    # works
    """returns a list of LocationReports that contain a certain tag"""
    all_location_reports = get_all_location_reports()
    location_report_key_set = set()

    tag_key_list = []
    for tn in tag_name_list:
        tag = create_or_get_tag(tn)
        tag_key = tag.key
        tag_key_list.append(tag_key)

    for lr in all_location_reports:
        lr_tag_keys = lr.tags
        for tk in tag_key_list:
            if tk in lr_tag_keys:
                location_report_key_set.add(lr.key)
                break

    location_reports = []
    for lrk in location_report_key_set:
        location_reports.append(lrk.get())
    return location_reports


def search_location_reports(query_string):
    # TODO: trying to implement google search api for future awesomeness
    sort = search.SortOptions(expressions=[
        search.SortExpression(expression='date',
                              direction=search.SortExpression.DESCENDING)
    ])

    options = search.QueryOptions(
        sort_options=sort,
        returned_fields=['address', 'date', 'sport_theme', 'user_email', 'image_url', 'tags']
    )

    query_string = ''.join(['pieces:', query_string])
    query = search.Query(query_string=query_string, options=options)

    results = search.Index('api-location-reports').search(query)
    out = {'results': []}
    if results:
        for item in results:
            out['results'].append({f.name: f.value for f in item.fields})
    return out


# Creates or Gets
def create_location_report(name, address, sport_theme_name, current_user_email, tag_name_list, image_url):  # works
    """returns a LocationReport after either pulling from datastore or creating new object"""
    location_report = LocationReport()

    location_report.name = name
    location_report.address = address

    # Create or get sport_theme and add to lr key property
    sport_theme = create_or_get_sport_theme(sport_theme_name)
    location_report.sport_theme = sport_theme.key

    location_report.user_email = current_user_email

    # Create or get tag for each tag name and add to lr repeated key property
    for tn in tag_name_list:
        tag = create_or_get_tag(tn)
        location_report.tags.append(tag.key)

    location_report.image_url = image_url

    location_report.put()


