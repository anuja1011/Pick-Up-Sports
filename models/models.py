from google.appengine.ext import ndb


class Creator(ndb.Model):
    """Unique"""
    email = ndb.StringProperty()
    subscribed_sport_themes = ndb.KeyProperty('SportTheme', repeated=True, indexed=True)


class LocationReport(ndb.Model):
    name = ndb.StringProperty()
    address = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    sport_theme = ndb.KeyProperty(kind="SportTheme", repeated=False, indexed=True)  # this stores a sport key
    user_email = ndb.StringProperty()  # this will store the email of the user who created the location_report
    image_url = ndb.StringProperty()
    tags = ndb.KeyProperty(kind="Tag", repeated=True)

    @property
    def tag_name_string(self):
        """returns string of all tag names space delimited"""
        tag_name_string = ""
        for tk in self.tags:
            tag_name_string += tk.get().tag_name
            tag_name_string += " "
        return tag_name_string


class SportTheme(ndb.Model):
    """Unique"""
    name = ndb.StringProperty()


class Tag(ndb.Model):
    """Unique"""
    tag_name = ndb.StringProperty()

    @property
    def location_reports(self):
        """returns keys for location reports associated with tag"""
        location_report_query = LocationReport.query().filter(LocationReport.tags == self.key)
        location_reports = location_report_query.fetch()
        return location_reports

    # Computed property that contains location report names
    @property
    def location_report_names(self):
        """returns list of location report names associated with tag"""
        location_report_keys = self.location_reports
        location_report_names = []
        for lrk in location_report_keys:
            location_report_names.append(lrk.get().name)
        return location_report_names
