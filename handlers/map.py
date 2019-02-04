import os
from google.appengine.api import users
import jinja2
import webapp2
from google.appengine.ext import ndb
import json

from services.report_services import *
from services.creator_services import *
from services.tag_services import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

class MapPage(webapp2.RequestHandler):

    def get(self):
        # Get current user, if logged in, create new Creator if not already created
        current_user = users.get_current_user()
        if current_user:
            creator = create_or_get_creator(current_user.email())
            location_reports = get_this_users_subscribed_reports(creator.email)
        else:
            location_reports = get_all_location_reports()

        all_tag_names = get_all_tag_names()  # tags for search bar suggestions
        # addresses = get_subscribed_reports_addresses(location_reports)
        location_reports_lists = get_subscribed_reports_addresses_names_imageurls(location_reports)

        # if logged in, create url and url_linktext for logout/login button
        if current_user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        # create dictionary that we pass to the template
        template_values = {
            'user': current_user,
            'location_reports': location_reports,
            'url': url,
            'url_linktext': url_linktext,
            'all_tag_names': json.dumps(all_tag_names),
            # 'addresses': json.dumps(addresses)
            'location_reports_list': json.dumps(location_reports_lists)
        }
        template = JINJA_ENVIRONMENT.get_template('views/map.html')
        self.response.write(template.render(template_values))


# [START app]
app = ndb.toplevel(webapp2.WSGIApplication([
    ('/map', MapPage),
], debug=True))


def main():
    app.run()


if __name__ == "__main__":
    main()
# [END app]
