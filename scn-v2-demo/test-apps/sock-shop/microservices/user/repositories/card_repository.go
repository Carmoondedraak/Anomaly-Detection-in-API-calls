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

type ICardRepository interface {
	SaveCard(newCard *models.Card) (string, error)
	GetCardById(id string) (*models.Card, error)
	GetCardByName(name string) (*models.Card, error)
	GetAllCards() ([]*models.Card, error)
	GetCardsByCustomerId(customerId string) ([]*models.Card, error)
	DeleteCard(cardId string) (err error)
}

type cardRepository struct {
	DAO *db.DAO
}

func NewCardRepository(dao *db.DAO) ICardRepository {
	return &cardRepository{DAO: dao}
}

func (c *cardRepository) SaveCard(card *models.Card) (string, error) {
	cardCollection := c.DAO.NewDocCollection("Card")
	result, err := cardCollection.InsertOne(context.TODO(), card)

	if oid, ok := result.InsertedID.(primitive.ObjectID); ok {
		card.ID = oid.Hex()

		update := bson.M{"$set": bson.M{
			"id":      oid.Hex(),
			"longNum": card.LongNum,
			"ccv":     card.CCV,
			"expires": card.Expires,
		},
		}

		_, err := cardCollection.UpdateByID(context.TODO(), oid, update)

		return oid.Hex(), err

	}
	return "", err
}

func (c *cardRepository) GetCardById(id string) (*models.Card, error) {

	cardCollection := c.DAO.NewDocCollection("Card")
	selector := bson.M{"id": id}

	var Card models.Card

	err := cardCollection.FindOne(context.TODO(), selector).Decode(&Card)
	if err != nil {
		log.Fatal(err)
	}
	return &Card, nil
}

func (c *cardRepository) GetCardByName(name string) (*models.Card, error) {

	cardCollection := c.DAO.NewDocCollection("Card")
	selector := bson.M{"name": name}

	var Card models.Card

	err := cardCollection.FindOne(context.TODO(), selector).Decode(&Card)
	if err != nil {
		log.Fatal(err)
	}
	return &Card, nil
}

func (c *cardRepository) GetAllCards() ([]*models.Card, error) {
	var cards []*models.Card

	cardCollection := c.DAO.NewDocCollection("Card")

	selector := bson.D{{}}

	findOptions := options.Find()
	findOptions.SetLimit(50)

	cur, err := cardCollection.Find(context.TODO(), selector, findOptions)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.Card
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		cards = append(cards, &elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return cards, nil
}

func (c *cardRepository) GetCardsByCustomerId(customerId string) ([]*models.Card, error) {
	var cards []*models.Card

	selector := bson.M{"userId": customerId}

	cardCollection := c.DAO.NewDocCollection("Card")

	findOptions := options.Find()
	findOptions.SetLimit(1000)

	cur, err := cardCollection.Find(context.TODO(), selector, findOptions)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.Card
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		cards = append(cards, &elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return cards, nil
}

func (c *cardRepository) DeleteCard(id string) (err error) {
	cardCollection := c.DAO.NewDocCollection("Card")
	res, err := cardCollection.DeleteOne(context.TODO(), bson.M{"_id": id})
	fmt.Println("DeleteOne Result TYPE:", reflect.TypeOf(res))

	if err != nil {
		log.Fatal("DeleteOne() ERROR:", err)
		return err
	}
	return nil
}
