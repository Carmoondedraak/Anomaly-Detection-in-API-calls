import connexion
import logging
import sys
import os
import uuid
from flask import jsonify, make_response, request, json

import tools
from main import GENERATE_BOLA_ERROR

USERS = [
    {
        "id": 100,
        "username": "the_last_toto",
        "firstName": "toto",
        "lastName": "the last",
        "email": "toto@gmail.com",
        "password": "*********",
        "phone": "",
        "userStatus": 1
    },{
        "id": 101,
        "username": "user_read_only",
        "firstName": "user1",
        "lastName": "firstname1",
        "email": "user1@gmail.com",
        "password": "*********",
        "phone": "",
        "userStatus": 1
    },{
        "id": 102,
        "username": "user_read_only",
        "firstName": "user1",
        "lastName": "firstname1",
        "email": "user1@gmail.com",
        "password": "*********",
        "phone": "",
        "userStatus": 1
    }
]

MSG_NOT_FOUND = "User not found"
REQUIRED_FIELD = ["username", "email", "password"]

def createUser(body):
    global USERS

    user_to_add = request.json
    print(f"User to add: {json.dumps(user_to_add)}")
    if not _check_user_validity(user_to_add):
        return make_response("", 400)

    # it's an user creation, then override any provided id, or create it
    user_to_add["id"]=tools.get_unique_id()
            
    USERS.append(user_to_add)
    return make_response(jsonify(user_to_add), 200)

def getUserByName(username):

    for user in USERS:
        if user["username"]==username:
            return make_response(jsonify(user), 200)

    return make_response(jsonify({"code":1,"type":"error","message":MSG_NOT_FOUND}), 404)

def updateUser(username, body):
    global USERS

    user_to_update = request.json
    if not _check_user_validity(user_to_update, test_username_unicity=False):
        return make_response("", 400)

    for user in USERS:
        if user["username"]==username:
            USERS.remove(user)
            USERS.append(user_to_update)
            return make_response(jsonify(user_to_update), 200)

    return make_response(jsonify({"code":1,"type":"error","message":MSG_NOT_FOUND}), 404)

def deleteUser(username): 
    global USERS

    for user in USERS:
        if user["username"]==username:
            USERS.remove(user)
            return make_response("", 200)

    return make_response(jsonify({"code":1,"type":"error","message":MSG_NOT_FOUND}), 404)

def createUsersWithListInput(body):
    global USERS

    users_to_add = request.json
    if not isinstance(users_to_add, list):
        return make_response("", 400)
    print(json.dumps(users_to_add))

    for user_to_add in users_to_add:
        print(f"User to add: {json.dumps(user_to_add)}")
        if not _check_user_validity(user_to_add):
            return make_response("", 400)

        # it's an user creation, then override any provided id, or create it
        user_to_add["id"]=tools.get_unique_id()
        USERS.append(user_to_add)

    return make_response("", 200)
    
def createUsersWithArrayInput(body):
    global USERS

    users_to_add = request.json
    if not isinstance(users_to_add, list):
        return make_response("", 400)
    #print(json.dumps(users_to_add))

    for user_to_add in users_to_add:
        print(f"User to add: {json.dumps(user_to_add)}")
        if not _check_user_validity(user_to_add):
            return make_response("", 400)

        # it's an user creation, then override any provided id, or create it
        user_to_add["id"]=tools.get_unique_id()
        USERS.append(user_to_add)

    return make_response("", 200)

def loginUser(username, password):
    return make_response("", 200)

def logoutUser():
    return make_response("", 200)

def _check_user_validity(user:dict, test_username_unicity:bool=True) -> bool:

    if not isinstance(user, dict):
        return False

    # Check for required field
    for key in REQUIRED_FIELD:
        if key not in user:
            return False

    if test_username_unicity:
        # Check for username unicity
        for existing_user in USERS:
            if user["username"]==existing_user["username"]:
                return False

    return True
