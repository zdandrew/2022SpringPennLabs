from flask import Flask, request, jsonify, send_from_directory
from flask import Flask, render_template, url_for, redirect, session
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
import json
from markupsafe import escape
import uuid
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from dataclasses import dataclass
from flask_marshmallow import Marshmallow

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"

db = SQLAlchemy(app)
ma = Marshmallow(app)

from models import *
app.secret_key = "I LOVE PENN LABS"


@app.route('/api')
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})

# Model Schema for Marshmallow (Object Serialization)
class ClubSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Club
    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    tags = ma.auto_field()
    users = ma.auto_field()

    comments = ma.auto_field()

class TagSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Club
    id = ma.auto_field()

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
    id = ma.auto_field()
    email = ma.auto_field()
    clubs = ma.auto_field()
    comments = ma.auto_field()
    

class CommentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Comment
    id = ma.auto_field()
    body = ma.auto_field()
    club = ma.auto_field()
    user = ma.auto_field()


# This route returns all users
@app.route('/api/users/', methods=['GET'])
def get_users_json():
    if request.method == 'GET':
        users = User.query.all()
        user_schema = UserSchema(many=True)
        output = user_schema.dump(users)
        return jsonify({'user': output})

@app.route('/api/user/<name>', methods=['GET'])
def search_user_json(name):
    user = User.query.filter_by(id=name)
    if user.count() == 0:
        return jsonify({'status': '404', 'message': 'user not found'}), 404
    user_schema = UserSchema(many=True)
    output = user_schema.dump(user)
    return jsonify({'user': output})

# This interacts with the front-end, return html
@app.route('/users', methods=['GET', 'POST'])
def users_html():
    if request.method == 'GET':
        users = [];
        users = User.query.all()
        return render_template('find_user.html', joined=users)
    else:
        search = request.form.get('name')
        users = [];
        # if nothing is being searched, display all users.
        if not search or len(search) == 0:
            users = User.query.all()
        else:
            users = User.query.filter_by(id=search)
        return render_template('find_user.html', joined=users)


# Get all clubs
@app.route('/api/clubs', methods=['GET'], strict_slashes = False)
def get_clubs_json():
    clubs = Club.query.all()
    club_schema = ClubSchema(many=True)
    output = club_schema.dump(clubs)
    for o in output:
        o['favorite_user_count'] = len(o['users'])
        o['favorite_users'] = o['users']
        del o['users']
    return jsonify({'clubs': output})

# Create new club
@app.route('/api/club', methods=['POST'], strict_slashes = False)
def post_club_json():
    req = request.get_json()
    tags = []
    if not Club.query.get(req['code']) == None:
        return jsonify({'message': 'club already exists'}), 409
    # creating tags only if it doesn't already exist
    for i in req['tags']:
        tag = Tag.query.get(i)
        if tag != None:
            tags.append(tag)
        else:
            #create new tag
            newTag = Tag(id=i)
            db.session.add(newTag)
            db.session.commit()
            tags.append(newTag)
    db.session.add(Club(id=req['code'], name=req['name'], 
        description=req['description'], tags=tags))
    db.session.commit()
    return jsonify({'message': 'new club created'}), 201

# Get specific club
@app.route('/api/club/<id>', methods=['GET'])
def search_club_json(id):
    query = id
    clubs = Club.query.all()
    filtered = []
    for i in clubs:
        # lowercasing the letters makes it case-insensitive
        c = i.name.lower()
        if c.find(query.lower()) != -1:
            filtered.append(i)
            
    club_schema = ClubSchema(many=True)
    output = club_schema.dump(filtered)
    return jsonify({'club': output})

# Update specific club
@app.route('/api/club/<id>', methods=['PUT'])
def update_club_json(id):
    club_obj = Club.query.get_or_404(id)
    input = request.get_json()
    changeMade = False
    # Checks the input for what is being changed
    if "name" in input:
        club_obj.name = input["name"]
        changeMade = True
    if "description" in input:
        club_obj.description = input["description"]
        changeMade = True
    if "tags" in input:
        club_obj.tags = []
        for i in input["tags"]:
            if Tag.query.get(i) == None:
                newTag = Tag(id=i)
                db.session.add(newTag)
                db.session.commit
                club_obj.tags.append(newTag)
            else:
                club_obj.tags.append(Tag.query.get(i))
        changeMade = True
    db.session.commit()
    if changeMade:
        return jsonify({'message': 'successfully updated'})
    else:
        return jsonify({'message': 'no changes made, invalid/empty payload'}), 400



# Interacts with front-end, return html
@app.route('/clubs', methods=['GET', 'POST'], strict_slashes = False)
def get_clubs_html():
    # if GET, returns information for every club
    if (request.method == 'GET'):
        clubs = Club.query.all()
        club_schema = ClubSchema(many=True)
        output = club_schema.dump(clubs)
        return render_template('clubs.html', joined=output)
    else:
        query = request.form.get('search')
        clubs = Club.query.all()
        if not query or len(query) == 0:
            return render_template('clubs.html', joined=clubs)
        filtered = []
        for i in clubs:
            # lowercasing the letters makes it case-insensitive
            c = i.name.lower()
            if c.find(query.lower()) != -1:
                filtered.append(i)
        return render_template('clubs.html', joined=filtered)


# Allows users to favorite clubs, each user can only favorite each club once. 
# users that favorite a club are visible on the Club list page.
@app.route('/api/favorite/<club>/<name>', methods=['POST'])
def fav_club_json(club, name):
    if request.method == 'POST' and not 'email' in session:
        return jsonify({'message': 'access denied, must be logged in'}), 401
    club_obj = Club.query.filter_by(id=club).first()
    user_obj = User.query.filter_by(id=name).first()
    if user_obj == None:
        return jsonify({'message': 'user does not exist'}), 404
    if club_obj == None:
        return jsonify({'message': 'club not found'}), 404
    
    users = club_obj.users
    # check if already favorited
    for j in users:
        if j.id == name:
            return jsonify({'message': 'Already favorited'}), 409
    club_obj.users.append(user_obj)
    db.session.commit()
    return jsonify({'message': 'Favorited'})


# Returns the number of clubs associated with each tag
@app.route('/api/tag_count')
def get_tag_count_json():
    clubs = Club.query.all()
    tags = {}
    #iterates through all clubs and their tags
    for i in clubs:
        for j in i.tags:
            if j.id not in tags:
                tags[j.id] = 1
            else:
                tags[j.id] += 1
    return jsonify(tags)

@app.route('/tag_count')
def get_tag_cnt_html():
    clubs = Club.query.all()
    tags = {}
    #iterates through all clubs and their tags
    for i in clubs:
        for j in i.tags:
            if j.id not in tags:
                tags[j.id] = 1
            else:
                tags[j.id] += 1
    return render_template('tag_count.html', tags=tags)

# Creates a comment
@app.route('/api/add_comment', methods=['POST'], strict_slashes = False)
def add_comment_json():
    if request.method == 'POST' and not 'email' in session:
        return jsonify({'message': 'access denied, must be logged in'}), 401
    new_comment = Comment(id=str(uuid.uuid4()), body=request.form.get('body'), user=session['email'])
    club = Club.query.filter_by(name=request.form.get('club_name')).first()
    club.comments.append(new_comment)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'message': 'comment published'})

@app.route('/add_comment', methods=['GET', 'POST'], strict_slashes = False)
def add_comment_html():
    if not 'email' in session:
        return 'access denied, must be logged in', 401
    new_comment = Comment(id=str(uuid.uuid4()), body=request.form.get('description'), user=session['email'])
    club = Club.query.filter_by(name=request.form.get('club_name')).first()
    if not club:
        return render_template('add_comment.html'), 404
    club.comments.append(new_comment)
    db.session.add(new_comment)
    db.session.commit()
    return render_template('add_comment.html')



# This route handles registering new account
@app.route("/", methods=['GET', 'POST']) 
def register_account():
    message = ''
    #if method post in index
    print('in the index')
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        print('in the post')
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        #if found in database showcase that it's found 
        user_found = User.query.filter_by(id=user).first()
        email_found = User.query.filter_by(email=email).first()
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            #hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            #insert it in the record collection
            new_user = User(id=user, email=email, password = hashed)
            db.session.add(new_user)
            db.session.commit()
            session["email"] = email
            
            #if registered redirect to logged in as the registered user
            return render_template('logged_in.html', email=email)
    return render_template('index.html')

# Login/logout routes
@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        input_email = request.form.get("email")
        password = request.form.get("password")
        #check if email exists in database
        email_found = User.query.filter_by(email=input_email).first()
        if email_found:
            email_val = email_found.email
            passwordcheck = email_found.password

            #encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')

#autogenerate documentation
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Penn Labs Backend Challenge',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON 
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)
docs.register(api)
docs.register(get_users_json)
docs.register(search_user_json)
docs.register(update_club_json)
docs.register(get_clubs_json)
docs.register(search_club_json)
docs.register(post_club_json)
docs.register(add_comment_json)
docs.register(fav_club_json)
docs.register(get_tag_count_json)


if __name__ == '__main__':
    app.run()
