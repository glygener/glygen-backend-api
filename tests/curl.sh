ACCESS="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NzYwNTM3OTIsIm5iZiI6MTY3NjA1Mzc5MiwianRpIjoiMzEyMjhiMzgtODY5Yi00NzA1LWJiY2EtZjIwYzQ3MWUyYjVhIiwiZXhwIjoxNjc2MTQwMTkyLCJpZGVudGl0eSI6InJ5a2Foc2F5QGd3dS5lZHUiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJjc3JmIjoiYjY2ZWUwMDktMzFmNi00YTZmLWExZTktYTA1NTk0MTllMWVmIn0.F-vCQms6Bm53TNzaP61JBFHp9_RzeX-zAslJ3pRpSzc"


#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/auth/userinfo/ -d '{"email": "james.bond@gmail.com"}'

curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/video/addnew/ -d '{"url":"https://www.youtube.com/embed/xyV5v5nRm6A?rel=0"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/video/delete/ -d '{"id":"63d04393d634c7d21067b32e"}'

