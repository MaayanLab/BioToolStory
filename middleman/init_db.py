from app.tempmodels import db

# drop database if it exists
db.drop_all()
# create database from models
db.create_all()