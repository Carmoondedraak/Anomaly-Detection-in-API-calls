package services

import (
	"bytes"
	"fmt"
	"github.com/labstack/echo/v4"
	"io/ioutil"
	"net/http"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/payment/models"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/payment/repositories"
)

func ProcessPayment(amount float64, authKey string, bearerKey string, paymentUrl string, accessToken string, headerKey string, headerValue string) models.Feedback {
	client := &http.Client{}

	var body = []byte(`{"intent": "CAPTURE", "purchase_units": [{"amount": {"currency_code": "GBP","value": "` + fmt.Sprintf("%v", amount) + `"}}]}`)

	req, err := http.NewRequest("POST", fmt.Sprintf("%s", paymentUrl), bytes.NewBuffer(body))
	if err != nil {
		return models.Feedback{
			Status:  false,
			Message: "Payment declined",
		}
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-internal-ip-server", "10.1.0.1")
	req.Header.Set("password", "password")
	req.Header.Add(authKey, fmt.Sprintf("%s %s", bearerKey, accessToken))

	fmt.Println("########################## REQUEST #####################")
	fmt.Println(req)

	resp, err := client.Do(req)
	if resp.StatusCode == 401 {
		return models.Feedback{
			Status:  false,
			Message: "Payment declined",
		}
		fmt.Println(err)
	}

	fmt.Println("########################## RESPONSE #####################")
	fmt.Println(resp.Status)
	respBody, err := ioutil.ReadAll(resp.Body)
	fmt.Println(string (respBody))
	return models.Feedback{
		Status:  true,
		Message: "Payment Authorised",
	}
}

func CreateTransaction(t models.Transaction) string {
	e := echo.New()

	transactionId, err := repositories.SaveTransaction(t)
	if err != nil{
		panic("Error saving transaction")
	}
	e.Logger.Printf("Transaction with id: %s, was created", transactionId)

	return transactionId
}

func FetchTransactions() [] *models.Transaction {
	e := echo.New()
	transactions, err := repositories.GetTransactions()
	if err != nil{
		panic("Error fetching transactions")
	}
	e.Logger.Printf(" %d Transactions found", len(transactions))
	return transactions
}