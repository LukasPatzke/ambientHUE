from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship, backref
from .database import Base


class Status(Base):
    __tablename__ = 'status'

    id = Column(Integer, nullable=False, primary_key=True)
    status = Column(Boolean, nullable=False, default=False)


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, nullable=False, primary_key=True)
    smart_off = Column(Boolean, nullable=False, default=True)


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
association_group_light = Table(
    'association_group_light',
    Base.metadata,
    Column('light_id', Integer, ForeignKey('light.id')),
    Column('group_id', Integer, ForeignKey('group.id'))
)

# Association table for many-to-many relationship light<->webhook
association_light_webhook = Table(
    'association_light_webhook',
    Base.metadata,
    Column('light_id', Integer, ForeignKey('light.id')),
    Column('webhook_id', Integer, ForeignKey('webhook.id'))
)

# Association table for many-to-many relationship group<->webhook
association_group_webhook = Table(
    'association_group_webhook',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('group.id')),
    Column('webhook_id', Integer, ForeignKey('webhook.id'))
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

    smart_off_on = Column(Boolean)
    smart_off_bri = Column(Integer)
    smart_off_ct = Column(Integer)
    smart_off_active = Column(Boolean, default=False)

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

    webhooks = relationship(
        'Webhook',
        back_populates='lights',
        secondary=association_light_webhook
    )


class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)

    lights = relationship(
        'Light',
        secondary=association_group_light
    )

    position = relationship(
        'Position',
        back_populates='group',
        cascade='all,delete',
        uselist=False
    )

    webhooks = relationship(
        'Webhook',
        back_populates='groups',
        secondary=association_group_webhook
    )


class Bridge(Base):
    """ Hue Bridge """
    __tablename__ = 'bridge'

    id = Column(String(16), primary_key=True)
    name = Column(String)
    ipaddress = Column(String, nullable=False)
    username = Column(String)


class Header(Base):
    __tablename__ = 'header'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(String)
    webhook_id = Column(Integer, ForeignKey('webhook.id'))

    webhook = relationship(
        'Webhook',
        back_populates='header'
    )


class Webhook(Base):
    __tablename__ = 'webhook'

    id = Column(Integer, primary_key=True)
    on = Column(Boolean, default=True)
    name = Column(String)
    url = Column(String)
    body = Column(String)
    method = Column(String)

    lights = relationship(
        'Light',
        back_populates='webhooks',
        secondary=association_light_webhook
    )

    groups = relationship(
        'Group',
        back_populates='webhooks',
        secondary=association_group_webhook
    )

    header = relationship(
        'Header',
        back_populates='webhook',
        cascade='all,delete'
    )
