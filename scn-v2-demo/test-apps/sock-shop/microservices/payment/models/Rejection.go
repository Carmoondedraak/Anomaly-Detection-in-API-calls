package models

type Rejection struct {
	Authorisation Authorisation
	Err           error
}
