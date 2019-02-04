import os
from google.appengine.api import users
import jinja2
import webapp2
import urllib
import json

from services.report_services import *
from services.tag_services import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class SearchPage(webapp2.RequestHandler):

    def get(self):

        current_user = users.get_current_user()

        tag_string = self.request.get('tags')
        searched_tags_list = tag_string.split()

        if tag_string != "":
            tag_name_list = tag_string.split()
            location_reports = search_location_reports_by_tags(tag_name_list)
        else:
            location_reports = []

        all_tag_names = get_all_tag_names()  # tags for search bar suggestions

        if current_user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        # create dictionary that we pass to the template
        template_values = {
            'url': url,
            'url_linktext': url_linktext,
            'user': current_user,
            'location_reports': location_reports,
            'all_tag_names': json.dumps(all_tag_names),
            'searched_tags_list': searched_tags_list
        }
        template = JINJA_ENVIRONMENT.get_template('views/search.html')
        self.response.write(template.render(template_values))

    def post(self):
        tag_string = self.request.get('tags')
        query_params = {'tags': tag_string}
        self.redirect('/search?' + urllib.urlencode(query_params))


# [START app]
app = webapp2.WSGIApplication([
    ('/search', SearchPage),
], debug=True)

def main():
    app.run()

if __name__ == "__main__":
    main()
# [END app]