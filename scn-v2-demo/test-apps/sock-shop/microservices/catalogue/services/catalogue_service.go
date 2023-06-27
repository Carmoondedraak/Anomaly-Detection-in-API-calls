package services

import (
	"catalogue/database"
	"catalogue/models"
	"catalogue/repositories"
	"github.com/labstack/gommon/log"
	"github.com/stroiman/go-automapper"
	"strings"
	"time"
)

func List(tags []string, order string, pageNum, pageSize int) ([]models.SockDTO, error) {

	var sockDTOList []models.SockDTO

	if len(tags) == 0 {
		return sockDTOList, nil
	}else {
		socks, err := repositories.FindSocksWithTags()

		if err != nil {
			log.Errorf("Error fetching socks with tags", err)
		}

		for i, s := range socks {
			socks[i].ImageURL = []string{s.ImageURL_1, s.ImageURL_2}
			socks[i].Tags = strings.Split(s.TagString, ",")
		}

		var filteredSocks []*models.Sock

		for _, s := range socks{
			for _, t := range s.Tags {
				_, found := findItem(t, tags)
				if found {
					filteredSocks = append(filteredSocks, s)
				}
			}
		}
		filteredSocks = cut(filteredSocks, pageNum, pageSize)
		sockDTOList = mapList(filteredSocks)
	}
	return sockDTOList, nil
}

func Count(tags []string) (int, error) {
	var socks []*models.Sock
	sockResults, err := repositories.FindSocksWithTags()
	if err != nil {
		log.Errorf("Error fetching tags", err)
	}
	for _, v := range sockResults{
		for _, x := range tags {
			_, found := findItem(x, v.Tags)
			if found {
				socks = append(socks, v)
			}
		}
	}

	return len(socks), nil
}

func Get(id string) (models.SockDTO, error) {
	socks, err := repositories.FindSocksWithTags()
	for _, v := range socks{
		if id == v.ID {
			var sockDTO models.SockDTO
			automapper.Map(v, &sockDTO)
			return sockDTO, nil
		}
	}
	return models.SockDTO{}, err
}

func Tags() ([]string, error) {
	tagsResults, err := repositories.FetchTags()
	if err != nil {
		log.Errorf("Error fetching tags", err)
	}
	var tags []string

	for _, v := range tagsResults {
		tags = append(tags, v.Name)
	}

	return tags, nil
}

func Health() []models.Health {
		var health []models.Health
		dbStatus := "OK"

		err := database.GetDbHealth()
		if err != nil {
			dbStatus = "err"
	}

		app := models.Health{Service: "catalogue", Status: "OK", Time: time.Now().String()}
		db := models.Health{Service: "catalogue-db", Status: dbStatus, Time: time.Now().String()}

		health = append(health, app)
		health = append(health, db)

		return health
}



func findItem(val string, slice []string) (int, bool) {
	for i, item := range slice {
		if item == val {
			return i, true
		}
	}
	return -1, false
}

func mapList(socks []*models.Sock) []models.SockDTO {
	var sockDTOs []models.SockDTO
	automapper.Map(socks, &sockDTOs)
	return sockDTOs
}

func cut(socks []*models.Sock, pageNum, pageSize int) []*models.Sock {
	if pageNum == 0 || pageSize == 0 {
		return []*models.Sock{} // pageNum is 1-indexed
	}
	start := (pageNum * pageSize) - pageSize
	if start > len(socks) {
		return []*models.Sock{}
	}
	end := pageNum * pageSize
	if end > len(socks) {
		end = len(socks)
	}
	return socks[start:end]
}

func contains(s []string, e string) bool {
	for _, a := range s {
		if a == e {
			return true
		}
	}
	return false
}