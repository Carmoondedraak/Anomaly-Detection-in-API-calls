package repositories

import (
	"context"
	"fmt"
	"github.com/labstack/gommon/log"
	"go.mongodb.org/mongo-driver/bson"
	_ "strings"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/payment/database"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/payment/models"
)

func SaveTransaction(t models.Transaction)(string, error){
	result, err := database.TransactionCollection.InsertOne(context.TODO(), t)

	if err != nil {
		log.Fatal(err)
	}
	return 	fmt.Sprintf("%v", result.InsertedID), err
}

func GetTransactions() ([]*models.Transaction, error) {
	var transactions []*models.Transaction

	selector := bson.D{{}}

	cur, err := database.TransactionCollection.Find(context.TODO(), selector)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.Transaction
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		transactions = append(transactions, &elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return transactions, nil
}
