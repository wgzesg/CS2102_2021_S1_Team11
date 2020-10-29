from __init__ import db, login_manager
from flask_user import UserMixin
from flask_sqlalchemy import SQLAlchemy

@login_manager.user_loader
def load_user(contact):
    us = Users.query.filter_by(contact=contact).first()
    return us

class Users(db.Model, UserMixin):
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    contact = db.Column(db.Integer, primary_key=True)
    usertype = db.Column(db.String, nullable=True)
    card = db.Column(db.String)
    isparttime = db.Column(db.Boolean)
    postalcode = db.Column(db.String)
    
    biddingccontact = db.relationship('Biddings', backref='contact')
    cantakecareccontact = db.relationship('Cantakecare', backref='contact')
    pet = db.relationship('Pets', backref='owner')
    
    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
    backref=db.backref('users', lazy='dynamic'))
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.contact
    
class Role(db.Model):
    
    name = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    #userrole = db.relationship('UserRoles', backref='userroletype')
    
    
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    contact = db.Column(db.Integer, db.ForeignKey('users.contact', ondelete='CASCADE'), primary_key=True, nullable=False)
    usertype = db.Column(db.String, db.ForeignKey('role.name', ondelete='CASCADE'), nullable=False)
    
    userrolecontact = db.relationship('Users', foreign_keys=[contact])
    userrolerole = db.relationship('Role', foreign_keys=[usertype])


class categories(db.Model, UserMixin):
    category = db.Column(db.String, primary_key=True, nullable=False)
    petcat = db.relationship('Pets', backref='type')
    cantakecarecat = db.relationship('Cantakecare', backref='type')
    
class Pets(db.Model, UserMixin):
    petname = db.Column(db.String, primary_key=True, nullable=False)
    pcontact = db.Column(db.Integer, db.ForeignKey('users.contact'), primary_key=True, nullable=False)
    category = db.Column(db.String, db.ForeignKey('categories.category'), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    # biddingpetname = db.relationship('Biddings', backref='pet')
    # biddingpcontact = db.relationship('Biddings', primaryjoin="Pets.pcontact==Biddings.pcontact")
    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return (self.pcontact, self.petname)
    
class Available(db.Model, UserMixin):
    startday = db.Column(db.Date, primary_key=True, nullable=False)
    endday = db.Column(db.Date, primary_key=True, nullable=False)
    ccontact = db.Column(db.Integer, primary_key=True, nullable=False)
    
    def get_key(self):
        return (self.startday, self.endday, self.ccontact)

class Biddings(db.Model, UserMixin):
    petname = db.Column(db.String, db.ForeignKey('pets.petname'), primary_key=True, nullable=False)
    pcontact = db.Column(db.Integer, db.ForeignKey('pets.pcontact'), primary_key=True, nullable=False)
    ccontact = db.Column(db.Integer, db.ForeignKey('users.contact'), primary_key=True, nullable=False)
    startday = db.Column(db.Date, primary_key=True, nullable=False)
    endday = db.Column(db.Date, primary_key=True, nullable=False)
    paymentmode = db.Column(db.String, nullable=False)
    deliverymode = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    
    pcontactrel = db.relationship("Pets", foreign_keys=[pcontact])
    petnamerel = db.relationship("Pets", foreign_keys=[petname])
    
    # reviewpetname = db.relationship('Reviews', backref='pet')
    # reviewpcontact = db.relationship('Reviews', backref='petonwercontact')
    # reviewccontact = db.relationship('Reviews', backref='caretakercontact')
    # reviewstartdate = db.relationship('Reviews', backref='start')
    # reviewenddate = db.relationship('Reviews', backref='end')
    
    def get_status(self):
        return self.status

    def get_key(self):
        return (self.startday, self.endday, self.ccontact, self.petname, self.pcontact)
    
class Reviews(db.Model, UserMixin):
    petname = db.Column(db.String, db.ForeignKey('biddings.petname'), primary_key=True, nullable=False)
    pcontact = db.Column(db.Integer, db.ForeignKey('biddings.pcontact'), primary_key=True, nullable=False)
    ccontact = db.Column(db.Integer, db.ForeignKey('biddings.ccontact'), primary_key=True, nullable=False)
    startday = db.Column(db.Date, db.ForeignKey('biddings.startday'), primary_key=True, nullable=False)
    endday = db.Column(db.Date, db.ForeignKey('biddings.endday'), primary_key=True, nullable=False)
    rating = db.Column(db.Integer, primary_key=True, nullable=False)
    review = db.Column(db.String, primary_key=True, nullable=False)
    
    reviewpetname = db.relationship('Biddings', foreign_keys=[petname])
    reviewpcontact = db.relationship('Biddings', foreign_keys=[pcontact])
    reviewccontact = db.relationship('Biddings', foreign_keys=[ccontact])
    reviewstartdate = db.relationship('Biddings', foreign_keys=[startday])
    reviewenddate = db.relationship('Biddings', foreign_keys=[endday])
    def get_rating(self):
        return self.rating
 
    def get_key(self):
        return (self.startday, self.endday, self.ccontact, self.petname, self.pcontact, self.rating, self.review)
    
class Cantakecare(db.Model, UserMixin):
    ccontact = db.Column(db.Integer, db.ForeignKey('users.contact'), primary_key=True, nullable=False)
    category = db.Column(db.String, db.ForeignKey('categories.category'), primary_key=True, nullable=False)
    dailyprice = db.Column(db.Integer, nullable=False)
    def get_dailyprice(self):
        return self.dailyprice
    
    def get_key(self):
        return (self.ccontact, self.category)