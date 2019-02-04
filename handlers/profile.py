import os
from google.appengine.api import users
import jinja2
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from lib.google.auth.transport import requests
from lib.google.oauth2 import id_token

import json

from services.report_services import *
from services.theme_services import *
from services.creator_services import *
from services.tag_services import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

CLIENT_ID = '145529355835-h041hu1f81v9o1gksrknfue45r891b25.apps.googleusercontent.com'


class ProfilePage(webapp2.RequestHandler):

    def get(self):

        sport_themes_and_images = get_all_sport_themes_with_images()
        current_user = users.get_current_user()
        if current_user:
            creator = create_or_get_creator(current_user.email())
            users_location_reports = get_this_users_created_reports(creator.email)
        else:
            creator = None
            users_location_reports = None

        all_tag_names = get_all_tag_names()  # tags for search bar suggestions

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
            'creator': creator,
            'sport_themes_and_images': sport_themes_and_images,
            'location_reports': users_location_reports,
            'url': url,
            'url_linktext': url_linktext,
            'all_tag_names': json.dumps(all_tag_names)
        }
        template = JINJA_ENVIRONMENT.get_template('views/profile.html')
        self.response.write(template.render(template_values))

    def post(self):

        current_user = users.get_current_user()
        if current_user:
            print ("here")
            creator = create_or_get_creator(current_user.email())
            new_sport_theme_names = self.request.POST.getall("sport_theme_name")
            add_subscribed_sport_themes_to_creator(creator, new_sport_theme_names)
        self.redirect('/profile')


class ProfilePageMobile(webapp2.RequestHandler):

    def get(self):

        token = self.request.get('token')
        email = self.request.get('email')
        result = ""

        # based on the example here: https://developers.google.com/identity/sign-in/android/backend-auth
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                result = " bad issuer"
                raise ValueError('Wrong issuer.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            user_id = id_info['sub']

        except ValueError, e:
            result = " " + str(e)
            # Invalid token
            pass

        if user_id:

            created_location_reports = get_this_users_created_reports(email)
            created_location_reports_jsonable = list()

            for lr in created_location_reports:
                lrd = dict()
                lrd['name'] = lr.name
                lrd['address'] = lr.address
                lrd['sport_theme'] = lr.sport_theme.get().name
                lrd['creator_email'] = lr.user_email
                lrd['image_url'] = lr.image_url
                # lrd['tags'] = lr.tag_name_string
                created_location_reports_jsonable.append(lrd)

            self.response.out.write(json.dumps(created_location_reports_jsonable))
        else:
            self.response.write('signed in user is ' + email + result)

# [START app]
app = webapp2.WSGIApplication([
    ('/profile', ProfilePage),
    ('/profile/mobile', ProfilePageMobile),
    ('/manage_subscriptions', ProfilePage),
], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
# [END app]
