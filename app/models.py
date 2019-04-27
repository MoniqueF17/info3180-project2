from . import db, bcryptHash
import datetime

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    photo = db.Column(db.String(255))
    caption = db.Column(db.String(255))
    created_on = db.Column(db.DateTime)

    def __init__(self, user_id, image, cap):
        self.user_id = user_id
        self.photo = image
        self.caption = cap
        self.created_on = datetime.datetime.now()


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(255))
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    email = db.Column(db.String(80))
    location = db.Column(db.String(225))
    biogarphy = db.Column(db.String(140))
    profile_photo = db.Column(db.String(255))
    joined_on = db.Column(db.DateTime)

    def __init__(self, uName, password, fName, lName, email, loc, bio, image):
        self.username = uName
        self.password = bcryptHash.generate_password_hash(password) 
        self.firstname = fName
        self.lastname = lName
        self.email = email
        self.location = loc
        self.biogarphy = bio
        self.profile_photo = image
        self.joined_on = datetime.datetime.now()

        # # Creates password for db storage
        # pw_hash = bcrypt.generate_password_hash('hunter2')
        # bcryptHash.check_password_hash(pw_hash, 'hunter2') # returns True

        # # Check Password for login
        # candidate = 'secret'
        # bcrypt.check_password_hash(pw_hash, candidate)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return '<User %r>' % (self.username)

class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.String(255))

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id

class Follows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    follower_id = db.Column(db.String(255))

    def __init__(self, user_id, follower_id):
        self.user_id = user_id
        self.follower_id = follower_id
