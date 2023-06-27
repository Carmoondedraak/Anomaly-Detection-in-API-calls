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
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/models"
)

type IAddressRepository interface {
	SaveAddress(newAddress *models.Address) (string, error)
	GetAddressById(id string) (*models.Address, error)
	GetAddressesByCustomerId(customerId string) ([]*models.Address, error)
	GetAllAddresses() ([]*models.Address, error)
	DeleteAddress(customerId string) (err error)
}

type addressRepository struct {
	DAO *db.DAO
}

func NewAddressRepository(dao *db.DAO) IAddressRepository {
	return &addressRepository{DAO: dao}
}

func (c *addressRepository) SaveAddress(address *models.Address) (string, error) {

	addressCollection := c.DAO.NewDocCollection("Address")
	result, err := addressCollection.InsertOne(context.TODO(), address)

	if oid, ok := result.InsertedID.(primitive.ObjectID); ok {
		address.ID = oid.Hex()

		update := bson.M{"$set": bson.M{
			"id":       oid.Hex(),
			"street":   address.Street,
			"number":   address.Number,
			"city":     address.City,
			"country":  address.Country,
			"postcode": address.PostCode},
		}

		_, err := addressCollection.UpdateByID(context.TODO(), oid, update)

		return oid.Hex(), err

	}
	return "", err
}

func (c *addressRepository) GetAddressById(id string) (*models.Address, error) {

	customerCollection := c.DAO.NewDocCollection("Address")
	selector := bson.M{"id": id}

	var Address models.Address

	err := customerCollection.FindOne(context.TODO(), selector).Decode(&Address)
	if err != nil {
		log.Fatal(err)
	}
	return &Address, nil
}

func (c *addressRepository) GetAddressesByCustomerId(customerId string) ([]*models.Address, error) {
	var addresses []*models.Address

	selector := bson.M{"userId": customerId}

	addressCollection := c.DAO.NewDocCollection("Address")

	findOptions := options.Find()
	findOptions.SetLimit(1000)

	cur, err := addressCollection.Find(context.TODO(), selector, findOptions)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.Address
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		addresses = append(addresses, &elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return addresses, nil
}

func (c *addressRepository) GetAllAddresses() ([]*models.Address, error) {
	var addresses []*models.Address

	addressCollection := c.DAO.NewDocCollection("Address")

	selector := bson.D{{}}

	findOptions := options.Find()
	findOptions.SetLimit(1000)

	cur, err := addressCollection.Find(context.TODO(), selector, findOptions)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.Address
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		addresses = append(addresses, &elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return addresses, nil
}

func (c *addressRepository) DeleteAddress(id string) (err error) {
	customerCollection := c.DAO.NewDocCollection("Address")
	res, err := customerCollection.DeleteOne(context.TODO(), bson.M{"_id": id})
	fmt.Println("DeleteOne Result TYPE:", reflect.TypeOf(res))

	if err != nil {
		log.Fatal("DeleteOne() ERROR:", err)
		return err
	}
	return nil
}
