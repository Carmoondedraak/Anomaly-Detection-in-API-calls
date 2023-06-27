package models

type Feedback struct {
	Status  bool   `json:"status"`
	Message string `json:"message"`
}
