from models.models import *


# Queries
def get_an_image_for_theme(theme_key):
    """returns the first image_url associated with a theme"""
    location_report_query = LocationReport.query(LocationReport.sport_theme == theme_key)
    location_report_list = location_report_query.fetch()
    image_url = None
    if len(location_report_list) > 0:
        location_report = location_report_list[0]
        image_url = location_report.image_url
    else:
        theme_key.delete()
    return image_url
