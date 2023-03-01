package services

// service.go contains the definition and implementation (business logic) of the
// user service. Everything here is agnostic to the transport (HTTP).

import (
	"crypto/sha1"
	"errors"
	"fmt"
	"io"

	models "wwwin-github.cisco.com/scn-demo/test-app/microservices/user/models"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/repositories"
)

var (
	ErrUnauthorized = errors.New("Unauthorized")
)

// ICustomerService is the user service, providing operations for users to login, register, and retrieve customer information.
type ICustomerService interface {
	Login(username, password string) (*models.Customer, error)
	Register(username, password, email, first, last string) (string, error)
	GetCustomer(id string) (*models.Customer, error)
	GetCustomers() ([]*models.Customer, error)
	GetAddressesByCustomerId(customerID string) ([]*models.Address, error)
	GetCardsByCustomerId(customerID string) ([]*models.Card, error)
	DeleteCustomer(id string) error
}

type customerService struct {
	CustomerRepository repositories.ICustomerRepository
	AddressService     IAddressService
	CardService        ICardService
}

// NewCustomerService returns a simple implementation of the Service interface,
func NewCustomerService(repository *repositories.ICustomerRepository, addressService *IAddressService, cardService *ICardService) ICustomerService {
	return &customerService{
		CustomerRepository: *repository,
		AddressService:     *addressService,
		CardService:        *cardService,
	}
}

func (c *customerService) Login(username, password string) (*models.Customer, error) {
	cus, err := c.CustomerRepository.GetCustomerByUserName(username)
	if err != nil {
		return &models.Customer{}, err
	}
	if cus.Password != calculatePassHash(password, cus.Salt) {
		return &models.Customer{}, ErrUnauthorized
	}
	cus.MaskCCs()
	cus.AddLinks()
	cus.IncludeLinks()
	return &cus, nil

}

func (c *customerService) Register(username, password, email, first, last string) (string, error) {
	cus := models.New()
	cus.Username = username
	cus.Password = calculatePassHash(password, cus.Salt)
	cus.Email = email
	cus.FirstName = first
	cus.LastName = last
	customerID, err := c.CustomerRepository.SaveCustomer(&cus)
	return customerID, err
}

func (c *customerService) GetCustomer(id string) (*models.Customer, error) {
	cus, err := c.CustomerRepository.GetCustomerById(id)
	cus.AddLinks()
	cus.IncludeLinks()
	return cus, err
}

func (c *customerService) GetAddressesByCustomerId(customerID string) ([]*models.Address, error) {
	addresses, err := c.AddressService.GetAddresses(customerID)
	if err != nil {
		return nil, err
	}
	if addresses != nil {
		return addresses, nil
	}
	return make([]*models.Address, 0), nil
}

func (c *customerService) GetCardsByCustomerId(customerID string) ([]*models.Card, error) {
	cards, err := c.CardService.GetCustomerCards(customerID)
	if err != nil {
		return nil, err
	}
	if cards != nil {
		return cards, nil
	}
	return make([]*models.Card, 0), nil
}

func (c *customerService) GetCustomers() ([]*models.Customer, error) {
	customers, err := c.CustomerRepository.GetCustomers()
	for _, cus := range customers {
		cus.AddLinks()
		cus.IncludeLinks()
	}
	if err != nil {
		return nil, err
	}
	return customers, nil
}

func (c *customerService) DeleteCustomer(id string) error {
	return c.DeleteCustomer(id)
}

func calculatePassHash(pass, salt string) string {
	h := sha1.New()
	io.WriteString(h, salt)
	io.WriteString(h, pass)
	return fmt.Sprintf("%x", h.Sum(nil))
}
