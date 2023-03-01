package services

import (
	_ "wwwin-github.cisco.com/scn-demo/test-app/microservices/user/db"
	models "wwwin-github.cisco.com/scn-demo/test-app/microservices/user/models"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/repositories"
)

type ICardService interface {
	PostCard(card models.Card) (string, error)
	GetCard(cardID string) (*models.Card, error)
	GetCards() ([]*models.Card, error)
	GetCustomerCards(customerID string) ([]*models.Card, error)
	Delete(id string) error
}

type cardService struct {
	CardRepository repositories.ICardRepository
}

func NewCardService(repository *repositories.ICardRepository) ICardService {
	return &cardService{CardRepository: *repository}
}

func (c *cardService) PostCard(card models.Card) (string, error) {
	cardId, err := c.CardRepository.SaveCard(&card)
	return cardId, err
}

func (c *cardService) GetCard(cardID string) (*models.Card, error) {
	card, err := c.CardRepository.GetCardById(cardID)
	card.AddLinks()
	return card, err
}

func (c *cardService) GetCards() ([]*models.Card, error) {
	cards, err := c.CardRepository.GetAllCards()
	for _, card := range cards {
		card.AddLinks()
	}
	return cards, err
}

func (c *cardService) GetCustomerCards(customerID string) ([]*models.Card, error) {
	cards, err := c.CardRepository.GetCardsByCustomerId(customerID)
	for _, card := range cards {
		card.AddLinks()
	}
	return cards, err
}

func (c *cardService) Delete(id string) error {
	return c.CardRepository.DeleteCard(id)
}
