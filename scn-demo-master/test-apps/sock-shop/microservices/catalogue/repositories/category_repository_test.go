package repositories

import (
	"catalogue/database"
	"fmt"
	"github.com/stretchr/testify/assert"
	"log"
	"testing"
)

func TestFetchSocks(t *testing.T) {
	//SOCKS
	socks, err := FetchSocks()

	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(socks)
}

func TestFetchSockById(t *testing.T) {
	//Socks by ID
	sock, err := FindSockById("510a0d7e-8e83-4193-b483-e27e09ddc34d")

	if err != nil {
		log.Fatal(err)
	}
	assert.NotNil(t, sock.ID)
	assert.Equal(t, "510a0d7e-8e83-4193-b483-e27e09ddc34d", sock.ID)
}

func TestFetchTags(t *testing.T) {

	//TAGS
	tags, err := FetchTags()

	if err != nil {
		log.Fatal(err)
	}
	assert.Equal(t, 11, len(tags))
}

func TestFetchSocksTags(t *testing.T) {
	tags, err := FetchSockTags()

	if err != nil {
		log.Fatal(err)
	}
	assert.Equal(t, 26, len(tags))
}

func TestPopulateDB(t *testing.T) {
     database.InitDB()
}