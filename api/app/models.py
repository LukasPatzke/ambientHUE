from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    ForeignKey,
    Table
)
from sqlalchemy.orm import relationship, backref
from .database import Base


class Status(Base):
    """ General app settings"""
    __tablename__ = 'status'

    id = Column(Integer, nullable=False, primary_key=True)
    status = Column(Boolean, nullable=False, default=False)


class Curve(Base):
    __tablename__ = 'curve'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    kind = Column(String(50), nullable=False)
    default = Column(Boolean, nullable=False, default=False)
    offset = Column(Float, nullable=False, default=0)

    points = relationship(
        'Point',
        back_populates='curve',
        cascade='all,delete',
        order_by='Point.x'
    )


class Point(Base):
    """ A point of the color temperature curve """
    __tablename__ = 'point'

    id = Column(Integer, primary_key=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    first = Column(Boolean, default=False)
    last = Column(Boolean, default=False)

    curve_id = Column(Integer, ForeignKey('curve.id'), nullable=False)

    curve = relationship('Curve', back_populates='points')


class Position(Base):
    """ Home Screen Position"""
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False, default=9999)
    visible = Column(Boolean, default=False)
    light_id = Column(String, ForeignKey('light.id'))
    group_id = Column(String, ForeignKey('group.id'))

    light = relationship('Light', back_populates='position')
    group = relationship('Group', back_populates='position')


# Association table for many-to-many relationship group<->light
association_table = Table(
    'association',
    Base.metadata,
    Column('light_id', Integer, ForeignKey('light.id')),
    Column('group_id', Integer, ForeignKey('group.id'))
)


class Light(Base):
    """ A single Light """
    __tablename__ = 'light'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    modelid = Column(String)
    manufacturername = Column(String)
    productname = Column(String)
    on = Column(Boolean, default=False)
    on_controlled = Column(Boolean, default=False)
    on_threshold = Column(Float, default=0)
    bri_controlled = Column(Boolean, default=False)
    bri_max = Column(Float, default=254)
    ct_controlled = Column(Boolean, default=False)

    bri_curve_id = Column(Integer, ForeignKey('curve.id'))
    ct_curve_id = Column(Integer, ForeignKey('curve.id'))

    bri_curve = relationship(
        'Curve',
        backref=backref('bri_lights'),
        foreign_keys=[bri_curve_id]
    )
    ct_curve = relationship(
        'Curve',
        backref=backref('ct_lights'),
        foreign_keys=[ct_curve_id]
    )

    position = relationship(
        'Position',
        back_populates='light',
        cascade='all,delete',
        uselist=False
    )


class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)

    lights = relationship(
        'Light',
        secondary=association_table
    )

    position = relationship(
        'Position',
        back_populates='group',
        cascade='all,delete',
        uselist=False
    )


class Bridge(Base):
    """ Hue Bridge """
    __tablename__ = 'bridge'

    id = Column(String(16), primary_key=True)
    name = Column(String)
    ipaddress = Column(String, nullable=False)
    username = Column(String)
