package models

// Sock describes the thing on offer in the catalogue.
type Sock struct {
	ID          string   `bson:"id"`
	Name        string   `bson:"name"`
	Description string   `bson:"description"`
	ImageURL    []string `bson:"image_url"`
	ImageURL_1  string   `bson:"image_url_1"`
	ImageURL_2  string   `bson:"image_url_2"`
	Price       float64  `bson:"price"`
	Count       int      `bson:"count"`
	Tags        []string `bson:"tag"`
	TagString   string   `bson:"tag_name"`
}

type Tag struct {
	ID   int    `bson:"id"`
	Name string `bson:"name"`
}

type SockTag struct {
	SockID string `bson:"sock_id"`
	TagID  int    `bson:"tag_id"`
}
// Health describes the health of a service
type Health struct {
	Service string `json:"service"`
	Status  string `json:"status"`
	Time    string `json:"time"`
}
