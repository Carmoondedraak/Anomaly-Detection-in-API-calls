#!/usr/bin/env bash

set -x 

apiID=$1
apiclarity="${UPSTREAM_TELEMETRY_HOST_NAME:-localhost}:8080"
telemetry="${UPSTREAM_TELEMETRY_HOST_NAME:-localhost}:9000"
#apiclarity="${UPSTREAM_TELEMETRY_HOST_NAME:-apiclarity-apiclarity.apiclarity:8080}"
#telemetry="${UPSTREAM_TELEMETRY_HOST_NAME:-apiclarity-apiclarity.apiclarity:9000}"

epoch_millis() {
	echo "$(date +%s)000"
}

# We need to create at least one trace to create the API entry
 curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<END_OF_TRACE
 {
   "requestID": "req-id",
   "scheme": "http",
   "destinationAddress": "32.45.66.51:8000",
   "destinationNamespace": "XXXDESTNAMESPACEXXX",
   "sourceAddress": "10.116.207.197:8000",
   "request": {
     "method": "GET",
     "path": "/pet/000000000010",
     "host": "petstore.com",
     "common": {
       "version": "1",
       "time": $(epoch_millis),
       "headers": [
         {
           "key": "authorization",
           "value": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjowfQ.i6i-xl0NxSyZBWVm-KFlqLN70w-QfRro5X2c1oTxSxfs_3OROBGdywHZMtgSpl2M"
         }
       ],
       "body": "",
       "TruncatedBody": false
     }
   },
   "response": {
     "statusCode": "200",
     "common": {
       "time": $(epoch_millis),
       "version": "1",
       "headers": null,
       "body": "eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=",
       "TruncatedBody": false
     }
   }
 }
END_OF_TRACE

curl -X PUT --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${apiclarity}/api/apiInventory/${apiID}/specs/providedSpec <<'END_OF_SPEC'
{"rawSpec":"swagger: '2.0'\ninfo:\n  description: >-\n    This is a sample server Petstore server.  You can find out more about\n    Swagger at [http://swagger.io](http://swagger.io) or on [irc.freenode.net,\n    #swagger](http://swagger.io/irc/).  For this sample, you can use the api key\n    `special-key` to test the authorization filters.\n  version: 1.0.6\n  title: Swagger Petstore\n  termsOfService: http://swagger.io/terms/\n  contact:\n    email: apiteam@swagger.io\n  license:\n    name: Apache 2.0\n    url: http://www.apache.org/licenses/LICENSE-2.0.html\nhost: petstore.swagger.io\nbasePath: /v2\ntags:\n  - name: pet\n    description: Everything about your Pets\n    externalDocs:\n      description: Find out more\n      url: http://swagger.io\n  - name: store\n    description: Access to Petstore orders\n  - name: user\n    description: Operations about user\n    externalDocs:\n      description: Find out more about our store\n      url: http://swagger.io\nschemes:\n  - https\n  - http\npaths:\n  /pet/{petId}/uploadImage:\n    post:\n      tags:\n        - pet\n      summary: uploads an image\n      description: ''\n      operationId: uploadFile\n      consumes:\n        - multipart/form-data\n      produces:\n        - application/json\n      parameters:\n        - name: petId\n          in: path\n          description: ID of pet to update\n          required: true\n          type: integer\n          format: int64\n        - name: additionalMetadata\n          in: formData\n          description: Additional data to pass to server\n          required: false\n          type: string\n        - name: file\n          in: formData\n          description: file to upload\n          required: false\n          type: file\n      responses:\n        '200':\n          description: successful operation\n          schema:\n            $ref: '#/definitions/ApiResponse'\n      security:\n        - petstore_auth:\n            - write:pets\n            - read:pets\n  /pet:\n    post:\n      tags:\n        - pet\n      summary: Add a new pet to the store\n      description: ''\n      operationId: addPet\n      consumes:\n        - application/json\n        - application/xml\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - in: body\n          name: body\n          description: Pet object that needs to be added to the store\n          required: true\n          schema:\n            $ref: '#/definitions/Pet'\n      responses:\n        '405':\n          description: Invalid input\n      security:\n        - petstore_auth:\n            - write:pets\n            - read:pets\n    put:\n      tags:\n        - pet\n      summary: Update an existing pet\n      description: ''\n      operationId: updatePet\n      consumes:\n        - application/json\n        - application/xml\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - in: body\n          name: body\n          description: Pet object that needs to be added to the store\n          required: true\n          schema:\n            $ref: '#/definitions/Pet'\n      responses:\n        '400':\n          description: Invalid ID supplied\n        '404':\n          description: Pet not found\n        '405':\n          description: Validation exception\n      security:\n        - petstore_auth:\n            - write:pets\n            - read:pets\n  /pet/findByStatus:\n    get:\n      tags:\n        - pet\n      summary: Finds Pets by status\n      description: Multiple status values can be provided with comma separated strings\n      operationId: findPetsByStatus\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: status\n          in: query\n          description: Status values that need to be considered for filter\n          required: true\n          type: array\n          items:\n            type: string\n            enum:\n              - available\n              - pending\n              - sold\n            default: available\n          collectionFormat: multi\n      responses:\n        '200':\n          description: successful operation\n          schema:\n            type: array\n            items:\n              $ref: '#/definitions/Pet'\n        '400':\n          description: Invalid status value\n      security:\n        - petstore_auth:\n            - write:pets\n            - read:pets\n  /pet/findByTags:\n    get:\n      tags:\n        - pet\n      summary: Finds Pets by tags\n      description: >-\n        Multiple tags can be provided with comma separated strings. Use tag1,\n        tag2, tag3 for testing.\n      operationId: findPetsByTags\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: tags\n          in: query\n          description: Tags to filter by\n          required: true\n          type: array\n          items:\n            type: string\n          collectionFormat: multi\n      responses:\n        '200':\n          description: successful operation\n          schema:\n            type: array\n            items:\n              $ref: '#/definitions/Pet'\n        '400':\n          description: Invalid tag value\n      security:\n        - petstore_auth:\n            - write:pets\n            - read:pets\n      deprecated: true\n  /pet/{petId}:\n    get:\n      tags:\n        - pet\n      summary: Find pet by ID\n      description: Returns a single pet\n      operationId: getPetById\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: petId\n          in: path\n          description: ID of pet to return\n          required: true\n          type: integer\n          format: int64\n      responses:\n        '200':\n          description: successful operation\n          schema:\n            $ref: '#/definitions/Pet'\n        '400':\n          description: Invalid ID supplied\n        '404':\n          description: Pet not found\n      security:\n        - api_key: []\n    post:\n      tags:\n        - pet\n      summary: Updates a pet in the store with form data\n      description: ''\n      operationId: updatePetWithForm\n      consumes:\n        - application/x-www-form-urlencoded\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: petId\n          in: path\n          description: ID of pet that needs to be updated\n          required: true\n          type: integer\n          format: int64\n        - name: name\n          in: formData\n          description: Updated name of the pet\n          required: false\n          type: string\n        - name: status\n          in: formData\n          description: Updated status of the pet\n          required: false\n          type: string\n      responses:\n        '405':\n          description: Invalid input\n      security:\n        - petstore_auth:\n            - write:pets\n            - read:pets\n    delete:\n      tags:\n        - pet\n      summary: Deletes a pet\n      description: ''\n      operationId: deletePet\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: api_key\n          in: header\n          required: false\n          type: string\n        - name: petId\n          in: path\n          description: Pet id to delete\n          required: true\n          type: integer\n          format: int64\n      responses:\n        '400':\n          description: Invalid ID supplied\n        '404':\n          description: Pet not found\n      security:\n        - petstore_auth:\n            - write:pets\n            - read:pets\n  /store/order:\n    post:\n      tags:\n        - store\n      summary: Place an order for a pet\n      description: ''\n      operationId: placeOrder\n      consumes:\n        - application/json\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - in: body\n          name: body\n          description: order placed for purchasing the pet\n          required: true\n          schema:\n            $ref: '#/definitions/Order'\n      responses:\n        '200':\n          description: successful operation\n          schema:\n            $ref: '#/definitions/Order'\n        '400':\n          description: Invalid Order\n  /store/order/{orderId}:\n    get:\n      tags:\n        - store\n      summary: Find purchase order by ID\n      description: >-\n        For valid response try integer IDs with value >= 1 and <= 10. Other\n        values will generated exceptions\n      operationId: getOrderById\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: orderId\n          in: path\n          description: ID of pet that needs to be fetched\n          required: true\n          type: integer\n          maximum: 10\n          minimum: 1\n          format: int64\n      responses:\n        '200':\n          description: successful operation\n          schema:\n            $ref: '#/definitions/Order'\n        '400':\n          description: Invalid ID supplied\n        '404':\n          description: Order not found\n    delete:\n      tags:\n        - store\n      summary: Delete purchase order by ID\n      description: >-\n        For valid response try integer IDs with positive integer value. Negative\n        or non-integer values will generate API errors\n      operationId: deleteOrder\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: orderId\n          in: path\n          description: ID of the order that needs to be deleted\n          required: true\n          type: integer\n          minimum: 1\n          format: int64\n      responses:\n        '400':\n          description: Invalid ID supplied\n        '404':\n          description: Order not found\n  /store/inventory:\n    get:\n      tags:\n        - store\n      summary: Returns pet inventories by status\n      description: Returns a map of status codes to quantities\n      operationId: getInventory\n      produces:\n        - application/json\n      parameters: []\n      responses:\n        '200':\n          description: successful operation\n          schema:\n            type: object\n            additionalProperties:\n              type: integer\n              format: int32\n      security:\n        - api_key: []\n  /user/createWithArray:\n    post:\n      tags:\n        - user\n      summary: Creates list of users with given input array\n      description: ''\n      operationId: createUsersWithArrayInput\n      consumes:\n        - application/json\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - in: body\n          name: body\n          description: List of user object\n          required: true\n          schema:\n            type: array\n            items:\n              $ref: '#/definitions/User'\n      responses:\n        default:\n          description: successful operation\n  /user/createWithList:\n    post:\n      tags:\n        - user\n      summary: Creates list of users with given input array\n      description: ''\n      operationId: createUsersWithListInput\n      consumes:\n        - application/json\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - in: body\n          name: body\n          description: List of user object\n          required: true\n          schema:\n            type: array\n            items:\n              $ref: '#/definitions/User'\n      responses:\n        default:\n          description: successful operation\n  /user/{username}:\n    get:\n      tags:\n        - user\n      summary: Get user by user name\n      description: ''\n      operationId: getUserByName\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: username\n          in: path\n          description: 'The name that needs to be fetched. Use user1 for testing. '\n          required: true\n          type: string\n      responses:\n        '200':\n          description: successful operation\n          schema:\n            $ref: '#/definitions/User'\n        '400':\n          description: Invalid username supplied\n        '404':\n          description: User not found\n    put:\n      tags:\n        - user\n      summary: Updated user\n      description: This can only be done by the logged in user.\n      operationId: updateUser\n      consumes:\n        - application/json\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: username\n          in: path\n          description: name that need to be updated\n          required: true\n          type: string\n        - in: body\n          name: body\n          description: Updated user object\n          required: true\n          schema:\n            $ref: '#/definitions/User'\n      responses:\n        '400':\n          description: Invalid user supplied\n        '404':\n          description: User not found\n    delete:\n      tags:\n        - user\n      summary: Delete user\n      description: This can only be done by the logged in user.\n      operationId: deleteUser\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: username\n          in: path\n          description: The name that needs to be deleted\n          required: true\n          type: string\n      responses:\n        '400':\n          description: Invalid username supplied\n        '404':\n          description: User not found\n  /user/login:\n    get:\n      tags:\n        - user\n      summary: Logs user into the system\n      description: ''\n      operationId: loginUser\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - name: username\n          in: query\n          description: The user name for login\n          required: true\n          type: string\n        - name: password\n          in: query\n          description: The password for login in clear text\n          required: true\n          type: string\n      responses:\n        '200':\n          description: successful operation\n          headers:\n            X-Expires-After:\n              type: string\n              format: date-time\n              description: date in UTC when token expires\n            X-Rate-Limit:\n              type: integer\n              format: int32\n              description: calls per hour allowed by the user\n          schema:\n            type: string\n        '400':\n          description: Invalid username/password supplied\n  /user/logout:\n    get:\n      tags:\n        - user\n      summary: Logs out current logged in user session\n      description: ''\n      operationId: logoutUser\n      produces:\n        - application/json\n        - application/xml\n      parameters: []\n      responses:\n        default:\n          description: successful operation\n  /user:\n    post:\n      tags:\n        - user\n      summary: Create user\n      description: This can only be done by the logged in user.\n      operationId: createUser\n      consumes:\n        - application/json\n      produces:\n        - application/json\n        - application/xml\n      parameters:\n        - in: body\n          name: body\n          description: Created user object\n          required: true\n          schema:\n            $ref: '#/definitions/User'\n      responses:\n        default:\n          description: successful operation\nsecurityDefinitions:\n  api_key:\n    type: apiKey\n    name: api_key\n    in: header\n  petstore_auth:\n    type: oauth2\n    authorizationUrl: https://petstore.swagger.io/oauth/authorize\n    flow: implicit\n    scopes:\n      read:pets: read your pets\n      write:pets: modify pets in your account\ndefinitions:\n  ApiResponse:\n    type: object\n    properties:\n      code:\n        type: integer\n        format: int32\n      type:\n        type: string\n      message:\n        type: string\n  Category:\n    type: object\n    properties:\n      id:\n        type: integer\n        format: int64\n      name:\n        type: string\n    xml:\n      name: Category\n  Pet:\n    type: object\n    required:\n      - name\n      - photoUrls\n    properties:\n      id:\n        type: integer\n        format: int64\n      category:\n        $ref: '#/definitions/Category'\n      name:\n        type: string\n        example: doggie\n      photoUrls:\n        type: array\n        xml:\n          wrapped: true\n        items:\n          type: string\n          xml:\n            name: photoUrl\n      tags:\n        type: array\n        xml:\n          wrapped: true\n        items:\n          xml:\n            name: tag\n          $ref: '#/definitions/Tag'\n      status:\n        type: string\n        description: pet status in the store\n        enum:\n          - available\n          - pending\n          - sold\n    xml:\n      name: Pet\n  Tag:\n    type: object\n    properties:\n      id:\n        type: integer\n        format: int64\n      name:\n        type: string\n    xml:\n      name: Tag\n  Order:\n    type: object\n    properties:\n      id:\n        type: integer\n        format: int64\n      petId:\n        type: integer\n        format: int64\n      quantity:\n        type: integer\n        format: int32\n      shipDate:\n        type: string\n        format: date-time\n      status:\n        type: string\n        description: Order Status\n        enum:\n          - placed\n          - approved\n          - delivered\n      complete:\n        type: boolean\n    xml:\n      name: Order\n  User:\n    type: object\n    properties:\n      id:\n        type: integer\n        format: int64\n      username:\n        type: string\n      firstName:\n        type: string\n      lastName:\n        type: string\n      email:\n        type: string\n      password:\n        type: string\n      phone:\n        type: string\n      userStatus:\n        type: integer\n        format: int32\n        description: User Status\n    xml:\n      name: User\nexternalDocs:\n  description: Find out more about Swagger\n  url: http://swagger.io\n"}
END_OF_SPEC

# ------------ NLID
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":null,"sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/pet/99874","host":"petstore.com","common":{"time": $(epoch_millis),"version":"1","headers":[],"body":"eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":null,"sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/user/pedro","host":"petstore.com","common":{"time": $(epoch_millis),"version":"1","headers":[],"body":"eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

for i in {000000000000001..20}
do
    curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<END_OF_TRACE
 {
   "requestID": "bla",
   "scheme": "http",
   "destinationAddress": "32.45.66.51:8000",
   "destinationNamespace": "XXXDESTNAMESPACEXXX",
   "sourceAddress": "10.116.207.197:8000",
   "request": {
     "method": "GET",
     "path": "/pet/0000000000${i}",
     "host": "petstore.com",
     "common": {
       "version": "1",
       "time": $(epoch_millis),
       "headers": [
       ],
       "body": "",
       "TruncatedBody": false
     }
   },
   "response": {
     "statusCode": "200",
     "common": {
       "time": $(epoch_millis),
       "version": "1",
       "headers": null,
       "body": "eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=",
       "TruncatedBody": false
     }
   }
 }
END_OF_TRACE
done

#### Weak Basic Auth, SHORT and KNOWN password
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
 {"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakbasicauth/SHORT_AND_KNOWN","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Basic dXNlcjE6cmFiYml0"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### Weak Basic Auth, KNOWN password
 curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
 {"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakbasicauth/KNOWN","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Basic dXNlcjE6bG9uZ2xvbmdsb25n"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### Weak Basic Auth, SAME password
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakbasicauth/SAME","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Basic dXNlcjE6cGFzc3dvcmRtb3JldGhhbjg="}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakbasicauth/SAME","host":"traceanalyzer2.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Basic dXNlcjE6cGFzc3dvcmRtb3JldGhhbjg="}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakbasicauth/SAME","host":"traceanalyzer3.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Basic dXNlcjE6cGFzc3dvcmRtb3JldGhhbjg="}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### JWT_NO_EXPIRE_CLAIM
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakjwt/NO_EXPIRE_CLAIM","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.Q6CM1qIz2WTgTlhMzpFL8jI8xbu9FFfj5DY_bGVY98Y"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### JWT_SENSITIVE_CONTENT_IN_CLAIMS
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakjwt/JWT_SENSITIVE_CONTENT_IN_CLAIMS","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjowLCJwYXNzd29yZCI6ImJsYSJ9.HoI84Px0J9oVujFgBvY42PF9xaBz0xCDJzuono4qo40"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### JWT_NO_ALG_FIELD
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakjwt/JWT_NO_ALG_FIELD","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJ0eXAiOiJKV1QifQ.eyJsb2dnZWRJbkFzIjoiYWRtaW4iLCJpYXQiOjE0MjI3Nzk2Mzh9.HoI84Px0J9oVujFgBvY42PF9xaBz0xCDJzuono4qo40"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### JWT_SENSITIVE_CONTENT_IN_CLAIMS
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakjwt/JWT_SENSITIVE_CONTENT_IN_CLAIMS","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJ0eXAiOiJKV1QifQ.eyJsb2dnZWRJbkFzIjoiYWRtaW4iLCJpYXQiOjE0MjI3Nzk2Mzh9.HoI84Px0J9oVujFgBvY42PF9xaBz0xCDJzuono4qo40Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzc24iOiI5OTk5IiwiaXAiOiIxOTIuMS4xLjEiLCJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.bySqmwlwljWpXLWZ4jlkb_ST3VtuPK2Sui79jkGUEIE"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### JWT_SENSITIVE_CONTENT_IN_HEADERS_AND_CLAIMS
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakjwt/JWT_SENSITIVE_CONTENT_IN_HEADERS_AND_CLAIMS","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImNvdmlkX3Bvc2l0aXZlIjp0cnVlfQ.eyJzc24iOiI5OTk5IiwiaXAiOiIxOTIuMS4xLjEiLCJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.kiDLC2Kl-3diNJ_8k-LAdQpNjWmPzmJ1YXvh-p2J9T4"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### JWT_WEAK_SYMETRIC_SECRET, JWT_NOT_RECOMMENDED_ALG
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakjwt/JWT_WEAK_SYMETRIC_SECRET_JWT_NOT_RECOMMENDED_ALG", "host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjowfQ.uzPFbqIJ2akC2gmGxN3KlXU_zhMFvE__N5kKwejY19reMaDaaDT21hmy1mMCZZY2"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### JWT_WEAK_SYMETRIC_SECRET_JWT_EXP_TOO_FAR
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakjwt/JWT_WEAK_SYMETRIC_SECRET_JWT_EXP_TOO_FAR", "host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZXhwIjo5OTk5OTk5OTk5fQ.X5NwJulKmNzdC2vW9J1UOMsaKikgzQbmFBWslfDNqZE"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### JWT_WEAK_SYMETRIC_SECRET_JWT_SENSITIVE_CONTENT_IN_CLAIMS_JWT_NOT_RECOMMENDED_ALG_JWT_EXP_TOO_FAR
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakjwt/JWT_WEAK_SYMETRIC_SECRET_JWT_SENSITIVE_CONTENT_IN_CLAIMS_JWT_NOT_RECOMMENDED_ALG_JWT_EXP_TOO_FAR", "host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZXhwIjo5OTk5OTk5OTk5OSwicGFzc3dvcmQiOiJibGEifQ.tCIFaW7882WmxIGednahpwN-1jEqOkkwgS0W1x5F35psVTACPcpbPw-P8K9CfQM3"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT


#### JWT_WEAK_SYMETRIC_SECRET_JWT_SENSITIVE_CONTENT_IN_CLAIMS_JWT_EXP_TOO_FAR
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/weakjwt/JWT_WEAK_SYMETRIC_SECRET_JWT_SENSITIVE_CONTENT_IN_CLAIMS_JWT_EXP_TOO_FAR", "host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZXhwIjo5OTk5OTk5OTk5OSwicGFzc3dvcmQiOiJibGFibHUifQ.SLWwRavOnos1ihyRJUPeG3xjKRy8eIBvUOD6VqW20WU"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### REGEXP_MATCHING_REQUEST_HEADERS
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/sensitive/REGEXP_MATCHING_REQUEST_HEADERS","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key": "api-key", "value":"bla"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### REGEXP_MATCHING_RESPONSE_HEADERS
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/sensitive/REGEXP_MATCHING_RESPONSE_HEADERS","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": [{"key": "username", "value":"testuser"}], "body": "", "TruncatedBody": false}}}
EOT

#### REGEXP_MATCHING_REQUEST_BODY
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/sensitive/REGEXP_MATCHING_REQUEST_BODY","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[],"body":"eyJ1c2VybmFtZSI6ICJ0ZXN0fQ==","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": [], "body": "", "TruncatedBody": false}}}
EOT

#### REGEXP_MATCHING_RESPONSE_BODY
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/sensitive/REGEXP_MATCHING_RESPONSE_BODY","host":"traceanalyzer.test.example.com","common":{"version":"","time": $(epoch_millis),"headers":[],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": [], "body": "eyJ1c2VybmFtZSI6ICJ0ZXN0fQ==", "TruncatedBody": false}}}
EOT

curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/pet/321654","host":"petstore.com","common":{"version":"","time": $(epoch_millis),"headers":[],"body":"eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":null,"sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/user/john","host":"petstore.com","common":{"version":null,"time": $(epoch_millis),"headers":[],"body":"eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":null,"sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/store/order/20","host":"petstore.com","common":{"version":null,"time": $(epoch_millis),"headers":[],"body":"eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":null,"sourceAddress":"10.116.207.197:8000","request":{"method":"DELETE","path":"/pet/65321","host":"petstore.com","common":{"version":null,"time": $(epoch_millis),"headers":[],"body":"eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":null,"sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/user/21654","host":"petstore.com","common":{"version":null,"time": $(epoch_millis),"headers":[],"body":"eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":null,"sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/pet/10231/name","host":"petstore.com","common":{"version":null,"time": $(epoch_millis),"headers":[],"body":"eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":null,"sourceAddress":"10.116.207.197:8000","request":{"method":"PUT","path":"/users/john","host":"petstore.com","common":{"version":null,"time": $(epoch_millis),"headers":[],"body":"eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT


curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":null,"sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/carts/99874","host":"petstore.com","common":{"time": $(epoch_millis),"version":"1","headers":[],"body":"eyJjdnNzIjpbeyJzY29yZSI6Ny44LCJ2ZWN0b3IiOiJBVjpML0FDOkwvUFI6Ti9VSTpSL1M6VS9DOkgvSTpIL0E6SCJ9XX0=","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT

#### JWT_WEAK_SYMETRIC_SECRET_JWT_SENSITIVE_CONTENT_IN_CLAIMS_JWT_EXP_TOO_FAR
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/pet/99874", "host":"petstore.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZXhwIjo5OTk5OTk5OTk5OSwicGFzc3dvcmQiOiJibGFibHUifQ.SLWwRavOnos1ihyRJUPeG3xjKRy8eIBvUOD6VqW20WU"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT
curl -X POST --data-binary @- -H 'Content-Type: application/json' -H 'Accept: application/json' ${telemetry}/api/telemetry <<EOT
{"requestID":"req-id","scheme":"http","destinationAddress":"32.45.66.51:8000","destinationNamespace":"","sourceAddress":"10.116.207.197:8000","request":{"method":"GET","path":"/user/john", "host":"petstore.com","common":{"version":"","time": $(epoch_millis),"headers":[{"key":"authorization", "value":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZXhwIjo5OTk5OTk5OTk5OSwicGFzc3dvcmQiOiJibGFibHUifQ.SLWwRavOnos1ihyRJUPeG3xjKRy8eIBvUOD6VqW20WU"}],"body":"","TruncatedBody":false}},"response": {"statusCode": "200", "common": {"time": $(epoch_millis), "version": "1", "headers": null, "body": "", "TruncatedBody": false}}}
EOT
