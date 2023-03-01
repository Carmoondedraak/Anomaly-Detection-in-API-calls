package services

// service.go contains the definition and implementation (business logic) of the
// user service. Everything here is agnostic to the transport (HTTP).

import (
	"log"

	models "wwwin-github.cisco.com/scn-demo/test-app/microservices/user/models"
	"wwwin-github.cisco.com/scn-demo/test-app/microservices/user/repositories"
)

// IAddressService is the user service, providing operations for users to login, register, and retrieve customer information.
type IAddressService interface {
	PostAddress(addressDTO models.Address) (string, error)
	GetAddress(addressId string) (*models.Address, error)
	GetAddresses(customerID string) ([]*models.Address, error)
	GetAllAddresses() ([]*models.Address, error)
	DeleteAddress(addressId string) error
}

type addressService struct {
	AddressRepository repositories.IAddressRepository
}

func NewAddressService(repository *repositories.IAddressRepository) IAddressService {
	return &addressService{AddressRepository: *repository}
}

func (a *addressService) PostAddress(address models.Address) (string, error) {
	addressId, err := a.AddressRepository.SaveAddress(&address)
	return addressId, err
}

func (a *addressService) GetAddress(addressId string) (*models.Address, error) {
	address, err := a.AddressRepository.GetAddressById(addressId)
	if err != nil {
		log.Fatal(err)
	}
	address.AddLinks()
	return address, nil
}

func (a *addressService) GetAllAddresses() ([]*models.Address, error) {
	addresses, err := a.AddressRepository.GetAllAddresses()
	for _, a := range addresses {
		a.AddLinks()
	}
	return addresses, err
}

func (a *addressService) GetAddresses(customerID string) ([]*models.Address, error) {
	addresses, err := a.AddressRepository.GetAddressesByCustomerId(customerID)
	for _, a := range addresses {
		a.AddLinks()
	}
	return addresses, err
}

func (a *addressService) DeleteAddress(id string) error {
	return a.DeleteAddress(id)
}
