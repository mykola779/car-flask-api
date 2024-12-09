from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    new_user = User(username="username", password=generate_password_hash("password"))
    db.session.add(new_user)
    db.session.commit()
    print("User created successfully!")


# If we have error user not found use this code (python seed.py) after that you can use login and logout