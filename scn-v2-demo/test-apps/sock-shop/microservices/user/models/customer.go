package models

import (
	"crypto/sha1"
	"errors"
	"fmt"
	"io"
	"strconv"
	"strings"
	"time"
)

var (
	ErrNoCustomerInResponse = errors.New("Response has no matching customer")
	ErrMissingField         = "Error missing %v"
)

type Customer struct {
	Id        string           `json:"id" bson:"id"`
	FirstName string           `json:"firstName" bson:"firstName"`
	LastName  string           `json:"lastName" bson:"lastName"`
	Email     string           `json:"email" bson:"email"`
	Username  string           `json:"username" bson:"username"`
	Password  string           `json:"password" bson:"password"`
	Addresses []Address        `json:"addresses" bson:"addresses"`
	Cards     []Card           `json:"cards" bson:"cards"`
	Links     Links            `json:"-" bson:"-"`
	LinkMap   map[string]Hrefs `json:"_links" bson:"_links"`
	Salt      string           `json:"salt" bson:"salt"`
}

type Hrefs struct {
	Href string `json:"href" bson:"href"`
}

func New() Customer {
	c := Customer{Addresses: make([]Address, 0), Cards: make([]Card, 0)}
	c.NewSalt()
	return c
}

func (c *Customer) Validate() error {
	if c.FirstName == "" {
		return fmt.Errorf(ErrMissingField, "FirstName")
	}
	if c.LastName == "" {
		return fmt.Errorf(ErrMissingField, "LastName")
	}
	if c.Username == "" {
		return fmt.Errorf(ErrMissingField, "Username")
	}
	if c.Password == "" {
		return fmt.Errorf(ErrMissingField, "Password")
	}
	return nil
}

func (cus *Customer) MaskCCs() {
	for k, c := range cus.Cards {
		c.MaskCC()
		cus.Cards[k] = c
	}
}

func (c *Customer) IncludeLinks() {
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

func (c *Customer) AddLinks() {
	c.Links.AddCustomer(c.Id)
}

func (c *Customer) NewSalt() {
	h := sha1.New()
	io.WriteString(h, strconv.Itoa(int(time.Now().UnixNano())))
	c.Salt = fmt.Sprintf("%x", h.Sum(nil))
}
