import os
import json
from uuid import uuid4
import flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, UUID
from dotenv import load_dotenv

load_dotenv(verbose=True)
app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URI', '')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class TempResource(db.Model):
  __tablename__ = 'tmp_resources'

  id = db.Column(UUID(as_uuid=True), primary_key=True)
  meta =  db.Column(JSONB)

  def __init__(self, kwargs):
    self.id = kwargs["id"]
    self.meta = kwargs["meta"]

  def __repr__(self):
    return '<id {}>'.format(self.id)

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
      '$validator': '/dcic/signature-commons-schema/v5/core/resource.json',
      'id': self.id,
      # TODO: add context to actual model instead of here
      'meta': self.meta,
    }

class TempLibrary(db.Model):
  __tablename__ = 'tmp_libraries'

  id = db.Column(UUID(as_uuid=True), primary_key=True)
  resource = db.Column(UUID(as_uuid=True), nullable=True)
  dataset = db.Column(db.String())
  dataset_type = db.Column(db.String())
  meta =  db.Column(JSONB)

  def __init__(self, kwargs):
    self.id = kwargs["id"]
    self.resource = kwargs.get("resource")
    self.dataset = kwargs["dataset"]
    self.dataset_type = kwargs["dataset_type"]
    self.meta = kwargs["meta"]
  
  def update(self, kwargs):
    self.id = kwargs["id"]
    self.resource = kwargs.get("resource")
    self.dataset = kwargs["dataset"]
    self.dataset_type = kwargs["dataset_type"]
    self.meta = kwargs["meta"]

  def __repr__(self):
    return '<id {}>'.format(self.id)

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
      '$validator': '/dcic/signature-commons-schema/v5/core/library.json',
      'id': self.id,
      'resource': self.resource,
      'dataset': self.dataset,
      'dataset_type': self.dataset_type,
      'meta': self.meta,
    }

class TempSignature(db.Model):
  __tablename__ = 'tmp_signatures'

  id = db.Column(UUID(as_uuid=True), primary_key=True)
  library = db.Column(UUID(as_uuid=True), nullable=False)
  meta =  db.Column(JSONB)
  
  def __init__(self, kwargs):
    self.id = kwargs["id"]
    self.library = kwargs["library"]
    self.meta = kwargs["meta"]

  def update(self, kwargs):
    self.id = kwargs["id"]
    self.library = kwargs["library"]
    self.meta = kwargs["meta"]

  def __repr__(self):
    return '<id {}>'.format(self.id)

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
      '$validator': '/dcic/signature-commons-schema/v5/core/signature.json',
      'id': self.id,
      'library': self.library,
      'meta': self.meta,
    }

class TempEntity(db.Model):
  __tablename__ = 'tmp_entities'

  id = db.Column(UUID(as_uuid=True), primary_key=True)
  meta =  db.Column(JSONB)
  
  def __init__(self, kwargs):
    self.id = kwargs["id"]
    self.meta = kwargs["meta"]

  def update(self, kwargs):
    self.id = kwargs["id"]
    self.meta = kwargs["meta"]

  def __repr__(self):
    return '<id {}>'.format(self.id)

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
      '$validator': '/dcic/signature-commons-schema/v5/core/entity.json',
      'id': self.id,
      'meta': self.meta,
    }