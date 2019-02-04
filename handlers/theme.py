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


class ThemePage(webapp2.RequestHandler):

    def get(self):

        sport_themes_and_images = get_all_sport_themes_with_images()

        current_user = users.get_current_user()
        if current_user:
            creator = create_or_get_creator(current_user.email())

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
            'url': url,
            'url_linktext': url_linktext,
            'sports_themes_and_images': sport_themes_and_images,
            'all_tag_names': json.dumps(all_tag_names)
        }

        template = JINJA_ENVIRONMENT.get_template('views/themes.html')
        self.response.write(template.render(template_values))


class ThemePageMobile(webapp2.RequestHandler):

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

            all_themes = get_all_sport_themes()
            all_themes_jsonable = list()

            for t in all_themes:
                td = dict()
                td['name'] = t.name
                td['image_url'] = get_an_image_for_theme(t.key)
                all_themes_jsonable.append(td)

            self.response.out.write(json.dumps(all_themes_jsonable))
        else:
            self.response.write('signed in user is ' + email + result)


class ThemeImagesPage(webapp2.RequestHandler):

    def get(self):

        theme_name = self.request.get("theme_name")
        location_reports = get_location_reports_by_theme(theme_name)

        theme_image_urls = get_themes_images(location_reports)

        current_user = users.get_current_user()
        if current_user:
            creator = create_or_get_creator(current_user.email())

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
            'url': url,
            'url_linktext': url_linktext,
            'theme_image_urls': theme_image_urls,
            'theme_name': theme_name
        }

        template = JINJA_ENVIRONMENT.get_template('views/theme_images.html')
        self.response.write(template.render(template_values))


class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    """Inherits from type Blobstore Download Handler"""
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)


# [START app]
app = webapp2.WSGIApplication([
    ('/themes', ThemePage),
    ('/themes/mobile', ThemePageMobile),
    ('/theme_images', ThemeImagesPage),
], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
# [END app]
