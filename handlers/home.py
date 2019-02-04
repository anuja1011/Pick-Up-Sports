import os

import jinja2
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb

from lib import cloudstorage as gcs
from lib.google.auth.transport import requests
from lib.google.oauth2 import id_token

import json

from services.report_services import *
from services.creator_services import *
from services.tag_services import *

import logging


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

CLIENT_ID = '145529355835-h041hu1f81v9o1gksrknfue45r891b25.apps.googleusercontent.com'


class HomePage(webapp2.RequestHandler):

    def get(self):

        # Get current user, if logged in, create new Creator if not already created
        current_user = users.get_current_user()
        if current_user:
            creator = create_or_get_creator(current_user.email())
            location_reports = get_this_users_subscribed_reports(creator.email)
        else:
            location_reports = get_all_location_reports()

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
            'location_reports': location_reports,
            'url': url,
            'url_linktext': url_linktext,
            'all_tag_names': json.dumps(all_tag_names)
        }
        template = JINJA_ENVIRONMENT.get_template('views/home.html')
        self.response.write(template.render(template_values))

    def post(self):
        uploaded_file = self.request.POST.get("file")
        uploaded_file_content = uploaded_file.file.read()
        uploaded_file_filename = uploaded_file.filename
        uploaded_file_type = uploaded_file.type
        bucket_name = 'pick-up-sports-images'

        # This write_retry_params params bit isn't essential, but Google's examples recommend it
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(
            "/" + bucket_name + "/" + uploaded_file_filename,
            "w",
            content_type=uploaded_file_type,
            retry_params=write_retry_params
        )
        gcs_file.write(uploaded_file_content)
        gcs_file.close()

        image_url = 'https://storage.googleapis.com' + "/" + bucket_name + "/" + uploaded_file_filename

        location_name = self.request.get('location_name')
        address = self.request.get('address')
        sport_theme_name = self.request.get('sport_theme_name')
        tag_names_string = self.request.get('tags')
        tag_name_list = tag_names_string.split()

        current_user = users.get_current_user()
        if current_user:
            creator = create_or_get_creator(current_user.email())
            creator_email = creator.email
        else:
            creator_email = None

        # create location report
        create_location_report(location_name, address, sport_theme_name, creator_email, tag_name_list, image_url)
        self.redirect('/')


class HomePageMobile(webapp2.RequestHandler):

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

            location_reports = get_this_users_subscribed_reports(email)
            location_reports_jsonable = list()

            for lr in location_reports:
                lrd = dict()
                lrd['name'] = lr.name
                lrd['address'] = lr.address
                lrd['sport_theme'] = lr.sport_theme.get().name
                lrd['creator_email'] = lr.user_email
                lrd['image_url'] = lr.image_url
                # lrd['tags'] = lr.tag_name_string
                location_reports_jsonable.append(lrd)

            self.response.out.write(json.dumps(location_reports_jsonable))
        else:
            self.response.write('signed in user is ' + email + result)

    def post(self):

        token = self.request.get('token')
        email = self.request.get('email')
        result = ""

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

            # upload new image from android
            # uploaded_file = self.request.POST.get("image")
            # uploaded_file_content = uploaded_file.file.read()
            # uploaded_file_filename = uploaded_file.filename
            # uploaded_file_type = uploaded_file.type
            # bucket_name = 'pick-up-sports-images'
            #
            # # This write_retry_params params bit isn't essential, but Google's examples recommend it
            # write_retry_params = gcs.RetryParams(backoff_factor=1.1)
            # gcs_file = gcs.open(
            #     "/" + bucket_name + "/" + uploaded_file_filename,
            #     "w",
            #     content_type=uploaded_file_type,
            #     retry_params=write_retry_params
            # )
            # gcs_file.write(uploaded_file_content)
            # gcs_file.close()
            #
            # image_url = 'https://storage.googleapis.com' + "/" + bucket_name + "/" + uploaded_file_filename

            # temporary image for location report from android until I figure out how to upload an image from android
            image_url = 'https://00e9e64baca7129fd93c9b3c8fae1d3ae5001f077dd61bb04b-apidata.googleusercontent.com/download/storage/v1/b/pick-up-sports-images/o/android-p1.jpg?qk=AD5uMEuOyI7kIsV5921fxnl-gWsfZOKuVbNlQ0Lw7LKG2rLUpSqfQ_ZjHI4SP_N-qxx9SwFXvYFeY2UHR6teOmaFpbnbAlxefv_QNBTITsAd_cZAN9uFhEmS4UIn902NXs0tkffM3cpqLGIEd6tGuDXZXWRVhcpRKbhDzFCKrsV3k-EXamjkg1nJpghP2qD97tgcUSZ_2SPeGpWSpxHP8GXpb-035YggBqcNFQg0g3feGprHlIEWBgdogaggLIrnURw25xif4ZeRNuntjt1qGHvaqr5UJ-FGxannzHDze963-nxCnLPCNpPFFmLFcEP6I8TuT2zg9gzCKo_T-V6SgxpDbqsop3tDBiKllOF916BcA1CNoJz-GmIBZuWh0R1YilaLGLItENa_NrUtLo4yW86ZipTiXH9lAccvQv44Zw1cr-CukEOo639n-evNOMCNTRqAWzkNTeSsT3CrAtunzzwcMF1B3_D8M1M6Vq-n9Dnv9qMOpPcpe8DhqqHyjFrd_p2-vlenyTXda8SLapI0i77hTfVfSBQMOUn6p5mL-OaoSb_a9xUFIom6ey8fehPVIFClvkNGeAR833Y8vu6DCeifvoUlZnI5tjRKjLTy4AR7Y3umvRUEznJOFJfD9r_txOjI4emW_7pYPn78SxoSMZfro4zqQlrWMKWJ0sC-DlJgIjANvVEKA6dkcGoBKGHNoq9bM9Noz1aCeA-X_MK_bP0n9xK6nZLrGbDsSwAzTofEqV8Scd2dhs4'
            location_name = self.request.get('location_name')
            address = self.request.get('address')
            sport_theme_name = self.request.get('sport_theme_name')
            tag_names_string = self.request.get('tags')
            tag_name_list = tag_names_string.split()

            create_location_report(location_name, address, sport_theme_name, email, tag_name_list, image_url)

        else:
            self.response.write('signed in user is ' + email + result)

# [START app]
app = ndb.toplevel(webapp2.WSGIApplication([
    ('/', HomePage),
    ('/add_location_report', HomePage),
    ('/mobile/home_page', HomePageMobile)
], debug=True))


def main():
    app.run()


if __name__ == "__main__":
    main()
# [END app]
