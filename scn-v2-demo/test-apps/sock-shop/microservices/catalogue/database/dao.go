package database

import (
	"context"
	"fmt"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"log"
)


func NewMongoClient() (*mongo.Client, error){
	mongoDbUrl := "mongodb://catalogue-db:27017"
	clientOptions := options.Client().ApplyURI(mongoDbUrl)
	client, err := mongo.Connect(context.TODO(), clientOptions)
	if err != nil {
		log.Fatalln(err)
		return nil, err
	}
	fmt.Println("Connected to MongoDB")
	return client, nil
}


func NewDocCollection(collectionName string) *mongo.Collection {
	client, err := NewMongoClient()
	if err != nil {
		log.Fatalln(err)
		return nil
	}
	docCollection := client.Database("catalogue").Collection(collectionName)

	return docCollection
}

func GetDbHealth() error {

	client, err := NewMongoClient()

	if err != nil {
		log.Fatal(err)
		return err
	}

	err = client.Ping(context.TODO(), nil)

	if err != nil {
		log.Fatal(err)
		return err
	}
	return nil
}

func InitDB() {
	client, err := NewMongoClient()
	if err != nil {
		log.Fatal(err)
	}

	//###################### CREATE ####################
	sockCollection := client.Database("catalogue").Collection("sock")

	socksDoc := []interface{}{
		bson.D{
			{"id", "6d62d909-f957-430e-8689-b5129c0bb75e"},
			{"name", "Weave special"},
			{"description", "Limited issue Weave socks."},
			{"image_url_1", "/catalogue/images/weave1.jpg"},
			{"image_url_2", "/catalogue/images/weave2.jpg"},
			{"price", 17.15},
			{"count", 33},
		},
		bson.D{
			{"id", "a0a4f044-b040-410d-8ead-4de0446aec7e"},
			{"name", "Nerd leg"},
			{"description", "For all those leg lovers out there. A perfect example of a swivel chair trained calf. Meticulously trained on a diet of sitting and Pina Coladas. Phwarr..."},
			{"image_url_1", "/catalogue/images/bit_of_leg_1.jpeg"},
			{"image_url_2", "/catalogue/images/bit_of_leg_2.jpeg"},
			{"price", 7.99},
			{"count", 115},
		},
		bson.D{
			{"id", "808a2de1-1aaa-4c25-a9b9-6612e8f29a38"},
			{"name", "Crossed"},
			{"description", "A mature sock, crossed, with an air of nonchalance."},
			{"image_url_1", "/catalogue/images/cross_1.jpeg"},
			{"image_url_2", "/catalogue/images/cross_2.jpeg"},
			{"price", 17.32},
			{"count", 738},
		},
		bson.D{
			{"id", "510a0d7e-8e83-4193-b483-e27e09ddc34d"},
			{"name", "SuperSport XL"},
			{"description", "Ready for action. Engineers: be ready to smash that next bug! Be ready, with these super-action-sport-masterpieces. This particular engineer was chased away from the office with a stick."},
			{"image_url_1", "/catalogue/images/puma_1.jpeg"},
			{"image_url_2", "/catalogue/images/puma_2.jpeg"},
			{"price", 15.00},
			{"count", 820},
		},
		bson.D{
			{"id", "03fef6ac-1896-4ce8-bd69-b798f85c6e0b"},
			{"name", "Holy"},
			{"description", "Socks fit for a Messiah. You too can experience walking in water with these special edition beauties. Each hole is lovingly proggled to leave smooth edges. The only sock approved by a higher power."},
			{"image_url_1", "/catalogue/images/holy_1.jpeg"},
			{"image_url_2", "/catalogue/images/holy_2.jpeg"},
			{"price", 99.99},
			{"count", 1},
		},
		bson.D{
			{"id", "d3588630-ad8e-49df-bbd7-3167f7efb246"},
			{"name", "YouTube.sock"},
			{"description", "We were not paid to sell this sock. It's just a bit geeky."},
			{"image_url_1", "/catalogue/images/youtube_1.jpeg"},
			{"image_url_2", "/catalogue/images/youtube_2.jpeg"},
			{"price", 10.99},
			{"count", 801},
		},
		bson.D{
			{"id", "819e1fbf-8b7e-4f6d-811f-693534916a8b"},
			{"name", "Figueroa"},
			{"description", "enim officia aliqua excepteur esse deserunt quis aliquip nostrud anim."},
			{"image_url_1", "/catalogue/images/WAT.jpg"},
			{"image_url_2", "/catalogue/images/WAT2.jpg"},
			{"price", 14.00},
			{"count", 808},
		},
		bson.D{
			{"id", "zzz4f044-b040-410d-8ead-4de0446aec7e"},
			{"name", "Classic"},
			{"description", "Keep it simple."},
			{"image_url_1", "/catalogue/images/classic.jpg"},
			{"image_url_2", "/catalogue/images/classic2.jpg"},
			{"price", 12.00},
			{"count", 127},
		},
		bson.D{
			{"id", "3395a43e-2d88-40de-b95f-e00e1502085b"},
			{"name", "Colourful"},
			{"description", "proident occaecat irure et excepteur labore minim nisi amet irure"},
			{"image_url_1", "/catalogue/images/colourful_socks.jpg"},
			{"image_url_2", "/catalogue/images/colourful_socks.jpg"},
			{"price", 18.00},
			{"count", 438},
		},
		bson.D{
			{"id", "837ab141-399e-4c1f-9abc-bace40296bac"},
			{"name", "Cat socks"},
			{"description", "consequat amet cupidatat minim laborum tempor elit ex consequat in."},
			{"image_url_1", "/catalogue/images/catsocks.jpg"},
			{"image_url_2", "/catalogue/images/catsocks2.jpg"},
			{"price", 15.00},
			{"count", 175},
		},
	}

	sockResult, err := sockCollection.InsertMany(context.Background(), socksDoc)

	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Inserted a Single Document: ", sockResult)

	//TAGS
	tagCollection := client.Database("catalogue").Collection("tag")

	tagsDoc := []interface{}{
		bson.D{{"id", 1}, {"name", "brown"}},
		bson.D{{"id", 2}, {"name", "geek"}},
		bson.D{{"id", 3}, {"name", "formal"}},
		bson.D{{"id", 4}, {"name", "blue"}},
		bson.D{{"id", 5}, {"name", "skin"}},
		bson.D{{"id", 6}, {"name", "red"}},
		bson.D{{"id", 7}, {"name", "action"}},
		bson.D{{"id", 8}, {"name", "sport"}},
		bson.D{{"id", 9}, {"name", "black"}},
		bson.D{{"id", 10}, {"name", "magic"}},
		bson.D{{"id", 11}, {"name", "green"}},
	}
	tagResult, err := tagCollection.InsertMany(context.Background(), tagsDoc)

	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Inserted a Single Document: ", tagResult)

	/*var sock bson.M
	  if err = sockCollection.FindOne(context.TODO(), bson.M{}).Decode(&sock); err != nil {
	  	log.Fatal(err)
	  }
	  fmt.Println(sock)
	*/
	//SOCKS_TAGS
	sockTagCollection := client.Database("catalogue").Collection("sock_tag")

	socksTagDoc := []interface{}{
		bson.D{{"sock_id", "6d62d909-f957-430e-8689-b5129c0bb75e"}, {"tag_id", 2}},
		bson.D{{"sock_id", "6d62d909-f957-430e-8689-b5129c0bb75e"}, {"tag_id", 9}},
		bson.D{{"sock_id", "a0a4f044-b040-410d-8ead-4de0446aec7e"}, {"tag_id", 4}},
		bson.D{{"sock_id", "a0a4f044-b040-410d-8ead-4de0446aec7e"}, {"tag_id", 5}},
		bson.D{{"sock_id", "808a2de1-1aaa-4c25-a9b9-6612e8f29a38"}, {"tag_id", 4}},
		bson.D{{"sock_id", "808a2de1-1aaa-4c25-a9b9-6612e8f29a38"}, {"tag_id", 6}},
		bson.D{{"sock_id", "808a2de1-1aaa-4c25-a9b9-6612e8f29a38"}, {"tag_id", 7}},
		bson.D{{"sock_id", "808a2de1-1aaa-4c25-a9b9-6612e8f29a38"}, {"tag_id", 3}},
		bson.D{{"sock_id", "510a0d7e-8e83-4193-b483-e27e09ddc34d"}, {"tag_id", 8}},
		bson.D{{"sock_id", "510a0d7e-8e83-4193-b483-e27e09ddc34d"}, {"tag_id", 9}},
		bson.D{{"sock_id", "510a0d7e-8e83-4193-b483-e27e09ddc34d"}, {"tag_id", 3}},
		bson.D{{"sock_id", "03fef6ac-1896-4ce8-bd69-b798f85c6e0b"}, {"tag_id", 10}},
		bson.D{{"sock_id", "d3588630-ad8e-49df-bbd7-3167f7efb246"}, {"tag_id", 2}},
		bson.D{{"sock_id", "d3588630-ad8e-49df-bbd7-3167f7efb246"}, {"tag_id", 3}},
		bson.D{{"sock_id", "819e1fbf-8b7e-4f6d-811f-693534916a8b"}, {"tag_id", 3}},
		bson.D{{"sock_id", "819e1fbf-8b7e-4f6d-811f-693534916a8b"}, {"tag_id", 11}},
		bson.D{{"sock_id", "819e1fbf-8b7e-4f6d-811f-693534916a8b"}, {"tag_id", 4}},
		bson.D{{"sock_id", "zzz4f044-b040-410d-8ead-4de0446aec7e"}, {"tag_id", 1}},
		bson.D{{"sock_id", "zzz4f044-b040-410d-8ead-4de0446aec7e"}, {"tag_id", 11}},
		bson.D{{"sock_id", "3395a43e-2d88-40de-b95f-e00e1502085b"}, {"tag_id", 1}},
		bson.D{{"sock_id", "3395a43e-2d88-40de-b95f-e00e1502085b"}, {"tag_id", 4}},
		bson.D{{"sock_id", "837ab141-399e-4c1f-9abc-bace40296bac"}, {"tag_id", 1}},
		bson.D{{"sock_id", "837ab141-399e-4c1f-9abc-bace40296bac"}, {"tag_id", 11}},
		bson.D{{"sock_id", "837ab141-399e-4c1f-9abc-bace40296bac"}, {"tag_id", 3}},
	}
	sockTagResult, err := sockTagCollection.InsertMany(context.Background(), socksTagDoc)

	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Inserted a Single Document: ", sockTagResult)

	var sock bson.M
	if err = sockCollection.FindOne(context.TODO(), bson.M{}).Decode(&sock); err != nil {
		log.Fatal(err)
	}
	fmt.Println(sock)

}
