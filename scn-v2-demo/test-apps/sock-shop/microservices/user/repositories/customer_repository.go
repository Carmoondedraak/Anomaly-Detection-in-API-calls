package repositories

import (
	"context"
	"fmt"
	"log"
	"reflect"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo/options"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/db"
	models "wwwin-github.cisco.com/scn-demo/test-app/microservices/user/models"
)

type ICustomerRepository interface {
	SaveCustomer(newCustomer *models.Customer) (string, error)
	GetCustomerById(id string) (*models.Customer, error)
	GetCustomerByUserName(username string) (models.Customer, error)
	GetCustomers() (customers []*models.Customer, err error)
	DeleteCustomer(customerId string) (err error)
}

type customerRepository struct {
	DAO *db.DAO
}

func NewCustomerRepository(dao *db.DAO) ICustomerRepository {
	return &customerRepository{DAO: dao}
}

func (c *customerRepository) SaveCustomer(customer *models.Customer) (string, error) {
	customerCollection := c.DAO.NewDocCollection("Customer")
	result, err := customerCollection.InsertOne(context.TODO(), customer)

	if oid, ok := result.InsertedID.(primitive.ObjectID); ok {
		customer.Id = oid.Hex()

		update := bson.M{"$set": bson.M{
			"id":        oid.Hex(),
			"firstName": customer.FirstName,
			"lastName":  customer.LastName,
			"email":     customer.Email,
			"username":  customer.Username,
			"password":  customer.Password,
			"salt":      customer.Salt},
		}

		_, err := customerCollection.UpdateByID(context.TODO(), oid, update)

		return oid.Hex(), err

	}
	return "", err
}

func (c *customerRepository) GetCustomerById(id string) (*models.Customer, error) {

	customerCollection := c.DAO.NewDocCollection("Customer")
	selector := bson.M{"id": id}

	var customer models.Customer

	err := customerCollection.FindOne(context.TODO(), selector).Decode(&customer)
	if err != nil {
		log.Fatal(err)
		return &models.Customer{}, err
	}

	addresses, err := FetchAddresses(id, c.DAO)
	if err != nil {
		log.Fatal("error fetching addresses", err)
		customer.Addresses = make([]models.Address, 0)
	} else {
		customer.Addresses = addresses
	}

	cards, err := FetchCards(id, c.DAO)
	if err != nil {
		log.Fatal("error fetching cards", err)
		customer.Cards = make([]models.Card, 0)
	} else {
		customer.Cards = cards
	}

	return &customer, nil
}

func (c *customerRepository) GetCustomerByUserName(username string) (models.Customer, error) {

	customerCollection := c.DAO.NewDocCollection("Customer")
	selector := bson.M{"username": username}

	var customer models.Customer

	err := customerCollection.FindOne(context.TODO(), selector).Decode(&customer)
	if err != nil {
		log.Fatal(err)
	}

	// addresses, err := FetchAddresses(id, c.DAO)
	// customer.Addresses = addresses

	// cards, err := FetchCards(id, c.DAO)
	// customer.Cards = cards

	return customer, nil
}

func (c *customerRepository) GetCustomers() (units []*models.Customer, err error) {
	var customers []*models.Customer

	selector := bson.D{{}}

	customerCollection := c.DAO.NewDocCollection("Customer")

	findOptions := options.Find()
	findOptions.SetLimit(5)

	cur, err := customerCollection.Find(context.TODO(), selector, findOptions)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.Customer
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		customers = append(customers, &elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return customers, nil
}

func (c *customerRepository) DeleteCustomer(id string) (err error) {
	customerCollection := c.DAO.NewDocCollection("Customer")
	res, err := customerCollection.DeleteOne(context.TODO(), bson.M{"_id": id})
	fmt.Println("DeleteOne Result TYPE:", reflect.TypeOf(res))

	if err != nil {
		log.Fatal("DeleteOne() ERROR:", err)
		return err
	}
	return nil
}

func FetchAddresses(customerId string, dao *db.DAO) ([]models.Address, error) {
	addressCollection := dao.NewDocCollection("Address")

	var addresses []models.Address

	selector := bson.M{"ID": customerId}

	cur, err := addressCollection.Find(context.TODO(), selector)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.Address
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		addresses = append(addresses, elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return addresses, nil
}

func FetchCards(customerId string, dao *db.DAO) ([]models.Card, error) {
	cardCollection := dao.NewDocCollection("Cards")

	var cards []models.Card

	selector := bson.M{"ID": customerId}

	cur, err := cardCollection.Find(context.TODO(), selector)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.Card
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		cards = append(cards, elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return cards, nil
}
