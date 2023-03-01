package main

import (
	"github.com/labstack/echo/v4"
	echoSwagger "github.com/swaggo/echo-swagger"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/payment/controllers"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/payment/database"
	_ "wwwin-github.cisco.com/scn-demo/test-app/microservices/payment/docs"
)
// @title Gateway to Paypal Sandbox
// @version 1.0
// @description This service acts as a gateway to Paypal Sandbox (a simulator to actual PayPal Service).
// @termsOfService https://swagger.io/terms/

// @contact.name API Support
// @contact.url https://www.swagger.io/support
// @contact.email ntafie@cisco.com

// @license.name Apache 2.0
// @license.url https://www.apache.org/licenses/LICENSE-2.0.html

// @host /
// @BasePath
func main()  {
	e := echo.New()

	database.Setup()

	e.POST("/paymentAuth", controllers.Authorise)
	e.GET("/transactions", controllers.FetchTransactions)
	e.POST("/verify", controllers.VerifyTransaction)
	e.GET("/swagger/*", echoSwagger.WrapHandler)
	e.Logger.Fatal(e.Start(":80"))
}
