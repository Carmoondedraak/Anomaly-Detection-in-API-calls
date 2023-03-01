package routes

import (
	"github.com/labstack/echo"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/controllers"
)

func InitCardRoutes(controller *controllers.CardController, e *echo.Echo) {
    e.POST("/cards", controller.PostCard)
    e.GET("/cards", controller.GetCards)
	e.GET("/cards/:id", controller.GetCardById)
	e.DELETE("/cards/:id", controller.DeleteCardById)
}