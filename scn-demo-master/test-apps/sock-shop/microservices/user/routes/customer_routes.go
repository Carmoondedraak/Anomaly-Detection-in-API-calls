package routes

import (
	"fmt"

	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/controllers"
)



func InitCustomerRoutes(controller *controllers.CustomerController, e *echo.Echo) {
	g := e.Group("/login")
	g.Use(middleware.BasicAuth(func(username, password string, c echo.Context) (bool, error) {
		fmt.Println("Authenticating with:", username, password)
		if username == "" && password == "" {
			return false, nil
		}
		c.Set("username", username)
		c.Set("password", password)
		return true, nil
	}))
	g.GET("", controller.Login)
	e.GET("/healthz", controller.Healthz)
    e.POST("/register", controller.Register)
	e.GET("/customers", controller.GetCustomers)
    e.GET("/customers/:id", controller.GetCustomerById)
	e.GET("/customers/:id/addresses", controller.GetCustomerAddresses)
	e.GET("/customers/:id/cards", controller.GetCustomerCards)
	e.DELETE("/customers/:id", controller.DeleteCustomer)
}