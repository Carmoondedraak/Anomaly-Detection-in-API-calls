package controllers

// endpoints.go contains the endpoint definitions, including per-method request
// and response structs. Endpoints are the binding between the service and
// transport.

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/labstack/echo"
	models "wwwin-github.cisco.com/scn-demo/test-app/microservices/user/models"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/services"
)

type CustomerController struct {
	CustomerService services.ICustomerService
	Health models.Health
}

func NewCustomerController(s services.ICustomerService, h models.Health) *CustomerController {
	return &CustomerController{s, h}
}

func (c *CustomerController) Healthz(ctx echo.Context) (err error) {
	return ctx.JSON(http.StatusOK, c.Health)
}

func (c *CustomerController) Register(ctx echo.Context) (err error) {
	e := echo.New()

	var req models.RegisterRequest

	requestJson := retrieveRequestObject(ctx)
	json.Unmarshal([]byte(requestJson), &req)

	e.Logger.Print("registerRequest:", req)

	id, err := c.CustomerService.Register(req.Username, req.Password, req.Email, req.FirstName, req.LastName)
	if err != nil {
		fmt.Println(err)
	}
	e.Logger.Print("Register Response:", models.ResponseResponse{ID: id})
	return ctx.JSON(http.StatusOK, models.ResponseResponse{ID: id})
}

func (c *CustomerController) Login(ctx echo.Context) (err error) {

	e := echo.New()

	var req loginRequest

	requestJson := retrieveRequestObject(ctx)
	json.Unmarshal([]byte(requestJson), &req)

	username := ctx.Get("username").(string)
	password := ctx.Get("password").(string)

	e.Logger.Print("Login Request:", username, password)

	cus, err := c.CustomerService.Login(username, password)

	if err != nil {
		fmt.Println("No user found..")
	}
	cookie := &http.Cookie{
		Name:    "sessionID",
		Value:   "some_string",
		Expires: time.Now().Add(48 * time.Hour),
	}
	ctx.SetCookie(cookie)
	e.Logger.Print("Login Response:", cus)
	return ctx.JSON(http.StatusOK, models.CustomerResponse{Customer: cus})
}

func (c *CustomerController) GetCustomer(ctx echo.Context) (err error) {

	e := echo.New()

	customerId := ctx.Param("id")
	path := ctx.Path()
	url := ctx.Request().URL.Path

	e.Logger.Print("customer id => ", customerId)
	e.Logger.Print("path => ", path)
	e.Logger.Print("url => ", url)

	pathArray := strings.Split(url, "/")
	resourcePath := pathArray[len(pathArray)-1]

	e.Logger.Print("Resource Path", resourcePath)

	req := GetRequest{
		ID:   customerId,
		Attr: resourcePath,
	}

	e.Logger.Print("getRequest:", req)

	cus, err := c.CustomerService.GetCustomer(req.ID)
	if err != nil {
		fmt.Println(err)
	}
	
	e.Logger.Print("Customer:", cus)
	return ctx.JSON(http.StatusOK, cus)
}

func (c *CustomerController) GetCustomerById(ctx echo.Context) (err error) {

	e := echo.New()

	customerId := ctx.Param("id")


	e.Logger.Print("customer id => ", customerId)

	cus, err := c.CustomerService.GetCustomer(customerId)
	if err != nil {
		fmt.Println(err)
	}
	
	if cus != nil {
			e.Logger.Print("Customer:", cus)
			return ctx.JSON(http.StatusOK, cus)
	}
	return ctx.JSON(http.StatusOK, models.Customer{})
}

func (c *CustomerController) GetCustomers(ctx echo.Context) (err error) {

	e := echo.New()

	customerId := ctx.Param("id")
	path := ctx.Path()
	url := ctx.Request().URL.Path

	e.Logger.Print("customer id => ", customerId)
	e.Logger.Print("path => ", path)
	e.Logger.Print("url => ", url)

	pathArray := strings.Split(url, "/")
	resourcePath := pathArray[len(pathArray)-1]

	e.Logger.Print("Resource Path", resourcePath)

	req := GetRequest{
		ID:   customerId,
		Attr: resourcePath,
	}

	e.Logger.Print("getRequest:", req)

	customers, err := c.CustomerService.GetCustomers()
	if err != nil {
		fmt.Println(err)
	}

	return ctx.JSON(http.StatusOK, models.EmbedStruct{ models.CustomerResponse{Customer: customers}})
}

func (c *CustomerController) GetCustomerAddresses(ctx echo.Context) (err error) {

	e := echo.New()

	customerId := ctx.Param("id")

	e.Logger.Print("customer id => ", customerId)

	addresses, err := c.CustomerService.GetAddressesByCustomerId(customerId)
	if err != nil {
		fmt.Println(err)
	}

	e.Logger.Print("addressResponse:", addresses)
	return ctx.JSON(http.StatusOK, models.EmbedStruct{ models.AddressResponse { Address : addresses} })
}

func (c *CustomerController) GetCustomerCards(ctx echo.Context) (err error) {

	e := echo.New()

	customerId := ctx.Param("id")

	e.Logger.Print("customer id => ", customerId)

	cards, err := c.CustomerService.GetCardsByCustomerId(customerId)
	if err != nil {
		fmt.Println(err)
	}

	e.Logger.Print("cardResponse:", cards)
	return ctx.JSON(http.StatusOK, models.EmbedStruct{ models.CardResponse { Card : cards} })
}

func (c *CustomerController) DeleteCustomer(ctx echo.Context) (err error) {
	e := echo.New()

	var req models.Customer

	requestJson := retrieveRequestObject(ctx)
	json.Unmarshal([]byte(requestJson), &req)

	e.Logger.Print("userRequest:", req)
	return ctx.JSON(http.StatusOK, nil)
}

func retrieveRequestObject(c echo.Context) string {
	body, err := ioutil.ReadAll(c.Request().Body)
	if err != nil {
		log.Fatalln("Error retrieving request body")
	}
	bodyString := string(body)
	return bodyString
}

type GetRequest struct {
	ID   string
	Attr string
}

type loginRequest struct {
	Username string
	Password string
}