#PORT="8082"
PORT="4442"

ACCESS="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NzkzNTAyNDYsIm5iZiI6MTY3OTM1MDI0NiwianRpIjoiNGVkMjkxMDAtM2Q5OS00ZmIyLWJhYzktNmIzMjY1OTY4ZDFmIiwiZXhwIjoxNjc5NDM2NjQ2LCJpZGVudGl0eSI6InJ5a2Foc2F5QGd3dS5lZHUiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJjc3JmIjoiMmI5Yzc2OTctNDZjMi00YWFmLThlYTktNWNmYzhiZGMxNzQwIn0.0XOMJBnz2sKU45vKgWzVrX-cRffWMV80lg15wexASKw"

curl -H "Content-Type: application/json" http://localhost:$PORT/auth/login/ -d '{"email": "myglygen@gmail.com", "password":"g1l2y3g4e5n!"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userinfo/ -d '{"email": "myglygen@gmail.com"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userupdate/ -d '{"email":"myglygen@gmail.com","access":"write", "status":1, "password":"g1l2y3g4e5n!"}'
#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userdelete/ -d '{"email":"james.bond@gmail.com"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/addnew/ -d '{"url":"https://www.youtube.com/embed/xyV5v5nRm6A?rel=0"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/delete/ -d '{"id":"63d04393d634c7d21067b32e"}'

