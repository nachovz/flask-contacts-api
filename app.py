import os
import sqlalchemy
from flask import Flask, jsonify, request
from models import db, Contact, Group
from flask_swagger import swagger
from flask_cors import CORS
from flask_migrate import Migrate

app = Flask(__name__)
##Setting the place for the db to run
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Initializing the db (after registering the Models)
db.init_app(app)
#migration engine
migrate = Migrate(app, db)
#Enabling CORS
CORS(app)
    
@app.route('/')
def hello():
  """
    Contact API doc
    ---
    definitions:
      - schema:
          id: Contact
          required:
            - email
            - name
            - phone
            - address
          properties:
            name:
             type: string
             description: the contact's name
            email:
             type: string
             description: the contact's email address
             unique: true
            address:
             type: string
             description: the contact's physical address
            phone:
             type: string
             description: he contact's phone number
             unique: true
  """
  swag = swagger(app)
  swag['info']['version'] = "1.0"
  swag['info']['title'] = "Contact API"
  #Showing some swagger
  return jsonify(swag)

# GET ALL
@app.route('/contact/all', methods=['GET'])
def allUsers():
  """
    Get the list of contacts
    ---
    responses:
      200:
        description: Contact created
        schema:
         type: array
         items:
          schema:
           id: Contact
      500:
        description: Server error
  """
  contacts = Contact.query.all()
  resp = []
  for u in contacts:
    resp.append(u.to_dict())
    print resp
  return jsonify(resp)

# GET SPECIFIC
@app.route('/contact/<int:id>', methods=['GET', 'PUT'])
def getContact(id):
  """
    Retrieve a specific contact
    ---
    parameters:
      - in: url
        type: int
    responses:
      200:
        schema:
         id: Contact
      400:
        description: Missing information
    """
  if request.method == 'GET':
    try:
      contact = Contact.query.filter_by(id=id).first()
      return jsonify(contact.to_dict_detailed())
    except Exception as e:
      return jsonify({ "response": "%s" % e})
  else:
    try:
      contact = Contact.query.filter_by(id=id).first()
      info = request.get_json() or {}
      for g in info["groups"]:
        group = Group.query.get(g)
        contact.groups.append(group)
      db.session.commit()
      resp =  jsonify({"response": "Contact updated", "data": contact.to_dict()})
      resp.status_code = 201
      return resp
    except Exception as e:
      return jsonify({ "response": "%s" % e})

# PUT NEW CONTACT
@app.route('/contact', methods=['POST'])
def add():
  """
    Create a new contact
    Endpoint for creating a new contact.
    ---
    parameters:
      - in: body
        name: body
        schema:
         id: Contact
    responses:
      201:
        description: Contact created
      400:
        description: Missing information
    """
  newContact = request.get_json() or {}
  try:
    #validations
    c = Contact(
      name=newContact["name"], 
      email=newContact["email"], 
      phone=newContact["phone"],
      address=newContact["address"]
      )
    db.session.add(c)
    db.session.commit()
    resp =  jsonify({"response": "Contact created"})
    resp.status_code = 201
    return resp
  except Exception as e:
    resp = jsonify({"response":'%s' % e})
    resp.status_code = 400
    return resp

# POST (Update) CONTACT


@app.route('/group', methods=['POST'])
def addGroup():
  newGroup = request.get_json() or {}
  try:
    g = Group(name=newGroup["name"])
    db.session.add(g)
    db.session.commit()
    resp =  jsonify({"response": "Group created"})
    resp.status_code = 201
    return resp
  except Exception as e:
    resp = jsonify({"response":'%s' % e})
    resp.status_code = 400
    return resp

@app.route('/group/all', methods=['GET'])
def allGroups():
  """
    Get the list of groups
    ---
    responses:
      200:
        description: Contact created
        schema:
         type: array
         items:
          schema:
           id: Group
      500:
        description: Server error
  """
  groups = Group.query.all()
  resp = []
  for g in groups:
      resp.append(g.to_dict())
    
  return jsonify(resp)

@app.route('/group/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def getGroup(id):
  """
    Retrieve a specific group
    ---
    parameters:
      - in: url
        type: int
    responses:
      200:
        schema:
         id: Group
      400:
        description: Missing information
    """
  try:
    group = Group.query.filter_by(id=id).first()
    if request.method == 'GET':
      return jsonify(group.to_dict_detailed())
    elif request.method == 'PUT':
      info = request.get_json() or {}
      group.name = info["name"]
      db.session.commit()
      resp =  jsonify({"response": "Group updated", "data": group.to_dict()})
      resp.status_code = 201
      return resp
    else:
      db.session.delete(group)
      db.session.commit()
      resp =  jsonify({"response": "Group deleted", "data": group.to_dict()})
      resp.status_code = 201
      return resp
  except Exception as e:
      return jsonify({ "response": "%s" % e})


app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))