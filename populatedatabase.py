"""
Populate database based on files "roles.csv", "users.csv", "talks.csv" and "registrations.csv"
"""
import os
import csv
from datetime import datetime
from textwrap import dedent

from factory import create_app, db
from models import Talks, User, Role, Registrations

# Create app and DB context
app = create_app()
basedir = os.path.abspath(os.path.dirname(__file__))

# Exception raised when an error occurs
class Error(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return dedent(
            f"""
            {self.message}.
            Sorry, something is wrong!
            """
        )


def create_roles(roles):
    for role in roles:
        new_role = Role(
            name=role["name"],
            can_access_sensitive_information=True if role["can_access_sensitive_information"] == "True" else False,
            can_manage_users=True if role["can_manage_users"] == "True" else False,
            can_manage_talks=True if role["can_manage_talks"] == "True" else False,
            can_create_talks=True if role["can_create_talks"] == "True" else False,
        )
        try:
            db.session.add(new_role)
            db.session.commit()
        except Exception as e:
            print(e)
            raise Error("Error on creating users.")


def create_users(users):
    for user in users:
        new_user = User(
            username=user["username"],
            password=user["password"],
            email=user["email"],
            role=Role.query.filter_by(name=user["role"]).first(),
            birthdate=datetime.fromisoformat(user["birthdate"]),
        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            print(e)
            raise Error("Error on creating users.")


def create_talks(talks):
    for talk in talks:
        starts_at_str = talk["starts_at"].strip()  # remove espaços extras
        starts_at_dt = datetime.fromisoformat(starts_at_str.replace("Z", "+00:00"))
        new_talk = Talks(title=talk["title"], description=talk["description"], speaker_id = talk["speaker_id"], speaker_name=talk["speaker_name"], starts_at = starts_at_dt)
        try:
            db.session.add(new_talk)
            db.session.commit()
        except Exception as e:
            print(e)
            raise Error("Error on creating talks.")
        
def create_registrations(registrations):
    for registration in registrations:
        new_registration = Registrations(user_id=registration["user_id"], talk_id=registration["talk_id"])
        try:
            db.session.add(new_registration)
            db.session.commit()
        except Exception as e:
            print(e)
            raise Error("Error on creating registrations.")


def main():
    resources_dir = os.path.join(basedir, "resources")

    with open(os.path.join(resources_dir, "roles.csv"), "r", encoding="utf-8"
    ) as roles_file, open(os.path.join(resources_dir, "users.csv"), "r", encoding="utf-8"
    ) as users_file, open(os.path.join(resources_dir, "talks.csv"), "r", encoding="utf-8"
    ) as talks_file, open(os.path.join(resources_dir, "registrations.csv"), "r", encoding="utf-8"
    ) as registrations_file, app.app_context():

        roles = csv.DictReader(roles_file)
        users = csv.DictReader(users_file)
        talks = csv.DictReader(talks_file)
        registrations = csv.DictReader(registrations_file)

        create_roles(roles)
        create_users(users)
        create_talks(talks)
        create_registrations(registrations)


if __name__ in "__main__":
    main()
