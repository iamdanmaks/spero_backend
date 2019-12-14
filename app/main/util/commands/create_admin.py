from app.main import db, flask_bcrypt
from app.main.model.user import User, user_datastore
from app.main.model.role import Role

import uuid
from datetime import datetime


def start_admin_account(
    name, 
    surname, 
    username,
    email,
    password,
    birthday
    ):
    user = User.query.filter_by(email=email).first()
    
    if not user:
        new_user = User(
            first_name=name,
            second_name=surname,
            username=username,
            email=email,
            password=password,
            active=True,
            admin=True,
            date_of_birth=datetime.strptime(birthday, '%d.%m.%Y'),
            public_id=str(uuid.uuid4())
        )
        db.session.add(new_user)
        db.session.commit()
        print('Admin created')

    else:
        print('Such user already exists')
