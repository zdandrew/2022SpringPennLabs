from app import *
from models import *
import bcrypt
import pytest

def test_new_user():
    password = 'pass'
    user = User(id="jj", email='jj@gmail.com', password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))
    assert user.email == 'jj@gmail.com'
    assert user.password != password
    assert bcrypt.checkpw(password.encode('utf-8'), user.password)

def test_new_club():
    tag = Tag(id='undergraduate')
    club = Club(id='petspenn', name='Penn Pets', description='pets!', tags=[tag])
    assert club.id == 'petspenn'
    assert club.name == 'Penn Pets'
    assert club.description == 'pets!'
    assert len(club.tags) == 1
    

def test_new_tag():
    tag = Tag(id='undergraduate')
    assert tag.id == 'undergraduate'

def test_new_comment():
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

def test_clubs_page(client):
    resp = client.get('/clubs')
    assert resp.data != None
    assert resp.status_code == 200