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

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)

from models import *
app.secret_key = "I LOVE PENN LABS"



@app.route('/api')
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})
    # return jsonify("welcome to the api")


#########################################################################################
################## Routes for USER LIST / FIND USER PAGE ################################
#########################################################################################
# This route returns all users
@app.route('/api/user/', methods=['GET'])
def user_api():
    if request.method == 'GET':
        ls = []
        users = User.query.all()
        for u in users:
            ls.append({'id': u.id, 'email': u.email, 'favorited_clubs': u.clubs})
        return jsonify(ls)

@app.route('/api/user/<name>', methods=['GET'])
def user_search_api(name):
    ls = []
    users = []
    # if nothing is being searched, display all users.
    if not name or len(name) == 0:
        users = User.query.all()
    else:
        users = User.query.filter_by(id=name)
    for u in users:
        ls.append({'id': u.id, 'email': u.email, 'favorited_clubs': u.clubs})
    return jsonify(ls)

# This interacts with the front-end, return html
@app.route('/user', methods=['GET', 'POST'])
def user():
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


#########################################################################################
#################### END OF Routes for USER LIST / FIND USER PAGE  ######################
#########################################################################################



#########################################################################################
##################### ROUTES FOR CLUB LIST / FIND CLUB PAGE / ADD CLUB   ################
#########################################################################################
@app.route('/api/club', methods=['GET', 'POST'], strict_slashes = False)
def club_api():
    # if GET, returns information for every club
    if (request.method == 'GET'):
        clubs = Club.query.all()
        ls = []
        for i in clubs:
            tags = []
            for j in i.tags:
                tags.append(j.id)
            comments = []
            for c in i.comments:
                print(c.id)
                comments.append(c.body + ' - ' + c.user)
            users = []
            for u in i.users:
                users.append(u.id)
            dic = {"club_id": i.id, "name": i.name, "description": i.description, 
                "tags": tags, "favorites": users, "num_favs": len(i.users), "comments": comments}
            ls.append(dic)
        return jsonify(ls)

    else:
        # if not 'email' in session:
        #     return 'access denied, must be logged in'
        req = request.get_json()
        print(req)
        tags = []
        if not Club.query.get(req['code']) == None:
            return jsonify("club already exists")
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
        return "new club: " + req['name'] +  " created"

@app.route('/api/club/<q>', methods=['GET', 'PATCH'])
def club_search_api(q):
    if request.method == 'PATCH':
        id = q
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
            return jsonify(id + " updated")
        else:
            return jsonify("no changes made to " + id)
    else:
        query = q
        clubs = Club.query.all()
        filtered = []
        for i in clubs:
            # lowercasing the letters makes it case-insensitive
            c = i.name.lower()
            if c.find(query.lower()) != -1:
                tags = []
                for j in i.tags:
                    tags.append(j.id)
                comments = []
                for c in i.comments:
                    print(c.id)
                    comments.append(c.body + ' - ' + c.user)
                users = []
                for u in i.users:
                    users.append(u.id)
                dic = {"club_id": i.id, "name": i.name, "description": i.description, 
                    "tags": tags, "favorites": users, "num_favs": len(i.users), "comments": comments}
                filtered.append(dic)

        return jsonify(filtered)


# Interacts with front-end, return html
@app.route('/club', methods=['GET', 'POST'], strict_slashes = False)
def clubs():
    # if GET, returns information for every club
    if (request.method == 'GET'):
        clubs = Club.query.all()
        ls = []
        for i in clubs:
            tags = []
            for j in i.tags:
                tags.append(j.id)
            comments = []
            for c in i.comments:
                print(c.id)
                comments.append(c.body + ' - ' + c.user)
            users = []
            for u in i.users:
                users.append(u.id)
            dic = {"club_id": i.id, "name": i.name, "description": i.description, 
                "tags": tags, "favorites": users, "num_favs": len(i.users), "comments": comments}
            ls.append(dic)
        return render_template('clubs.html', joined=ls)
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

#########################################################################################
################   END OF ROUTES FOR CLUB LIST / FIND CLUB PAGE   #######################
#########################################################################################


#########################################################################################
# Allows users to favorite clubs, each user can only favorite each club once. 
# users that favorite a club are visible on the Club list page.
@app.route('/api/<club>/favorite/<name>', methods=['GET', 'POST'])
def fav_club(club, name):
    if request.method == 'POST' and not 'email' in session:
        return 'access denied, must be logged in'
    club_obj = Club.query.filter_by(id=club).first()
    user_obj = User.query.filter_by(id=name).first()
    if user_obj == None:
        return jsonify("user does not exist")
    if club_obj == None:
        return jsonify("club not found")
    
    users = club_obj.users
    # check if already favorited
    for j in users:
        if j.id == name:
            return jsonify("Already favorited")
    club_obj.users.append(user_obj)
    db.session.commit()
    return jsonify("Favorited")
#########################################################################################


#########################################################################################
# Modifies the specified club if it exists.
# @app.route('/api/clubs/<id>', methods=['PATCH'])
# def modify_club(id):
#     if request.method == 'PATCH' and not 'email' in session:
#         return 'access denied, must be logged in'
#     club_obj = Club.query.get_or_404(id)
#     input = request.get_json()
#     changeMade = False
#     # Checks the input for what is being changed
#     if "name" in input:
#         club_obj.name = input["name"]
#         changeMade = True
#     if "description" in input:
#         club_obj.description = input["description"]
#         changeMade = True
#     if "tags" in input:
#         club_obj.tags = []
#         for i in input["tags"]:
#             if Tag.query.get(i) == None:
#                 newTag = Tag(id=i)
#                 db.session.add(newTag)
#                 db.session.commit
#                 club_obj.tags.append(newTag)
#             else:
#                 club_obj.tags.append(Tag.query.get(i))
#         changeMade = True
#     db.session.commit()
#     if changeMade:
#         return jsonify(id + " updated")
#     else:
#         return jsonify("no changes made to " + id)
#########################################################################################

#########################################################################################
# Returns the number of clubs associated with each tag
@app.route('/api/tag_count')
def tag_cnt_api():
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
def tag_cnt():
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
#########################################################################################


#########################################################################################
# Creates a comment
@app.route('/api/add_comment', methods=['POST'], strict_slashes = False)
def add_comment_api():
    if request.method == 'POST' and not 'email' in session:
        return 'access denied, must be logged in'
    new_comment = Comment(id=str(uuid.uuid4()), body=request.form.get('description'), user=session['email'])
    club = Club.query.filter_by(name=request.form.get('club_name')).first()
    # if not club:
    #     return render_template('add_comment.html')
    club.comments.append(new_comment)
    db.session.add(new_comment)
    db.session.commit()
    return 'comment published'

@app.route('/add_comment', methods=['GET', 'POST'], strict_slashes = False)
def add_comment():
    if request.method == 'POST' and not 'email' in session:
        return 'access denied, must be logged in'
    new_comment = Comment(id=str(uuid.uuid4()), body=request.form.get('description'), user=session['email'])
    club = Club.query.filter_by(name=request.form.get('club_name')).first()
    if not club:
        return render_template('add_comment.html')
    club.comments.append(new_comment)
    db.session.add(new_comment)
    db.session.commit()
    return render_template('add_comment.html')
#########################################################################################


#########################################################################################
################# REGISTER, LOGIN, AND LOGOUT ROUTES ####################################
#########################################################################################
# This route handles registering new account
@app.route("/", methods=['GET', 'POST']) 
def main():
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
        print('in post')
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
#########################################################################################
################# END OF USER AUTH ROUTES ###############################################
#########################################################################################


if __name__ == '__main__':
    app.run()
