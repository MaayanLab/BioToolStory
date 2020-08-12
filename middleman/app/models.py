import json
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, UUID

db = SQLAlchemy()

class Resource(db.Model):
  __tablename__ = 'tmp_resources'

  id = db.Column(UUID(as_uuid=True), primary_key=True)
  meta =  db.Column(JSONB)
  libraries = db.relationship('Library', backref='resource', lazy=True)

  def __init__(self, meta, uuid):
    self.id = uuid
    self.meta = meta

  def __repr__(self):
    return '<id {}>'.format(self.uuid)

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
      '$validator': '/dcic/signature-commons-schema/v5/core/resource.json',
      'id': self.id,
      # TODO: add context to actual model instead of here
      'meta': self.meta,
      'libraries': [library.serialize() for library in self.libraries],
    }

class Library(db.Model):
  __tablename__ = 'tmp_libraries'

  id = db.Column(UUID(as_uuid=True), primary_key=True)
  resource = db.Column(UUID(as_uuid=True), db.ForeignKey('resources.uuid'), nullable=False)
  dataset = db.Column(db.String())
  dataset_type = db.Column(db.String())
  meta =  db.Column(JSONB)
  signatures = db.relationship('Signature', backref='library', lazy=True)

  def __init__(self, meta, uuid):
    self.id = uuid
    self.meta = meta

  def __repr__(self):
    return '<id {}>'.format(self.uuid)

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
      'signatures': [signature.serialize() for signature in self.signatures],
    }

class Signature(db.Model):
  __tablename__ = 'tmp_signatures'

  id = db.Column(UUID(as_uuid=True), primary_key=True)
  library = db.Column(UUID(as_uuid=True), db.ForeignKey('libraries.uuid'), nullable=False)
  meta =  db.Column(JSONB)
  
  def __init__(self, meta, uuid):
    self.id = uuid
    self.meta = meta

  def __repr__(self):
    return '<id {}>'.format(self.uuid)

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
      '$validator': '/dcic/signature-commons-schema/v5/core/signature.json',
      'id': self.id,
      'library': self.library,
      'meta': self.meta,
    }

class Entity(db.Model):
  __tablename__ = 'tmp_entities'

  id = db.Column(UUID(as_uuid=True), primary_key=True)
  meta =  db.Column(JSONB)
  
  def __init__(self, meta, uuid):
    self.id = uuid
    self.meta = meta

  def __repr__(self):
    return '<id {}>'.format(self.uuid)

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
      '$validator': '/dcic/signature-commons-schema/v5/core/entity.json',
      'id': self.id,
      'meta': self.meta,
    }