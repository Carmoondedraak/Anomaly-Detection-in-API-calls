package models

import (
	"fmt"
	"strings"
)

type Card struct {
	ID      string           `json:"id" bson:"id,omitempty"`
	LongNum string           `json:"longNum" bson:"longNum,omitempty"`
	Expires string           `json:"expires" bson:"expires,omitempty"`
	CCV     string           `json:"ccv" bson:"ccv,omitempty"`
	Links   Links            `json:"-" bson:"-"`
	LinkMap map[string]Hrefs `json:"_links" bson:"_links"`
	UserID  string           `json:"userId" bson:"userId,omitempty"`
}

func (c *Card) MaskCC() {
	l := len(c.LongNum) - 4
	c.LongNum = fmt.Sprintf("%v%v", strings.Repeat("*", l), c.LongNum[l:])
}

func (c *Card) AddLinks() {
	c.Links.AddCard(c.ID)
	c.IncludeLinks()
}

func (c *Card) IncludeLinks() {
	links := make(map[string]Hrefs)
	for key, link := range c.Links {
		fmt.Println("Key:", key, "=>", "Link:", link)

		linkArray := strings.Split(link.string, "///")
		resultLink := strings.Join(linkArray, "//user/")
		href := Hrefs{
			Href: resultLink,
		}
		links[key] = href
	}
	c.LinkMap = links
}
