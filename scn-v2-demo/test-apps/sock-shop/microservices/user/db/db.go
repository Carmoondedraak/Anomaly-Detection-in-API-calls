package db

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

var (
	name     string
	password string
	host     string
	port     string
	db       string
)

func init() {
	os.Setenv("DB_HOST", "localhost")
	os.Setenv("DB_PORT", "27017")
	flag.StringVar(&name, "db-user", os.Getenv("DB_USER"), "Database user")
	flag.StringVar(&password, "db-password", os.Getenv("DB_PASSWORD"), "Database password")
	flag.StringVar(&host, "db-host", os.Getenv("DB_HOST"), "Database host")
	flag.StringVar(&port, "db-port", os.Getenv("DB_PORT"), "Database port")
	flag.StringVar(&db, "db-name", os.Getenv("DB_NAME"), "Database name")
}

type DAO struct {
	DBClient *mongo.Client
}

func NewDAO() (*DAO, error) {

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)

	defer cancel()
	
	clientOptions := options.Client().ApplyURI(fmt.Sprintf("mongodb://%s:%s", host, port))
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		fmt.Println(err)
		return &DAO{}, err
	}
	err = client.Ping(ctx, readpref.Primary())

	if err != nil {
		fmt.Println(err.Error())
		return &DAO{}, err
	}

	fmt.Println("Connected to MongoDB")
	return & DAO{DBClient: client}, nil
}

func (d *DAO) NewDocCollection(collectionName string) *mongo.Collection {
	docCollection := d.DBClient.Database("user").Collection(collectionName)
	return docCollection
}

func (d *DAO) GetDBConnection() (*mongo.Client, error) {
	if d.DBClient != nil {
		return d.DBClient, nil
	}
	return nil, errors.New("could not get Database connection")
}

