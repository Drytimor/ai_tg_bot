package main

import (
	"context"
	"github.com/redis/go-redis/v9"
	"os"
	"time"
	"net/http"
	"encoding/xml"
	"io"
	"gopkg.in/yaml.v2"
	"io/ioutil"
	"log"
	"strings"
)

func main() {
	fetch()
}

var ctx = context.Background()

func fetch() {
    url := "https://www.cbr-xml-daily.ru/daily_utf8.xml"
    resp, err := http.Get(url)
    if err != nil {
        log.Fatalf("fetch: %v", err)
    }

    curr := parse_xml(resp.Body)
    conf_pr := price_param(curr)
    cache(curr, conf_pr["input_price"], conf_pr["output_price"])
}

type Element struct {
    Valute []Valute `xml:"Valute"`
}

type Valute struct {
    NumCode string `xml:"NumCode"`
    CharCode string `xml:"CharCode"`
    Nominal string `xml:"Nominal"`
    Name string `xml:"Name"`
    Value string `xml:"Value"`
    VunitRate string `xml:"VunitRate"`
}

func parse_xml(b io.ReadCloser) (string) {
    var (
        el Element
        val Valute
        curr string
    )
    dec := xml.NewDecoder(b)
    for {
        tok, err := dec.Token()
        if err == io.EOF {
            break
        } else if err != nil {
            log.Fatalf("parse_xml: %v", err)
        }
        switch tok := tok.(type) {
        case xml.StartElement:
            if tok.Name.Local == "Valute" {
                dec.DecodeElement(&val, &tok)
                el.Valute = append(el.Valute, val)
            }
        }
    }
    for _, v := range el.Valute {
        if v.CharCode == "USD" {
            curr = v.Value
            break
        }
    }
    curr = strings.Replace(curr, ",", ".", 1)
    return curr
}


const yaml_price = "price.yaml"


func price_param(curr string) (map[string]string) {

    conf := make(map[string]string)

    buf, err_r := ioutil.ReadFile(yaml_price)
    if err_r != nil {
        log.Fatalf("чтение yaml %v", err_r)
    }

    err_des := yaml.Unmarshal(buf, &conf)
    if err_des != nil {
        log.Fatalf("сериализация yaml %v", err_des)
    }

    conf["currency"] = curr

    buf, err_ser := yaml.Marshal(&conf)
    if err_ser != nil {
        log.Fatalf("десериализация yaml %v", err_ser)
    }

    err_w := ioutil.WriteFile(yaml_price, buf, 0644)
    if err_w != nil {
        log.Fatalf("запись в yaml %v", err_w)
    }
    return conf
}


func cache(curr string, inp_pr string, out_pr string) {
    rdb := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379",
        Password: "",
        DB:       0,
    })
    hash := map[string]interface{} {
        "currency": curr,
        "input_price": inp_pr,
        "output_price": out_pr,
    }
    err := rdb.HMSet(ctx, "price-param", hash).Err()
    if err != nil {
        log.Fatalf("запись в редис: %v", err)
    }

    rdb.Expire(ctx, "price-param", 25*time.Hour)
}
