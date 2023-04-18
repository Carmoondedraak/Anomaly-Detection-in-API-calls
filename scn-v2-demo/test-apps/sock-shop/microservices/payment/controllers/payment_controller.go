package controllers

import (
	"encoding/json"
	"errors"
	"github.com/labstack/echo/v4"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/payment/models"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/payment/services"
)

var ErrInvalidPaymentAmount = errors.New("invalid payment amount")

// Authorise @Title AuthorisePayment
// @Description Authorise Payment for placed order
// @Accept  json
// @Produce json
// @Param payment body models.Payment true "Payment details"
// @Success 200 {object} models.Feedback
// @Failure 400 {object} models.Feedback
// @Router /paymentAuth [post]
func Authorise(ctx echo.Context) (err error) {

	e := echo.New()

	var payment models.Payment

	paymentJson := retrieveRequestObject(ctx)
	json.Unmarshal([]byte(paymentJson), &payment)

	e.Logger.Print("Payment:", payment)

	if payment.Amount == 0 {
		return ctx.JSON(
			http.StatusBadRequest,
			models.Rejection{
				Authorisation: models.Authorisation{
					Authorised: false,
					Message:    ErrInvalidPaymentAmount.Error(),
				}})
	}

	if payment.Amount < 0 {
		return ctx.JSON(
			http.StatusBadRequest,
			models.Rejection{
				Authorisation: models.Authorisation{
					Authorised: false,
					Message:    ErrInvalidPaymentAmount.Error(),
				}})
	}

	var authorised bool
	var message string

	callCounter := 0

	paymentUrl := os.Getenv("PAYPAL_SERVICE_URL")
	accessToken := os.Getenv("PAYPAL_ACCESS_TOKEN")

	feedback := services.ProcessPayment(payment.Amount, "Authorization", "Bearer", paymentUrl, accessToken, "time", time.Now().String())
	callCounter += 1

	log.Println("Paypal service called", callCounter, " time")
	authorised = feedback.Status
	message = feedback.Message

	code := http.StatusUnauthorized
	if authorised {
		code = http.StatusCreated
	}

	e.Logger.Printf("Authorised: %t, Reason: %s", authorised, message)

	/**
	 * Persist Transaction (Payment and Status)
	 */
	transaction := models.Transaction{
		Payment: payment,
		Feedback: models.Feedback{
			Status:  authorised,
			Message: message,
		},
	}
	services.CreateTransaction(transaction)

	return ctx.JSON(
		code,
		models.Authorisation{
			Authorised: authorised,
			Message:    message,
		})
}

// FetchTransactions Retrieve @Title Transactions
// @Description FetchTransactions Retrieves executed Transaction for placed order
// @Accept  json
// @Produce json
// @Success 200 {object} models.Transaction
// @Failure 400 {string} Error
// @Router /FetchTransactions [get]
func FetchTransactions(ctx echo.Context) (err error) {
	return ctx.JSON(
		http.StatusOK,
		services.FetchTransactions())
}

// VerifyTransaction Verifies @Title Transactions
// @Description Verifies executed Transaction for placed order
// @Accept  json
// @Produce json
// @Param payment body models.Transaction true "Transaction details"
// @Success 200 {object} models.Transaction
// @Failure 400 {string} Error
// @Failure 500 {string} Server Error
// @Router /VerifyTransaction [post]
func VerifyTransaction(ctx echo.Context) (err error) {
	return ctx.JSON(
		http.StatusInternalServerError,
		models.Feedback{
			Status:  false,
			Message: "Something really bad happened!",
		})
}

func retrieveRequestObject(c echo.Context) string {
	body, err := ioutil.ReadAll(c.Request().Body)
	if err != nil {
		log.Fatalln("Error retrieving request body")
	}
	bodyString := string(body)
	return bodyString
}
