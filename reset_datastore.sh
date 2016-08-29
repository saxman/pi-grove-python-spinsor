#!/bin/sh

auth_token=$(cat AUTH_TOKEN)

datastore_url="https://spinsor-b38d3.firebaseio.com/samples/saxman.json?auth=$auth_token"

curl -X DELETE $datastore_url

