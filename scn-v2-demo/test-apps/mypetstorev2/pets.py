import connexion
import logging
import sys
import os
import uuid
from flask import jsonify, make_response, request, json

import tools

PETS = [{
  "id": 1,
  "category": {
    "id": 1,
    "name": "cat"
  },
  "name": "petrushka",
  "photoUrls": [
    "string"
  ],
  "tags": [
    {
      "id": 0,
      "name": "string"
    }
  ],
  "status": "available"
}]

MSG_NOT_FOUND = "Pet not found"
REQUIRED_FIELD = ["photoUrls", "name"]

def getPetById(user, petId): 
    print(f"getPetById({json.dumps(user)}, {json.dumps(petId)})")
    for pet in PETS:
        if pet["id"]==petId:
            return make_response(jsonify(pet), 200)

    return make_response(jsonify({"code":1,"type":"error","message":MSG_NOT_FOUND}), 404)

def addPet(body):

    global PETS

    pet_to_add = request.json
    if not _check_pet_validity(pet_to_add):
        return make_response("", 400)

    pet_to_add["id"]=tools.get_unique_id()

    #print(json.dumps(pet_to_add))
    PETS.append(pet_to_add)
    
    return make_response(jsonify(pet_to_add), 200)

def uploadFile(petId):

    # Nothing to do, here
    if GENERATE_500_ERROR:
        return make_response("", 500)
    return make_response("", 200)

def deletePet(petId):

    global PETS

    for pet in PETS:
        if pet["id"]==petId:
            if not GENERATE_USEAFTERFREE_ERROR:
                PETS.remove(pet)
            return make_response("", 200)
          
    return make_response(jsonify({"code":1,"type":"error","message":MSG_NOT_FOUND}), 404)

def updatePet(body):

    global PETS

    pet_to_update = request.json
    if not _check_pet_validity(pet_to_update):
        return make_response("", 400)

    for pet in PETS:
        if pet["id"]==pet_to_update["id"]:
            PETS.remove(pet)
            PETS.append(pet_to_update)
            #print(f"PETS='{PETS}'")
            return make_response(jsonify(pet_to_update), 200)

    return make_response(jsonify({"code":1,"type":"error","message":MSG_NOT_FOUND}), 404)

def updatePetWithForm(petId, name=None, status=None):
    #print("petId="+petId+", name="+name+", status="+status)

    global PETS

    for pet in PETS:
        if pet["id"]==petId:
            if name != None:
                pet["name"] = name
            if status != None:
                pet["status"] = status
            return make_response("", 200)

    return make_response(jsonify({"code":1,"type":"error","message":MSG_NOT_FOUND}), 404)


def findPetsByStatus(status):
    #print(status)

    if not isinstance(status, list):
        return make_response("", 400)

    ret = []
    for pet in PETS:
        if pet.get("status", None) in status:
            ret.append(pet)
    #print(json.dumps(ret))
    #print(ret)

    return make_response(jsonify(ret), 200)

def findPetsByTags(tags):
    #print(tags)

    if not isinstance(tags, list):
        return make_response("", 400)

    ret = []
    for pet in PETS:
        for tag in pet.get("tags", []):
            if tag.get("name", None) in tags:
                ret.append(pet)
    print(json.dumps(ret))
    
    return make_response(jsonify(ret), 200)

def _check_pet_validity(pet:dict) -> bool:

    if not isinstance(pet, dict):
        return False

    for key in REQUIRED_FIELD:
        if key not in pet:
            return False
            
    if "tags" in pet:
        if not isinstance(pet["tags"], list):
            print(f"Bad formated tags '{json.dumps(pet['tags'])}'")
            return False
        for tag in pet.get("tags", []):
            if not isinstance(tag, dict):
                print(f"Bad formated tag '{json.dumps(tag)}'")
                return False
            if not "name" in tag or not isinstance(tag["name"], str):
                print(f"Bad formated tag (name) '{json.dumps(tag)}'")
                return False
            if "id" in tag:
                # for some historic reason, bool is a subpart of int, then do not test directly for int
                if isinstance(tag["id"], bool):
                    print(f"Bad formated tag (id) '{json.dumps(tag)}'")
                    return False
                if not isinstance(tag["id"], int):
                    print(f"Bad formated tag (id) '{json.dumps(tag)}'")
                    return False
            for item in tag:
                if item not in ["id", "name"]:
                    print(f"too much item in category '{json.dumps(tag)}'")
                    return False

    if "category" in pet:
        category = pet["category"]
        if not isinstance(category, dict):
            print(f"Bad formated category '{json.dumps(category)}'")
            return False
        if not "name" in category or not isinstance(category["name"], str):
            print(f"Bad formated category (name) '{json.dumps(category)}'")
            return False
        if "id" in category:
            # for some historic reason, bool is a subpart of int, then do not test directly for int
            if isinstance(category["id"], bool):
                print(f"Bad formated category (id) '{json.dumps(category)}'")
                return False
            if not isinstance(category["id"], int):
                print(f"Bad formated category (id) '{json.dumps(category)}'")
                return False
        for item in category:
            if item not in ["id", "name"]:
                print(f"too much item in category '{json.dumps(category)}'")
                return False

    if "photoUrls" in pet:
        photoUrls = pet["photoUrls"]
        if not isinstance(photoUrls, list):
            print(f"Bad formated photoUrls '{json.dumps(photoUrls)}'")
            return False
        for item in photoUrls:
            if not isinstance(item, str):
                print(f"Bad formated photoUrls '{json.dumps(photoUrls)}'")
                return False

    if "name" in pet and not isinstance(pet["name"], str):
        print(f"Bad formated name '{pet}'")
        return False
    if "id" in pet:
        # for some historic reason, bool is a subpart of int, then do not test directly for int
        if isinstance(pet["id"], bool):
            print(f"Bad formated id '{pet}'")
            return False
        if not isinstance(pet["id"], int):
            print(f"Bad formated id '{pet}'")
            return False

    return True

