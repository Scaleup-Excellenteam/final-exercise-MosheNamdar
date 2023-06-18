import os

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, sessionmaker, mapped_column
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    email = mapped_column(String(255), unique=True, nullable=False)

    uploads = relationship('Upload', back_populates='user', cascade='all, delete')


class Upload(Base):
    __tablename__ = 'uploads'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid = mapped_column(String(36), default=str(uuid.uuid4()), nullable=False)
    filename = mapped_column(String(255), nullable=False)
    upload_time = mapped_column(DateTime, nullable=False, default=datetime.now)
    finish_time = mapped_column(DateTime)
    status = mapped_column(String(50), nullable=False)
    user_id = mapped_column(Integer, ForeignKey('users.id'), default="none")

    user = relationship('User', back_populates='uploads')

    def upload_path(self) -> str:
        base_dir = 'uploads'
        user_dir = f'user_{self.user_id}'
        return os.path.join(base_dir, user_dir, self.filename)

    def get_error_messages(self) -> str:
        # Assuming you have an error_message column in the uploads table
        return self.error_message

    def set_finish_time(self):
        if self.status == 'done':
            self.finish_time = datetime.now()
        elif self.status == 'failed':
            self.finish_time = None  # If the upload failed, finish_time is reset


# Create the SQLite database file
engine = create_engine('sqlite:///db/database.db')

# Create the tables if they don't exist
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# -------------------------------------------
user_email = input("Enter your email (optional): ").strip()

if user_email:
    # Check if the email already exists in the Users table
    existing_user = session.query(User).filter_by(email=user_email).first()

    if existing_user:
        # User already exists, create an Upload associated with the user
        upload = Upload(filename="a.txt", status="done", user_id=existing_user.id)
        upload.set_finish_time()
    else:
        # User doesn't exist, create a new User and an associated Upload
        new_user = User(email=user_email)
        session.add(new_user)
        session.commit()
        upload = Upload(filename="a.txt", status="done", user_id=new_user.id)
        upload.set_finish_time()

    session.add(upload)
    session.commit()
else:
    # User did not provide an email, create Upload without User
    upload = Upload(filename="a.txt", status="done")
    upload.set_finish_time()
    session.add(upload)
    session.commit()
