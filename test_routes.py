from app import *
from models import *
import bcrypt
import pytest


def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password are defined correctly
    """
    password = 'pass'
    user = User(id="jj", email='jj@gmail.com', password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))
    assert user.email == 'jj@gmail.com'
    assert user.password != password
    assert bcrypt.checkpw(password.encode('utf-8'), user.password)

def test_new_club():
    """
    GIVEN a Club and Tag model
    WHEN a new Club is created
    THEN check the id, name, description, and tags are defined correctly
    """
    tag = Tag(id='incredible')
    club = Club(id='petspenn', name='Penn Pets', description='pets!', tags=[tag])
    assert club.id == 'petspenn'
    assert club.name == 'Penn Pets'
    assert club.description == 'pets!'
    assert len(club.tags) == 1
    

def test_new_tag():
    """
    GIVEN a Tag model
    WHEN a new Tag is created
    THEN check the id is defined correctly
    """
    tag = Tag(id='woww')
    assert tag.id == 'woww'

def test_new_comment():
    """
    GIVEN a Comment model
    WHEN a new Comment is created
    THEN check the body, club, user are defined correctly
    """
    password = 'pass'
    user = User(id="jj", email='jj@gmail.com', password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))
    club = Club(id='petspenn', name='Penn Pets', description='pets!')
    comment = Comment(id=1, body='test comment', club=club.id, user=user.email)
    assert comment.body == 'test comment'
    assert comment.club == 'petspenn'
    assert comment.user == 'jj@gmail.com'


@pytest.fixture
def client():
    app.config.update({'TESTING': True})
    with app.test_client() as client:
        yield client


def test_clubs(client):
    """
    GIVEN a Flask App
    WHEN the '/api/clubs/' is requested (GET)
    THEN check that the response is valid and clubs are returned
    """
    resp = client.get('/api/clubs/')
    assert resp.status_code == 200
    assert b'locustlabs' in resp.data

def test_search_club(client):
    """
    GIVEN a Flask App
    WHEN the '/api/club/meme' is requested (GET)
    THEN check that the response is valid and specific clubs are returned
    """
    resp = client.get('/api/club/meme')
    assert resp.status_code == 200
    assert b'meme' in resp.data

def test_users(client):
    """
    GIVEN a Flask App
    WHEN the '/api/users/' is requested (GET)
    THEN check that the response is valid and users are returned
    """
    resp = client.get('/api/users/')
    assert resp.status_code == 200
    assert b'josh' in resp.data


def test_search_user(client):
    """
    GIVEN a Flask App
    WHEN the '/api/user/josh' is requested (GET)
    THEN check that the response is valid and specific user is returned
    """
    resp = client.get('/api/user/josh')
    assert resp.status_code == 200
    assert b'josh' in resp.data

def test_post_club(client):
    """
    GIVEN a Flask App
    WHEN the '/api/club' is requested (POST)
    THEN check that the response is valid and club is created
    """
    resp = client.post('api/club', json={'name': 'test_name', 'description': 'test_des!', 'code': 'test_id', 'tags':[]})
    assert resp.status_code == 201
    resp2 = client.get('/api/clubs/')
    assert b'test_id' in resp2.data
    db.session.delete(Club.query.filter_by(id='test_id').one())
    db.session.commit()

def test_put_club(client):
    """
    GIVEN a Flask App
    WHEN the '/api/club' is requested (PUT)
    THEN check that the response is valid and club is updated
    """
    resp = client.post('api/club', json={'name': 'test_name', 'description': 'test_des!', 'code': 'test_id', 'tags':[]})
    assert resp.status_code == 201
    resp2 = client.get('/api/clubs/')
    assert b'test_id' in resp2.data
    resp3 = client.put('api/club/test_id', json={'name': 'test_name_mod', 'description': 'test_name_mod', 'tags':[]})
    resp4 = client.get('/api/clubs/')
    assert b'test_name_mod' in resp4.data
    db.session.delete(Club.query.filter_by(id='test_id').one())
    db.session.commit()

def test_fav_club_not_logged_in(client):
    """
    GIVEN a Flask App
    WHEN the '/api/favorite/Locust Labs/josh' is requested (POST) and not logged in
    THEN check that the response 401
    """
    resp = client.post('/api/favorite/Locust Labs/josh')
    assert resp.status_code == 401

def test_fav_club(client):
    """
    GIVEN a Flask App
    WHEN the '/api/favorite/Locust Labs/josh' is requested (POST) and logged in
    THEN check that the response 200 if successful, 409 if already faved
    """
    resp = client.post('api/club', json={'name': 'test_name', 'description': 'test_des!', 'code': 'test_id', 'tags':[]})
    login = client.post('/api/login', json={'email': 'josh@gmail.com', 'password': 'test'})
    assert login.status_code == 200
    resp = client.post('/api/favorite/test_id/josh')
    assert resp.status_code == 200
    resp2 = client.post('/api/favorite/test_id/josh')
    assert resp2.status_code == 409
    db.session.delete(Club.query.filter_by(id='test_id').one())
    db.session.commit()
    client.post('/logout')


def test_login_logout(client):
    """
    GIVEN a Flask App
    WHEN the '/api/login' and '/logout' is requested 
    THEN check that both are successful
    """
    login = client.post('/api/login', json={'email': 'josh@gmail.com', 'password': 'test'})
    assert login.status_code == 200
    logout = client.post('/logout')
    assert logout.status_code == 200

def test_add_get_comment(client):
    login = client.post('/api/login', json={'email': 'josh@gmail.com', 'password': 'test'})
    comment = client.post('/api/add_comment', json={"body": "test_comm", "email": "josh@gmail.com", "club_name": "Penn Memes Club"})
    assert comment.status_code == 200
    get_comm = client.get('/api/comments/')
    assert b'test_comm' in get_comm.data

