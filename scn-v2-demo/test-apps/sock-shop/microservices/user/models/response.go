package models

type CustomerResponse struct {
	Customer interface{} `json:"user"`
}

type AddressResponse struct {
	Address interface{} `json:"address"`
}

type CardResponse struct {
	Card interface{} `json:"card"`
}

type EmbedStruct struct {
	Embed interface{} `json:"_embedded"`
}

type ResponseResponse struct {
	ID string `json:"id"`
}
