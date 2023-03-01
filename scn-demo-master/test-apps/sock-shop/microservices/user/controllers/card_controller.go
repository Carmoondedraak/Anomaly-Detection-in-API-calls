package controllers

import (
	"encoding/json"
	"fmt"
	"net/http"

	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/models"

	"github.com/labstack/echo"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/services"
)

type CardController struct {
	cardService services.ICardService
}

func NewCardController(s services.ICardService) *CardController {
	return &CardController{s}
}

func (c *CardController) PostCard(ctx echo.Context) (err error) {

	e := echo.New()

	var card models.Card

	requestJson := retrieveRequestObject(ctx)
	json.Unmarshal([]byte(requestJson), &card)

	e.Logger.Print("Post Card Request:", card)

	id, err := c.cardService.PostCard(card)
	if err != nil {
		fmt.Println(err)
	}
	e.Logger.Print("Post Card Response:", models.ResponseResponse{ID: id})
	return ctx.JSON(http.StatusOK, models.ResponseResponse{ID: id})
}

func (c *CardController) GetCardById(ctx echo.Context) (err error) {
	e := echo.New()

	cardID := ctx.Param("id")

	e.Logger.Print("card id => ", cardID)

	card, err := c.cardService.GetCard(cardID)
	if err != nil {
		fmt.Println(err)
	}

	e.Logger.Print("cards:", card)
	return ctx.JSON(http.StatusOK, card)
}

func (c *CardController) GetCards(ctx echo.Context) (err error) {

	e := echo.New()
	cards, err := c.cardService.GetCards()
	if err != nil {
		fmt.Println(err)
	}

	e.Logger.Print("cardsResponse:", cards)
	return ctx.JSON(http.StatusOK, cards)
}

func (c *CardController) GetCustomerCards(ctx echo.Context) (err error) {

	e := echo.New()

	customerID := ctx.Param("id")

	e.Logger.Print("customer id => ", customerID)

	cards, err := c.cardService.GetCustomerCards(customerID)
	if err != nil {
		fmt.Println(err)
	}

	e.Logger.Print("cardsResponse:", cards)
	return ctx.JSON(http.StatusOK, cards)
}

func (c *CardController) DeleteCardById(ctx echo.Context) (err error) {
	e := echo.New()

	cardId := ctx.Param("id")

	e.Logger.Print("card id => ", cardId)

	err = c.cardService.Delete(cardId)
	if err == nil {
		return ctx.JSON(http.StatusOK, true)
	}
	return ctx.JSON(http.StatusOK, false)
}
