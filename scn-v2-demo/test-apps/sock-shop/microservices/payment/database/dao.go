package database

import (
	"context"
	"fmt"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"log"
)

var (
	TransactionCollection *mongo.Collection
	Ctx               = context.TODO()
)

func Setup(){
	//payment-db
	mongoDbUrl := "mongodb://payment-db:27017"
	clientOptions := options.Client().ApplyURI(mongoDbUrl)
	client, err := mongo.Connect(Ctx, clientOptions)
	if err != nil {
		log.Fatalln(err)
	}

	err = client.Ping(Ctx, nil)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Connecting to payment database successful!")

	db := client.Database("payment")
	TransactionCollection = db.Collection("transactions")
}
