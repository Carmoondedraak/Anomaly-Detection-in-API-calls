import connexion
import logging
import sys
import os
import uuid
from copy import copy
from flask import jsonify, make_response, request, json

import tools
from main import GENERATE_BOLA_ERROR

"""
    "Order": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64"
            },
            "petId": {
                "type": "integer",
                "format": "int64"
            },
            "quantity": {
                "type": "integer",
                "format": "int32"
            },
            "shipDate": {
                "type": "string",
                "format": "date-time"
            },
            "status": {
                "type": "string",
                "description": "Order Status",
                "enum": [
                    "placed",
                    "approved",
                    "delivered"
                ]
          },
          "complete": {
              "type": "boolean"
          }
      },
"""
STORE = []

MSG_NOT_FOUND = "Order not found"
REQUIRED_FIELD = ["petId", "quantity", "status", "complete"]

def getInventory():
    ret = {"placed": 0, "approved": 0, "delivered": 0}
    for order in STORE:
        if order.get("status", None) in ret:
            ret[order.get("status", None)] += 1
    return make_response(jsonify(ret), 200)

def placeOrder(user, body):
    global STORE

    order_to_add = request.json
    # test for validity (seems not done by flask...)
    if not _check_order_validity(order_to_add):
        return make_response("", 400)

    order_to_add["id"] = int(tools.get_unique_id()/1000)
    order_to_add["uid"] = user

    STORE.append(order_to_add) 
    #print(f"STORE: {json.dumps(STORE)}")

    # return the order without uid
    order_without_uid = copy(order_to_add)
    order_without_uid.pop('uid')
    return make_response(jsonify(order_without_uid), 200)

def getOrderById(user, orderId):

    #print(f"STORE: {json.dumps(STORE)}")
    for order in STORE:
        if order["id"]==orderId:
            if order["uid"]==user or GENERATE_BOLA_ERROR:
                order_without_uid = copy(order)
                order_without_uid.pop('uid')
                return make_response(jsonify(order_without_uid), 200)
            else:
                return make_response("", 403)
    return make_response(jsonify({"code":1,"type":"error","message":MSG_NOT_FOUND}), 404)

def deleteOrder(user, orderId):
    global STORE
    
    for order in STORE:
        #print(f"order: {order}")
        if order["id"]==orderId:
            if order["uid"]==user or GENERATE_BOLA_ERROR:
                STORE.remove(order)
                return make_response("", 200)
            else:
                return make_response("", 403)
          
    return make_response(jsonify({"code":1,"type":"error","message":MSG_NOT_FOUND}), 404)

def _check_order_validity(order:dict) -> bool:

    if not isinstance(order, dict):
        return False

    for key in REQUIRED_FIELD:
        if key not in order:
            return False
    return True
