from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

groups = db.Table('groups',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.id'), primary_key=True)
)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    address = db.Column(db.String(250), unique=False, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    groups = db.relationship('Group', secondary=groups, lazy='subquery',
        backref=db.backref('contacts', lazy=True))
    
    def __repr__(self):
        return u'%s'% self.name
    
    def to_dict(self):
        groups = []
        for group in self.groups:
            groups.append(group.id)
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'groups': groups
        }
        
    def to_dict_detailed(self):
        groups = []
        for group in self.groups:
            groups.append(group.list_details())
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'groups': groups
        }
        
    def list_details(self):
        return {
            'id': self.id,
            'name': self.name
        }
    
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    
    def to_dict(self):
        contacts = []
        for c in self.contacts:
            contacts.append(c.id)
        return {
            'id': self.id,
            'name': self.name,
            'contacts': contacts
        }
    
    def to_dict_detailed(self):
        contacts = []
        for c in self.contacts:
            contacts.append(c.list_details())
        return {
            'id': self.id,
            'name': self.name,
            'contacts': contacts
        }
    
    def list_details(self):
        return {
            'id': self.id,
            'name': self.name
        }