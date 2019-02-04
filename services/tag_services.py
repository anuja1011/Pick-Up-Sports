from models.models import *


# Queries
def get_all_tags():
    """returns list of tag objects"""
    tag_query = Tag.query()
    tags = tag_query.fetch()
    return tags


def get_all_tag_names():
    """returns list of tag names"""
    tags = get_all_tags()
    tag_names = []
    for t in tags:
        tag_names.append(t.tag_name)
    return tag_names


# Create or Gets
def create_or_get_tag(tag_name):
    """returns a tag object after either creating a new tag or finding one"""
    all_tag_names = get_all_tag_names()
    if tag_name in all_tag_names:
        tag_to_return_query = Tag.query(Tag.tag_name == tag_name)
        tag_to_return_list = tag_to_return_query.fetch()
        tag_to_return = tag_to_return_list[0]
    else:
        tag_to_return = Tag()
        tag_to_return.tag_name = tag_name
    tag_to_return.put()
    return tag_to_return
