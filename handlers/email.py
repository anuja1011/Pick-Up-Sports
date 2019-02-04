from google.appengine.api import app_identity
from google.appengine.api import mail
import webapp2


def send_approved_mail(sender_address):
    # [START send_mail]
    mail.send_mail(sender=sender_address,
                   to="Barrett Poth <barrettpoth@utexas.edu>",
                   subject="Your account has been approved",
                   body="""Dear Albert:
Your example.com account has been approved.  You can now visit
http://www.example.com/ and sign in using your Google Account to
access new features.
Please let us know if you have any questions.
The example.com Team
""")
    # [END send_mail]


class SendMailHandler(webapp2.RequestHandler):
    def get(self):
        send_approved_mail("barrett.a.poth@gmail.com")
        self.response.content_type = 'text/plain'
        self.response.write('Sent an email to Albert.')


app = webapp2.WSGIApplication([
    ('/send_mail', SendMailHandler),
], debug=True)