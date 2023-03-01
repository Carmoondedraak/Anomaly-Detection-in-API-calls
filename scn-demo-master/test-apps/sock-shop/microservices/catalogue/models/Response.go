package models

type SockDTO struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Description string   `json:"description"`
	ImageURL    []string `json:"imageUrl"`
	Price       float64  `json:"price"`
	Count       int      `json:"count"`
	Tags        []string `json:"tag"`
}

type TagDTO struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

type ListResponse struct {
	Socks []SockDTO `json:"sock"`
	Err   error  `json:"err"`
}

type CountResponse struct {
	N   int   `json:"size"` // to match original
	Err error `json:"err"`
}

type GetResponse struct {
	Sock Sock  `json:"sock"`
	Err  error `json:"err"`
}

type TagsResponse struct {
	Tags []string `json:"tags"`
	Err  error    `json:"err"`
}

type HealthResponse struct {
	Health []Health `json:"health"`
}
