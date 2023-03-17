ACCESS="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2Nzg5MTMxOTcsIm5iZiI6MTY3ODkxMzE5NywianRpIjoiY2JlN2ZmZWUtODM0Ni00MDIzLWJmNzUtMjNhYzE1ZTEzZWFiIiwiZXhwIjoxNjc4OTk5NTk3LCJpZGVudGl0eSI6InJ5a2Foc2F5QGd3dS5lZHUiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJjc3JmIjoiNmYyM2JhODAtMzE4Ni00N2Y3LThhMGEtMGJlOWU5OGY5MTY3In0.8BjSRsazF1PqGW7ybMn-UdZnKYT2SQjFRGfHOaVpITM"

curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/auth/userinfo/ -d '{"email": "james.bond@gmail.com"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/auth/userupdate/ -d '{"email":"james.bond@gmail.com","access":"write", "status":1}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/auth/userdelete/ -d '{"email":"james.bond@gmail.com"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/video/addnew/ -d '{"url":"https://www.youtube.com/embed/xyV5v5nRm6A?rel=0"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/video/delete/ -d '{"id":"63d04393d634c7d21067b32e"}'

