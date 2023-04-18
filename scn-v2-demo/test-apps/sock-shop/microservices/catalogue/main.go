package main

import (
	"catalogue/controllers"
	"catalogue/database"
	"github.com/labstack/echo/v4"
)

func main() {
	e := echo.New()

	database.InitDB()

	e.GET("/catalogue", controllers.FetchSocks)
	e.GET("/catalogue/size", controllers.CountSocks)
	e.GET("/catalogue/:id", controllers.FetchSockById)
	e.GET("/tags", controllers.FetchTags)
	e.GET("/health", controllers.Health)
	e.Static("/catalogue/images", "images")
	e.Logger.Fatal(e.Start(":80"))
}
