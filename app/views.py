"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.forms import CreateUserForm, LoginForm, CreatPostForm
from app.models import Posts, UserProfile, Likes, Follows
#from image_getter import get_images
import random, os, datetime, requests #urlparse
import jwt

###
# Routing for your application.
###

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.headers.get('Authorization', None)
    if not auth:
      return jsonify({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'}), 401

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}), 401
    elif len(parts) == 1:
      return jsonify({'code': 'invalid_header', 'description': 'Token not found'}), 401
    elif len(parts) > 2:
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}), 401

    token = parts[1]
    try:
         payload = jwt.decode(token, token_key)
         get_user = Users.query.filter_by(id=payload['user_id']).first()

    except jwt.ExpiredSignature:
        return jsonify({'code': 'token_expired', 'description': 'token is expired'}), 401
    except jwt.DecodeError:
        return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401

    g.current_user = user = payload['user_id']
    return f(*args, **kwargs)
    
  return decorated

@app.route('/')
def index():
    """Render website's initial page and let VueJS take over."""
    return render_template('index.html')

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')

###----------------------------------- START OF SPECIFIED API ROUTES ---------------------------------------------###
@app.route('/api/users/register', methods=["GET", "POST"])
def register():
    """Accepts user information and saves it to the database."""
    form = CreateUserForm()
    if request.method == "POST":
        form.FormSubmitted = True
        
        if form.validate_on_submit():            
            if validFileExtension(request.files['imgfile'].filename):
                file_folder = app.config['UPLOAD_FOLDER']

                # Assigns 1 of 7 default profile pics if the user has not uploaded one
                if request.files['imgfile'].filename != "":
                    file = request.files['imgfile']
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(file_folder, filename))
                else:
                    filename = randomDefaultProfilePic()
                
                # Assigns the default bio if the user has not uploaded one
                if form.bio.data == "":
                    form.bio.data = app.config['DEFAULT_BIO']

                NewProfile = UserProfile(form.uName.data, form.password.data, form.fName.data, form.lName.data, 
                                        form.email.data, form.loc.data, form.bio.data, filename)

                db.session.add(NewProfile)
                db.session.commit()

                flash('Profile created and successfully saved', 'success')
                login_user(NewProfile)
                return redirect(url_for('profile'))
        
            else:
                form.imgfile.errors.append("Invalid image file uploaded")

    return render_template('register.html',form=form)
    

@app.route('/api/auth/login', methods=["GET", "POST"])
def login():
    """Accepts login credentials as email and password"""
    # If the user is already logged in then it will just return them to the 
    # home page instead of logging them in again
    if (current_user.is_authenticated):
        return redirect(url_for('home'))
    
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        
            # Get the username and password values from the form.
            username = form.username.data
            password = form.password.data
            
            user = UserProfile.query.filter_by(username=username).first()
            
            # Fails if username doesn't exist 
            if user is not None: 
                # Compares Bcrypt hash to see if password is correct
                if (bcryptHash.check_password_hash(user.password, password)):
                    login_user(user)
                    flash('User successfully logged in .', 'success')
                    next = request.args.get('next')
                    return redirect(url_for('home'))
            
            flash('Username or Password is incorrect.', 'danger')                
    return render_template("login.html", form=form)


@app.route("/api/auth/logout")
@login_required
def logout():
    """Logout a user"""
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


@app.route('/api/users/{user_id}/posts', methods=["POST"])
@login_required
def addPost(user_id):
    """Used for adding posts to the users feed"""
    form = CreatPostForm()
    if request.is_json:
        data = request.get_json(force=True)
        
        NewPost = Photos(user_id, data["photo"], data["caption"])
                                
        db.session.add(NewPost)
        db.session.commit()

        result = {"error": "null",
                  "data": {
                      "item":{
                          "user_id": user_id,
                          "photo": NewPost.photo,
                          "description": NewPost.caption
                      }
                  }, 
                  "message":"Success"}
        flash('Photo successfully posted.', 'success')
        print ("Success")
    else:
        result = {"error": "true", "data": {}, "message": "Unable to post photo."}
        print ("failed")
    print ("returning")
    return jsonify(result)


@app.route('/api/users/{user_id}/posts', methods=["GET"])
@login_required
def userPostsPage(user_id):
    """Returns JSON data for a user's posts"""

    Posts = {"error": "null","data": {"photos":[]},"message":"Success"}

    temp = Photos.query.filter_by(user_id=user_id).all()

    for i in temp:
        Posts["data"]["photos"].append({ "id": i.id,
                                        "user_id": i.user_id,
                                        "caption": i.caption,
                                        "created_on": i.created_on, })
    
    return jsonify(Posts)


@app.route('/api/users/{user_id}/follow', methods=["POST"])
@login_required
def following(user_id):
    if current_user.is_authenticated():
        id = current_user.id
        follow = Follows(id, user_id)
        db.session.add(follow)
        db.session.commit()
        
        #Flash message to indicate a successful following
        success = "You are now following that user"
        return jsonify(message=success), 201
    
    #Flash message to indicate that an error occurred
    failure = "Failed to follow user"
    return jsonify(error=failure)


@app.route('/api/posts', methods=["GET"])
@login_required
def postsPage():
    """Returns JSON data for a user's posts"""

    Posts = {"error": "null","data": {"photos":[]},"message":"Success"}

    temp = Photos.query.all()

    for i in temp:
        Posts["data"]["photos"].append({ "id": i.id,
                                        "user_id": i.user_id,
                                        "caption": i.caption,
                                        "created_on": i.created_on, })
    
    return jsonify(Posts)

###----------------------------------- END OF SPECIFIED API ROUTES ---------------------------------------------###

@app.route('/users/{user_id}', methods=["GET"])
@login_required
def profile():
    """View user profile info as well as all Posts by that user."""
    user = UserProfile.query.filter_by(id=current_user.get_id()).first_or_404()
    return render_template('profile.html', profile=user)


@app.route('/posts/new')
@login_required
def addPostPage(userid):
    """Allow the user to add a new post"""
    return render_template('addPost.html')


###
# The functions below should be applicable to all Flask apps.
###

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d %b %Y'):
    return value.strftime(format)

def validFileExtension(filename):
    """Used during registration to test if the file being uploaded is one of the allowed formats. The formats
       allowed are 'jpg', 'jpeg' and 'png' """
    if filename == "":
        return True

    if len(filename) > 3:
        fileExt = filename[-3:]
        if (fileExt != 'jpg' and fileExt != 'peg' and fileExt != 'png'):
            return False
        return True
    return False

def randomDefaultProfilePic():
    return "default/default-" + str(random.randint(1, 7)) + ".jpg"


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to tell the browser not to cache the rendered page.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
    