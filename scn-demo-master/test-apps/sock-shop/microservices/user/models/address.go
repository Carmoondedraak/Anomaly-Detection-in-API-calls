package models

import (
	"fmt"
	"strings"
)

type Address struct {
	ID       string           `json:"id" bson:"id,omitempty"`
	Street   string           `json:"street" bson:"street,omitempty"`
	Number   string           `json:"number" bson:"number,omitempty"`
	Country  string           `json:"country" bson:"country,omitempty"`
	City     string           `json:"city" bson:"city,omitempty"`
	PostCode string           `json:"postcode" bson:"postcode,omitempty"`
	Links    Links            `json:"-" bson:"-"`
	LinkMap  map[string]Hrefs `json:"_links" bson:"_links"`
	UserID   string           `json:"userId" bson:"userId,omitempty"`
}

func (a *Address) AddLinks() {
	a.Links.AddAddress(a.ID)
	a.IncludeLinks()
}

func (a *Address) IncludeLinks() {
	links := make(map[string]Hrefs)
	for key, link := range a.Links {
		fmt.Println("Key:", key, "=>", "Link:", link)

		linkArray := strings.Split(link.string, "///")
		resultLink := strings.Join(linkArray, "//user/")
		href := Hrefs{
			Href: resultLink,
		}
		links[key] = href
	}
	a.LinkMap = links
}
