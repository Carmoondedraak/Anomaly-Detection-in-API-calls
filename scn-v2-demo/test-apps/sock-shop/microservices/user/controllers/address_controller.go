package controllers

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/labstack/echo"

	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/models"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/services"
)

type AddressController struct {
	addressService services.IAddressService
}

func NewAddressController(s services.IAddressService) *AddressController {
	return &AddressController{s}
}

func (c *AddressController) PostAddress(ctx echo.Context) (err error) {

	e := echo.New()

	var address models.Address

	requestJson := retrieveRequestObject(ctx)
	json.Unmarshal([]byte(requestJson), &address)

	e.Logger.Print("Post Address Request:", address)

	id, err := c.addressService.PostAddress(address)
	if err != nil {
		fmt.Println(err)
	}
	e.Logger.Print("Post Address Response:", models.ResponseResponse{ID: id})
	return ctx.JSON(http.StatusOK, models.ResponseResponse{ID: id})

}

func (c *AddressController) GetAddressById(ctx echo.Context) (err error) {

	e := echo.New()

	addressId := ctx.Param("id")

	e.Logger.Print("address id => ", addressId)

	address, err := c.addressService.GetAddress(addressId)
	if err != nil {
		fmt.Println(err)
	}
	e.Logger.Print("addresses:", address)
	return ctx.JSON(http.StatusOK, address)
}

func (c *AddressController) GetAddresses(ctx echo.Context) (err error) {
	e := echo.New()

	addresses, err := c.addressService.GetAllAddresses()
	if err != nil {
		fmt.Println(err)
	}

	e.Logger.Print("addressResponse:", addresses)
	return ctx.JSON(http.StatusOK, addresses)
}

func (c *AddressController) DeleteAddressById(ctx echo.Context) (err error) {

	e := echo.New()

	addressId := ctx.Param("id")

	e.Logger.Print("address id => ", addressId)

	err = c.addressService.DeleteAddress(addressId)
	if err == nil {
		return ctx.JSON(http.StatusOK, true)
	}
	return ctx.JSON(http.StatusOK, false)
}
