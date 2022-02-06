from app import *
from models import *
import bcrypt

def test_new_user():
    password = 'pass'
    user = User(id="jj", email='jj@gmail.com', password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))
    assert user.email == 'jj@gmail.com'
    assert user.password != password

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
