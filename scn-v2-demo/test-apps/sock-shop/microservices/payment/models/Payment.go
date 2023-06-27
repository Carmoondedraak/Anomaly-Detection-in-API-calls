package models

// Payment information
type Payment struct {
	Address  Address  `json:"address"`
	Card     Card     `json:"card"`
	Customer Customer `json:"customer"`
	Amount   float64  `json:"amount"`
}

type Address struct {
	Id       string `json:"id"`
	Number   int64  `json:"number"`
	Street   string `json:"street"`
	City     string `json:"city"`
	PostCode string `json:"postcode"`
	Country  string `json:"country"`
}

type Card struct {
	Id      string `json:"id"`
	LongNum string `json:"message"`
	expires string `json:"message"`
	ccv     int64  `json:"message"`
}

type Customer struct {
	Id        string    `json:"id"`
	FirstName string    `json:"firstName"`
	LastName  string    `json:"lastName"`
	UserName  string    `json:"userName"`
	Addresses []Address `json:"addresses"`
	Cards     []Card    `json:"cards"`
}
