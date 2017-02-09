from google.appengine.ext import ndb


class Message(ndb.Model):
    message_text = ndb.StringProperty()
    email_text = ndb.StringProperty()
    comment_text = ndb.StringProperty()