package main

import (
	"context"
	"github.com/redis/go-redis/v9"
)

func main() {
	fetch()
}


var ctx = context.Background()
func fetch() {
//     usd_curr := make(map[string]float32)
//     url := "https://www.cbr-xml-daily.ru/daily_utf8.xml"
//     var curr Currency
//     var arr Array
//     resp, err := http.Get(url)
//     if err != nil {
//         fmt.Fprintf(os.Stderr, "fetch: %v\n", err)
//         os.Exit(1)
//     }
//     if err != nil {
//         fmt.Fprintf(os.Stderr, "fetch: чтение %s: %v\n", url, err)
//         os.Exit(1)
//     }
    rdb := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379",
        Password: "", // no password set
        DB:       0,  // use default DB
    })
    err := rdb.HMSet(ctx, "price-param", map[string]interface{}{
        "USD": 89.7026,
        "input_price": 0.50,
        "output_price": 1.50,
    }).Err()

    if err != nil {
        panic(err)
    }

}

//     d := xml.NewDecoder(resp.Body)
//     for t, _ := d.Token(); t != nil; t, _ = d.Token() {
//     }

//         switch se := t.(type) {
//
//     }
//         case xml.StartElement:
//             if se.Name.Local == "Name" {
//                 d.DecodeElement(&food, &se)
//                 fmt.Printf("%s", se.Attr)
//             }
//         }

//     curr := new(Currency)
//     errr := xml.Unmarshal([]byte(b), curr)
//     if errr != nil {
//         fmt.Printf("error curr parsing: %v", errr)
//         return
//     }
//     fmt.Println(curr.Curr)
//     for _, value := range curr.Curr {
//         fmt.Printf("NumCode: %s \n", value.NumCode)
//         fmt.Printf("CharCode: %s \n", value.CharCode)
//         fmt.Printf("Nominal: %s \n", value.Nominal)
//         fmt.Printf("Name: %s \n", value.Name)
//         fmt.Printf("Value: %s \n", value.Value)
//         fmt.Printf("VunitRate: %s \n", value.VunitRate)
//         fmt.Printf("---\n")
//     }

//     XMLName xml.Name `xml:"ValCurs"`
//     Curr []struct {
//         NumCode string `xml:"NumCode"`
//         CharCode string `xml:"CharCode"`
//         Nominal string `xml:"Nominal"`
//         Name string `xml:"Name"`
//         Value string `xml:"Value"`
//         VunitRate string `xml:"VunitRate"`
//     } `xml:"Valute"`