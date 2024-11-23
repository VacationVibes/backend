import uuid
from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, ForeignKey, CheckConstraint, TIMESTAMP, func, \
    PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class UserModel(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)  # bcrypt hash

    reactions = relationship('PlaceReactionModel', back_populates='user', lazy='dynamic')

    def __repr__(self):
        return f"<UserModel(id='{self.id}', name='{self.name}', email='{self.email}')>"


class PlaceTypeModel(Base):
    __tablename__ = 'place_type'
    place_id = Column(UUID(as_uuid=True), ForeignKey('place.id', ondelete='CASCADE'), nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    places = relationship('PlaceModel', back_populates='types', lazy='joined')

    __table_args__ = (
        PrimaryKeyConstraint('place_id', 'type'),
    )


class PlaceImageModel(Base):
    __tablename__ = 'place_image'
    place_id = Column(UUID(as_uuid=True), ForeignKey('place.id', ondelete='CASCADE'), nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    places = relationship('PlaceModel', back_populates='images', lazy='joined')

    __table_args__ = (
        PrimaryKeyConstraint('place_id', 'image_url'),
    )


class PlaceModel(Base):
    __tablename__ = 'place'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(String, nullable=False)
    latitude = Column(DECIMAL(10, 9), nullable=False)
    longitude = Column(DECIMAL(10, 9), nullable=False)
    name = Column(String, nullable=False)
    rating = Column(DECIMAL(2, 2), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    reactions = relationship('PlaceReactionModel', back_populates='place', lazy='dynamic')
    images = relationship('PlaceImageModel', back_populates='places', lazy='joined')
    types = relationship('PlaceTypeModel', back_populates='places', lazy='joined')

    def __repr__(self):
        return f"<PlaceModel(id='{self.id}', place_id='{self.place_id}', latitude='{self.latitude}', longitude='{self.longitude}', created_at='{self.created_at}')>"


class PlaceReactionModel(Base):
    __tablename__ = 'place_reaction'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(UUID(as_uuid=True), ForeignKey('place.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    reaction = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    place = relationship('PlaceModel', back_populates='reactions', lazy='joined')
    user = relationship('UserModel', back_populates='reactions', lazy='joined')

    __table_args__ = (
        CheckConstraint(reaction.in_(['like', 'dislike']), name='reaction_check'),
    )

    def __repr__(self):
        return f"<PlaceReactionModel(id='{self.id}', place_id='{self.place_id}', reaction='{self.reaction}', created_at='{self.created_at}')>"
