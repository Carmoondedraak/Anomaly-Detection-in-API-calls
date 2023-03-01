(function (){
  'use strict';

  var async     = require("async")
    , express   = require("express")
    , request   = require("request")
    , endpoints = require("../endpoints")
    , helpers   = require("../../helpers")
    , app       = express()

  app.get("/orders", function (req, res, next) {
    console.log("##########=START=########");
    console.log("GET:/orders");
    console.log("Request: " + JSON.stringify(req.body));
    console.log("Response: " + JSON.stringify(res.body));
    console.log("#########=END=#########");
    var logged_in = req.cookies.logged_in;
    if (!logged_in) {
      throw new Error("User not logged in.");
      return
    }

    var custId = req.session.customerId;

    async.waterfall([
        function (callback) {

          var options = {
              uri: endpoints.ordersUrl + "/orders/search/customerId?sort=date&custId=" + custId,
                  method: 'GET',
                  headers: {
                        'Authorization':'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZXhwIjo5OTk5OTk5OTk5OSwicGFzc3dvcmQiOiJibGEifQ.zueOSw5L53D7thIuYWz5P5-zgAzBQ4L8bCSiGZrF-yRx4cJawwiJKjVjjetfzf1a'
                    }
            };
          request(options, function (error, response, body) {
            if (error) {
              return callback(error);
            }
                console.log("#########=START=#########");
                console.log("GET:" +endpoints.ordersUrl + "/orders/search/customerId?sort=date&custId=" + custId);
                console.log("Request: " + JSON.stringify(req.body));
                console.log("Options: " + JSON.stringify(options));
                console.log("Response: " + JSON.stringify(response.body));
                console.log("#########=END=#########");
            if (response.statusCode == 404) {
              console.log("No orders found for user: " + custId);
              return callback(null, []);
            }
            callback(null, JSON.parse(body)._embedded.customerOrders);
          });
        }
    ],
    function (err, result) {
      if (err) {
        return next(err);
      }
      helpers.respondStatusBody(res, 201, JSON.stringify(result));
    });
  });

  app.get("/orders/*", function (req, res, next) {
    var url = endpoints.ordersUrl + req.url.toString();
        console.log("#########=START=#########");
        console.log("GET:" +url);
        console.log("Request: " + JSON.stringify(req.body));
        console.log("Response: " + JSON.stringify(res.body));
        console.log("#########=END=#########");
    request.get(url).pipe(res);
  });

  app.post("/orders", function(req, res, next) {
        console.log("#########=START=#########");
        console.log("POST:/orders");
        console.log("Request: " + JSON.stringify(req.body));
        console.log("Response: " + JSON.stringify(res.body));
        console.log("#########=END=#########");
    var logged_in = req.cookies.logged_in;
    if (!logged_in) {
      throw new Error("User not logged in.");
      return
    }

    var custId = req.session.customerId;

    async.waterfall([
        function (callback) {

        request(endpoints.customersUrl + "/" + custId, function (error, response, body) {
        console.log("##########=START=########");
        console.log("??:/orders"+endpoints.customersUrl + "/" + custId);
        console.log("Body: " + JSON.stringify(body));
        console.log("Response: " + JSON.stringify(response));
        console.log("#########=END=#########");
            if (error || body.status_code === 500) {
              console.log(error)
              callback(error);
              return;
            }
            var jsonBody = JSON.parse(body);
            var customerlink = jsonBody._links.customer.href;
            var addressLink = jsonBody._links.addresses.href;
            var cardLink = jsonBody._links.cards.href;
            var order = {
              "customer": customerlink,
              "address": null,
              "card": null,
              "items": endpoints.cartsUrl + "/" + custId + "/items"
            };
            callback(null, order, addressLink, cardLink);
          });
        },
        function (order, addressLink, cardLink, callback) {
          async.parallel([
              function (callback) {
                request.get(addressLink, function (error, response, body) {
                    console.log("#########=START=#########");
                    console.log("GET:/"+addressLink);
                    console.log("Body: " + JSON.stringify(body));
                    console.log("Response: " + JSON.stringify(response));
                    console.log("#########=END=#########");
                  if (error) {
                    callback(error);
                    console.log(error)
                    return;
                  }
                  var jsonBody = JSON.parse(body);
                  if (jsonBody.status_code !== 500 && jsonBody._embedded.address[0] != null) {
                    order.address = jsonBody._embedded.address[0]._links.self.href;
                  }
                  callback();
                });
              },
              function (callback) {
                request.get(cardLink, function (error, response, body) {
                    console.log("#########=START=#########");
                    console.log("GET:/"+cardLink);
                    console.log("Body: " + JSON.stringify(body));
                    console.log("Response: " + JSON.stringify(response));
                    console.log("#########=END=#########");
                  if (error) {
                    console.log(error)
                    callback(error);
                    return;
                  }
                  var jsonBody = JSON.parse(body);
                  if (jsonBody.status_code !== 500 && jsonBody._embedded.card[0] != null) {
                    order.card = jsonBody._embedded.card[0]._links.self.href;
                  }
                  callback();
                });
              }
          ], function (err, result) {
            if (err) {
              callback(err);
              return;
            }
            console.log(result);
            callback(null, order);
          });
        },
        function (order, callback) {
          var options = {
            uri: endpoints.ordersUrl + '/orders',
            method: 'POST',
            json: true,
            body: order,
            headers: {
                'password': 'password',
                'x-internal-ip-server': '128.9.8.4'
            }
          };
                console.log("##########=START POST TO ORDER=########");
                console.log("POST:/"+endpoints.ordersUrl + '/orders');
                console.log("Options: " + JSON.stringify(options));
                console.log("##########=END POST TO ORDER=########");
          request(options, function (error, response, body) {
            if (error) {
              console.log("!!!!!!!!ERROR:", error);
              return callback(error);
            }
            callback(null, response.statusCode, body);
          });
        }
    ],
    function (err, status, result) {
      if (err) {
        return next(err);
      }
      helpers.respondStatusBody(res, status, JSON.stringify(result));
    });
  });

  module.exports = app;
}());
