package controllers

import (
	"catalogue/models"
	"catalogue/services"
	"encoding/json"
	"fmt"
	"github.com/labstack/echo/v4"
	"io/ioutil"
	"log"
	"net/http"
	"strconv"
	"strings"
)

func FetchSocks(ctx echo.Context) (err error) {
	e := echo.New()

	var page, size int

	if ctx.QueryParam("page") == "0" {
		page = 0
	} else {
		page, _ = strconv.Atoi(ctx.QueryParam("page"))
	}

	if ctx.QueryParam("size") == "0" {
		size = 0
	} else {
		size, _ = strconv.Atoi(ctx.QueryParam("size"))
	}

	tags := ctx.QueryParam("tags")
	order := ctx.QueryParam("order")

	e.Logger.Printf(fmt.Sprintf("Page:%v - Page Size:%v - Tags:%s - Order:%s", page, size, tags, order))
	socks, err := services.List(strings.Split(tags, ","), order, page, size)
	for _, v := range socks {
		e.Logger.Print("Socks:", v)
	}
	return ctx.JSON(http.StatusOK, socks)
}

func CountSocks(ctx echo.Context) (err error) {
	e := echo.New()

	var page, size int

	if ctx.QueryParam("page") == "0" {
		page = 0
	} else {
		page, _ = strconv.Atoi(ctx.QueryParam("page"))
	}

	if ctx.QueryParam("size") == "0" {
		size = 0
	} else {
		size, _ = strconv.Atoi(ctx.QueryParam("size"))
	}
	tags := ctx.QueryParam("tags")

	order := ctx.QueryParam("order")

	e.Logger.Printf(fmt.Sprintf("Page:%v - Page Size:%v - Tags:%s - Order:%s", page, size, tags, order))

	count, err := services.Count(strings.Split(tags, ","))

	return ctx.JSON(http.StatusOK, models.CountResponse{
		N: count,
	})
}

func FetchSockById(ctx echo.Context) (err error) {
	e := echo.New()

	id := ctx.Param("id")

	e.Logger.Print("CountSocks Params:", id)

	var page, size int

	if ctx.QueryParam("page") == "0" {
		page = 0
	} else {
		page, _ = strconv.Atoi(ctx.QueryParam("page"))
	}

	if ctx.QueryParam("size") == "0" {
		size = 0
	} else {
		size, _ = strconv.Atoi(ctx.QueryParam("size"))
	}

	tags := ctx.QueryParam("tags")

	order := ctx.QueryParam("order")

	e.Logger.Printf(fmt.Sprintf("Page:%v - Page Size:%v - Tags:%s - Order:%s", page, size, tags, order))

	sock, err := services.Get(id)

	return ctx.JSON(http.StatusOK, sock)
}

func FetchTags(ctx echo.Context) (err error) {
	e := echo.New()

	var page, size int

	if ctx.QueryParam("page") == "0" {
		page = 0
	} else {
		page, _ = strconv.Atoi(ctx.QueryParam("page"))
	}

	if ctx.QueryParam("size") == "0" {
		size = 0
	} else {
		size, _ = strconv.Atoi(ctx.QueryParam("size"))
	}

	order := ctx.QueryParam("order")

	e.Logger.Printf(fmt.Sprintf("Page:%v - Page Size:%v - Order:%s", page, size, order))

	tags, err := services.Tags()

	return ctx.JSON(http.StatusOK, models.TagsResponse{
		Tags: tags,
	})
}

func Health(ctx echo.Context) (err error) {
	e := echo.New()
	var req models.HealthRequest

	jsonRequest := retrieveRequestObject(ctx)
	json.Unmarshal([]byte(jsonRequest), &req)

	health := services.Health()
	e.Logger.Print("FetchSocks Request:", req)

	return ctx.JSON(http.StatusOK, health)
}

func retrieveRequestObject(c echo.Context) string {
	body, err := ioutil.ReadAll(c.Request().Body)
	if err != nil {
		log.Fatalln("Error retrieving request body")
	}
	bodyString := string(body)
	return bodyString
}
