ACCESS="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NzQ1OTI5NTksIm5iZiI6MTY3NDU5Mjk1OSwianRpIjoiOTcwNjNjYmItZmI0MC00MTk5LThiOTEtYWU1OGZhNTA0MTQ1IiwiZXhwIjoxNjc0Njc5MzU5LCJpZGVudGl0eSI6InJ5a2Foc2F5QGd3dS5lZHUiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJjc3JmIjoiODFjMDU4MTEtYjc4Ni00MGZiLWFjZWUtMmI2ZWIzNWMyMmRhIn0.AR5f_PpQVcZaJqTzce9FapCjbROBvo8_kTqKNyTmZm4"


#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/auth/userinfo/ -d '{"email": "james.bond@gmail.com"}'

curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/video/addnew/ -d '{"url":"https://www.youtube.com/embed/xyV5v5nRm6A?rel=0"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/video/delete/ -d '{"id":"63d04393d634c7d21067b32e"}'

