from app import db

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/


tags = db.Table('tags',
    db.Column('tag_id', db.String(100), db.ForeignKey('tag.id'), primary_key=True),
    db.Column('club_id', db.String(100), db.ForeignKey('club.id'), primary_key=True)
)

users = db.Table('users',
    db.Column('club_id', db.String(100), db.ForeignKey('club.id'), primary_key=True),
    db.Column('user_id', db.String(100), db.ForeignKey('user.id'), primary_key=True)
)

# Remove this bcause comment and user is many to one relationship
# comments = db.Table('comments',
#     db.Column('comment_id', db.String(100), db.ForeignKey('comment.id'), primary_key=True),
#     db.Column('club_id', db.String(100), db.ForeignKey('club.id'), primary_key=True)
# )


class Club(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(500), unique=False, nullable=False)
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
        backref=db.backref('tag_clubs', lazy=True))
    users = db.relationship('User', secondary=users, lazy='subquery',
        back_populates='clubs')
    comments = db.relationship('Comment', backref='Club')

    def __repr__(self):
        return '<Club %r>' % self.name

class Tag(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    def __repr__(self):
        return '<Tag %r>' % self.id

class User(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=True)
    clubs = db.relationship('Club', secondary=users, lazy='subquery',
        back_populates='users')
    comments = db.relationship('Comment', backref='User')
    def __repr__(self):
        return '<User %r>' % self.id

class Comment(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    body = db.Column(db.String(500), unique=False, nullable=False)
    club = db.Column(db.String(100), db.ForeignKey(Club.id))
    user = db.Column(db.String(100), db.ForeignKey(User.email))