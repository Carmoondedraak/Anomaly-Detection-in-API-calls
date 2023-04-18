package routes

import (
	"github.com/labstack/echo"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/controllers"
)



func InitAddressRoutes(controller *controllers.AddressController, e *echo.Echo) {
	e.POST("/addresses", controller.PostAddress)
	e.GET("/addresses", controller.GetAddresses)
	e.GET("/addresses/:id", controller.GetAddressById)
	e.DELETE("/addresses/:id", controller.DeleteAddressById)

}