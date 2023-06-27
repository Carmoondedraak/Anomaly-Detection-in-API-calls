package models

// Transaction information
type Transaction struct {
	Payment  Payment  `json:"payload"`
	Feedback Feedback `json:"outcome"`
}
