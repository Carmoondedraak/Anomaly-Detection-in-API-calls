package repositories

import (
	"catalogue/database"
	"catalogue/models"
	"context"
	"github.com/labstack/gommon/log"
	"go.mongodb.org/mongo-driver/bson"
	"strings"
)


func FindSocksWithTags() ([]*models.Sock, error) {
	sockResults, err := FetchSocks()
	if err != nil {
		log.Errorf("Error fetching socks", err)
	}

	tagsResults, err := FetchTags()
	if err != nil {
		log.Errorf("Error fetching tags", err)
	}

	sockTagsResults, err := FetchSockTags()
	if err != nil {
		log.Errorf("Error fetching sockTags", err)
	}
	tagsNameMap := make(map[int]string)
	for _, v := range tagsResults {
		tagsNameMap[v.ID] = v.Name
	}

	tagsMap := make(map[string][]string)
	for _, t := range sockTagsResults {
		tagsMap[t.SockID] = append(tagsMap[t.SockID], tagsNameMap[t.TagID])
	}

	for _, v := range sockResults {
		for k, e := range tagsMap {
			if v.ID == k {
				v.TagString = strings.Join(e[:], ",")
				v.Tags = e
			}
		}
		v.ImageURL = append(v.ImageURL, v.ImageURL_1, v.ImageURL_2)
	}
	return sockResults, nil
}

func FetchSocks() ([]*models.Sock, error) {
	var socks []*models.Sock

	sockCollection := database.NewDocCollection("sock")
	selector := bson.D{{}}

	cur, err := sockCollection.Find(context.TODO(), selector)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.Sock
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		socks = append(socks, &elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return socks, nil
}

func FindSockById(id string) (models.Sock, error) {
	sockCollection := database.NewDocCollection("sock")
	selector := bson.M{"id": id}

	var result models.Sock

	err := sockCollection.FindOne(context.TODO(), selector).Decode(&result)
	if err != nil {
		log.Fatal(err)
	}
	return result, nil
}

func FetchTags() ([]*models.Tag, error) {
	var tags []*models.Tag

	tagCollection := database.NewDocCollection("tag")
	selector := bson.D{{}}

	cur, err := tagCollection.Find(context.TODO(), selector)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.Tag
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		tags = append(tags, &elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return tags, nil
}

func FetchSockTags() ([]*models.SockTag, error) {
	tagCollection := database.NewDocCollection("sock_tag")

	var sockTags []*models.SockTag

	selector := bson.D{{}}

	cur, err := tagCollection.Find(context.TODO(), selector)

	if err != nil {
		log.Fatal(err)
	}

	for cur.Next(context.TODO()) {
		var elem models.SockTag
		err := cur.Decode(&elem)
		if err != nil {
			log.Fatal(err)
		}
		sockTags = append(sockTags, &elem)
	}

	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	cur.Close(context.TODO())
	return sockTags, nil
}
