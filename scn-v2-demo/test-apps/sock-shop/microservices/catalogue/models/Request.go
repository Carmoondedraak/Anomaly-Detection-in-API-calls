package models

type ListRequest struct {
	Tags     []string `json:"tags"`
	Order    string   `json:"order"`
	PageNum  int      `json:"pageNum"`
	PageSize int      `json:"pageSize"`
}

type CountRequest struct {
	Tags []string `json:"tags"`
}

type GetRequest struct {
	ID string `json:"id"`
}

type TagsRequest struct {
	//
}

type HealthRequest struct {
	//
}