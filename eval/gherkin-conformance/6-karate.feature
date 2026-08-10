Feature: dialecte Karate -- tous les pas en `*`

  Background:
    * url 'https://example.invalid'

  Scenario: get all users and then get the first user by id
    * path 'users'
    * method get
    * status 200
    * match response[0] contains { id: 1 }
