// Code generated by go-swagger; DO NOT EDIT.

package operations

// This file was generated by the swagger tool.
// Editing this file might prove futile when you re-run the swagger generate command

import (
	"net/http"

	"github.com/go-openapi/runtime"

	"github.com/openclarity/apiclarity/api/server/models"
)

// GetAPIInventoryAPIIDAPIInfoOKCode is the HTTP code returned for type GetAPIInventoryAPIIDAPIInfoOK
const GetAPIInventoryAPIIDAPIInfoOKCode int = 200

/*GetAPIInventoryAPIIDAPIInfoOK Success

swagger:response getApiInventoryApiIdApiInfoOK
*/
type GetAPIInventoryAPIIDAPIInfoOK struct {

	/*
	  In: Body
	*/
	Payload *models.APIInfoWithType `json:"body,omitempty"`
}

// NewGetAPIInventoryAPIIDAPIInfoOK creates GetAPIInventoryAPIIDAPIInfoOK with default headers values
func NewGetAPIInventoryAPIIDAPIInfoOK() *GetAPIInventoryAPIIDAPIInfoOK {

	return &GetAPIInventoryAPIIDAPIInfoOK{}
}

// WithPayload adds the payload to the get Api inventory Api Id Api info o k response
func (o *GetAPIInventoryAPIIDAPIInfoOK) WithPayload(payload *models.APIInfoWithType) *GetAPIInventoryAPIIDAPIInfoOK {
	o.Payload = payload
	return o
}

// SetPayload sets the payload to the get Api inventory Api Id Api info o k response
func (o *GetAPIInventoryAPIIDAPIInfoOK) SetPayload(payload *models.APIInfoWithType) {
	o.Payload = payload
}

// WriteResponse to the client
func (o *GetAPIInventoryAPIIDAPIInfoOK) WriteResponse(rw http.ResponseWriter, producer runtime.Producer) {

	rw.WriteHeader(200)
	if o.Payload != nil {
		payload := o.Payload
		if err := producer.Produce(rw, payload); err != nil {
			panic(err) // let the recovery middleware deal with this
		}
	}
}

/*GetAPIInventoryAPIIDAPIInfoDefault unknown error

swagger:response getApiInventoryApiIdApiInfoDefault
*/
type GetAPIInventoryAPIIDAPIInfoDefault struct {
	_statusCode int

	/*
	  In: Body
	*/
	Payload *models.APIResponse `json:"body,omitempty"`
}

// NewGetAPIInventoryAPIIDAPIInfoDefault creates GetAPIInventoryAPIIDAPIInfoDefault with default headers values
func NewGetAPIInventoryAPIIDAPIInfoDefault(code int) *GetAPIInventoryAPIIDAPIInfoDefault {
	if code <= 0 {
		code = 500
	}

	return &GetAPIInventoryAPIIDAPIInfoDefault{
		_statusCode: code,
	}
}

// WithStatusCode adds the status to the get API inventory API ID API info default response
func (o *GetAPIInventoryAPIIDAPIInfoDefault) WithStatusCode(code int) *GetAPIInventoryAPIIDAPIInfoDefault {
	o._statusCode = code
	return o
}

// SetStatusCode sets the status to the get API inventory API ID API info default response
func (o *GetAPIInventoryAPIIDAPIInfoDefault) SetStatusCode(code int) {
	o._statusCode = code
}

// WithPayload adds the payload to the get API inventory API ID API info default response
func (o *GetAPIInventoryAPIIDAPIInfoDefault) WithPayload(payload *models.APIResponse) *GetAPIInventoryAPIIDAPIInfoDefault {
	o.Payload = payload
	return o
}

// SetPayload sets the payload to the get API inventory API ID API info default response
func (o *GetAPIInventoryAPIIDAPIInfoDefault) SetPayload(payload *models.APIResponse) {
	o.Payload = payload
}

// WriteResponse to the client
func (o *GetAPIInventoryAPIIDAPIInfoDefault) WriteResponse(rw http.ResponseWriter, producer runtime.Producer) {

	rw.WriteHeader(o._statusCode)
	if o.Payload != nil {
		payload := o.Payload
		if err := producer.Produce(rw, payload); err != nil {
			panic(err) // let the recovery middleware deal with this
		}
	}
}