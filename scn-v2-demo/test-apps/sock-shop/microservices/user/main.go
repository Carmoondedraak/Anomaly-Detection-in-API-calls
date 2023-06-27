package main

import (
	"fmt"
	"time"

	"github.com/labstack/echo"
	log2 "github.com/labstack/gommon/log"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/controllers"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/db"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/models"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/repositories"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/routes"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/services"
)


func main()  {
	e := echo.New()

	dbStatus := "OK"

	dao, err:= db.NewDAO()
	if err != nil {
		dbStatus = ""
		panic(fmt.Sprintf("%s:%s", "Database error:", err))
	}

	appHealth := models.Health{dbStatus, time.Now().String()}

	cardRepository := repositories.NewCardRepository(dao)
	cardService := services.NewCardService(&cardRepository)
	cardController := controllers.NewCardController(cardService)
	routes.InitCardRoutes(cardController, e)

	addressRepository := repositories.NewAddressRepository(dao)
	addressService := services.NewAddressService(&addressRepository)
	addressController := controllers.NewAddressController(addressService)
	routes.InitAddressRoutes(addressController, e)

	// Initialize Service
	customerRepository := repositories.NewCustomerRepository(dao)
	customerService := services.NewCustomerService(&customerRepository, &addressService, &cardService)
	customerController := controllers.NewCustomerController(customerService, appHealth)
	routes.InitCustomerRoutes(customerController, e)






	e.Logger.SetLevel(log2.INFO)
	e.Logger.Fatal(e.Start(":8000"))
}