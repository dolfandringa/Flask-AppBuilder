from nose.tools import eq_
import unittest
import sqlalchemy as sa
import sqlalchemy.ext.declarative
from flask_appbuilder.models.sqla.interface import _is_sqla_type
from flask_appbuilder.models.sqla.interface import SQLAInterface

Base = sqlalchemy.ext.declarative.declarative_base()


rel_table = sa.Table('association', Base.metadata,
                     sa.Column('parent_id', sa.Integer,
                               sa.ForeignKey('parent.id'), nullable=False),
                     sa.Column('neighbour_id', sa.Integer,
                               sa.ForeignKey('neighbour.id'), nullable=False))

class Parent(Base):
    __tablename__ = 'parent'
    id = sa.Column(sa.Integer, primary_key=True)
    favorite_child = sa.orm.relation('FavoriteChild', back_populates='parent',
                                     uselist=False)
    children = sa.orm.relation('Child', back_populates='parent')
    neighbours = sa.orm.relation('Neighbour', secondary=rel_table)


class FavoriteChild(Base):
    __tablename__ = 'favorite_child'
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('parent.id'))
    parent = sa.orm.relation(Parent, back_populates='favorite_child')


class Child(Base):
    __tablename__ = 'child'
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('parent.id'))
    parent = sa.orm.relation(Parent, back_populates='children')

class Neighbour(Base):
    __tablename__ = 'neighbour'
    id = sa.Column(sa.Integer, primary_key=True)
    parents = sa.orm.relation('Parent', secondary=rel_table)

class Headache(Base):
    """Relation without backref or back_populates"""
    __tablename__ = "headache"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('parent.id'))
    parent = sa.orm.relation(Parent)


class CustomSqlaType(sa.types.TypeDecorator):
    impl = sa.types.DateTime(timezone=True)


class NotSqlaType():
    def __init__(self):
        self.impl = sa.types.DateTime(timezone=True)


class FlaskTestCase(unittest.TestCase):
    def test_is_one_to_one(self):
        interf = SQLAInterface(Parent)
        eq_(True, interf.is_relation('favorite_child'))
        eq_(True, interf.is_relation_one_to_one('favorite_child'))
        eq_(False, interf.is_relation_one_to_many('favorite_child'))
        eq_(False, interf.is_relation_many_to_many('favorite_child'))
        eq_(False, interf.is_relation_many_to_one('favorite_child'))
        interf = SQLAInterface(FavoriteChild)
        eq_(True, interf.is_relation('parent'))
        eq_(True, interf.is_relation_one_to_one('parent'))
        eq_(False, interf.is_relation_one_to_many('parent'))
        eq_(False, interf.is_relation_many_to_many('parent'))
        eq_(False, interf.is_relation_many_to_one('parent'))

    def test_is_many_to_many(self):
        interf = SQLAInterface(Parent)
        eq_(True, interf.is_relation('neighbours'))
        eq_(False, interf.is_relation_one_to_many('neighbours'))
        eq_(False, interf.is_relation_one_to_one('neighbours'))
        eq_(False, interf.is_relation_many_to_one('neighbours'))
        eq_(True, interf.is_relation_many_to_many('neighbours'))
        interf = SQLAInterface(Neighbour)
        eq_(True, interf.is_relation('parents'))
        eq_(False, interf.is_relation_one_to_many('parents'))
        eq_(False, interf.is_relation_one_to_one('parents'))
        eq_(False, interf.is_relation_many_to_one('parents'))
        eq_(True, interf.is_relation_many_to_many('parents'))

    def test_is_many_to_one_no_backref(self):
        interf = SQLAInterface(Headache)
        eq_(True, interf.is_relation('parent'))
        eq_(False, interf.is_relation_one_to_many('parent'))
        eq_(False, interf.is_relation_one_to_one('parent'))
        eq_(True, interf.is_relation_many_to_one('parent'))
        eq_(False, interf.is_relation_many_to_many('parent'))

    def test_is_one_to_many(self):
        interf = SQLAInterface(Parent)
        eq_(True, interf.is_relation('children'))
        eq_(True, interf.is_relation_one_to_many('children'))
        eq_(False, interf.is_relation_one_to_one('children'))
        eq_(False, interf.is_relation_many_to_one('children'))
        eq_(False, interf.is_relation_many_to_many('children'))

    def test_is_many_to_one(self):
        interf = SQLAInterface(Child)
        eq_(True, interf.is_relation('parent'))
        eq_(False, interf.is_relation_one_to_many('parent'))
        eq_(False, interf.is_relation_one_to_one('parent'))
        eq_(True, interf.is_relation_many_to_one('parent'))
        eq_(False, interf.is_relation_many_to_many('parent'))

    def test_is_sqla_type(self):
        t1 = sa.types.DateTime(timezone=True)
        t2 = CustomSqlaType()
        t3 = NotSqlaType()
        eq_(True, _is_sqla_type(t1, sa.types.DateTime))
        eq_(True, _is_sqla_type(t2, sa.types.DateTime))
        eq_(False, _is_sqla_type(t3, sa.types.DateTime))
