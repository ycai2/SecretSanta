import os
import re
from string import letters

import webapp2
import jinja2
import random

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)



############################


class MainPage(MainHandler):
    #friends = db.GqlQuery("select * from Friends order by created desc limit 10")
    def get(self):
        friends = db.GqlQuery("select * from Friends order by created desc limit 10")
        santa = ' '
        self.render('main.html', friends = friends, santa = santa)

    def post(self):
        friends = db.GqlQuery("select * from Friends order by created desc limit 10")
        current = self.request.get('name')
        santa = None
        for friend in friends:
          if friend.picked == False and random.randint(1,2) == 1 and friend.name != current:
            print friend.name
            santa = friend
            break

        if not santa:
          for friend in friends:
            if friend.picked == False and friend.name != current:
              santa = friend
              break


        if santa:
          friend_current = Friends.by_name(santa.name)
          friend_current.picked = True
          friend_current.put()


        self.render('main.html', friends = friends, santa = santa)
        

def friend_key(name = 'default'):
    return db.Key.from_path('friends', name)

class Friends(db.Model):
    name = db.StringProperty(required = True)
    address = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    picked = db.BooleanProperty()

    @classmethod
    def by_name(cls, name):
        n = Friends.all().filter('name =', name).get()
        return n

    @classmethod
    def register(cls, name, address, picked):
        return Friends(name = name, address = address, picked = picked)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

class Signup(MainHandler):

    def get(self):
        self.render("signup-form.html")

    def post(self):
        self.name = self.request.get('name')
        self.address = 'add'
        self.done()


class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        f = Friends.by_name(self.name)
        if f:
            msg = 'That name already exists. '
            self.render('signup-form.html', error_name = msg)
        else:
            f = Friends.register(self.name, self.address, False)
            f.put()
            self.redirect('/signup')


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', Register)
                               ],
                              debug=True)
