from models.models import *


# Creates
def create_or_get_creator(email):   # works

    # check if we already have a creator with this user's email
    creator_query = Creator.query(email == Creator.email)
    creator = creator_query.fetch()

    # if there is already this creator, get it
    if len(creator) == 1:
        creator = creator[0]

    # if there is no creator for this user yet, create one
    else:
        creator = Creator()
        creator.email = email
        creator.put()

    return creator
