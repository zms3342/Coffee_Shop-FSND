import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, true'
    header['Access-Control-Allow-Methods'] = 'POST,GET,PUT,DELETE,PATCH,OPTIONS'
    return response

# db_drop_and_create_all()




@app.route("/drinks", methods=['GET'])
def get_drinks(): 
    try:
        drinks = list(map(Drink.short, Drink.query.all()))
        return jsonify({
            "success": True,
            "drinks": drinks
        })
        
    except: abort(400)



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_details(jwt):
    drinks = Drink.query.all()
    if len(drinks)==0: 
        abort(400)
    details =[drink.long() for drink in drinks]
    return jsonify({
        "success":True, 
        "drink-details":details
    })





'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['POST'])
@requires_auth("post:drinks")
def add_drink(jwt): 

    body = request.get_json() 
    if body.get('title') is None:
        abort(400)

    drink = Drink(
        title=body.get('title'),
        recipe=json.dumps(body.get('recipe'))
        )
    drink.insert()
    new_drink = Drink.query.filter_by(id=drink.id).first()

    return jsonify({
        "success":True, 
        "drinks":[new_drink.long()],
    }),201



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt,id):
    body =request.get_json()
    drink = Drink.query.filter(Drink.id == id).one()
    if drink is None:
        abort(404)
    drink.title = body.get("title")
    drink.recipe = json.dumps(body.get("recipe"))
    drink.update()

    return jsonify({
        'success':True, 
        'new_drink':[drink.long()]
    
    })
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt,id):
    try: 
        drink = Drink.query.filter(Drink.id == id).one()
        drink.delete()
        return jsonify({
            'success':True,
            'drink': drink.id
        }),200
    except: 
        abort(404)
    

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Not Found"
                    },404)

@app.errorhandler(401)
def auth_error(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "Authorization error "
                    },401)


