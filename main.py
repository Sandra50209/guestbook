#!/usr/bin/env python
import os
import jinja2
import webapp2

from google.appengine.api import users
from models import Message

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
            user = users.get_current_user()
            if user:
                logged_in = True
                logout_url = users.create_logout_url("/")
                parameters = {"logged_in" : logged_in, "logout_url" : logout_url, "user" : user}
            else:
                logged_in = False
                login_url = users.create_login_url("/")
                parameters = {"logged_in": logged_in, "login_url": login_url, "user": user}
            return self.render_template("Startseite.html", parameters)

class ResultHandler(BaseHandler):
    def post(self):
        parameters = {}
        parameters["message"] = self.request.get("Name")
        parameters["name"] = self.request.get("Email")
        parameters["comment"] = self.request.get("Kommentar")
        message = Message(message_text=parameters["message"], email_text=parameters["name"], comment_text=parameters["comment"])
        message.put()
        parameters["messages"] = Message.query().fetch()
        return self.render_template("Eingabe.html", parameters)

class ChangeHandler(BaseHandler):
    def get(self):
        parameters = {}
        parameters ["messages"] = Message.query().fetch()
        return self.render_template("change.html", parameters)

class EditHandler(BaseHandler):
    def get(self, message_id):
        msg_id = int(message_id)
        msg = Message.get_by_id(msg_id)
        parameters = {}
        parameters["message_id"] = msg_id
        parameters["message_text"] = msg.message_text
        return self.render_template("edit.html", parameters)
    def post(self, message_id):
        msg_id = int(message_id)
        msg = Message.get_by_id(msg_id)
        msg.message_text = self.request.get("message")
        msg.put()
        return self.redirect_to("Eingabe")

class EndHandler(BaseHandler):
    def post(self):
        return self.render_template("end.html")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="home"),
    webapp2.Route("/Eingabe", ResultHandler, name="result"),
    webapp2.Route("/change", ChangeHandler, name="change"),
    webapp2.Route("/edit", EditHandler, name="edit"),
    webapp2.Route("/end", EndHandler, name="end")
], debug=True)