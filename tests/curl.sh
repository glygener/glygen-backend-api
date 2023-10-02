#PORT="8082"
PORT="4442"
#PORT="4042"


ACCESS="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2OTU5MzA3MTIsIm5iZiI6MTY5NTkzMDcxMiwianRpIjoiY2ExMjQ2YzYtMjNhZi00ZTM4LTljZWMtMTA0MjkwNzM3NmZkIiwiZXhwIjoxNjk2MDE3MTEyLCJpZGVudGl0eSI6Im15Z2x5Z2VuQGdtYWlsLmNvbSIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyIsImNzcmYiOiJkZjhiYTgyZi01N2FmLTQzMDQtYWRlZi0wNGFhY2UxYzA2ODIifQ.R9mnA_BJYtv5s302kna5ys4KrpcywqHpBcnO9UG4_F0"

#curl -H "Content-Type: application/json" http://localhost:$PORT/auth/login/ -d '{"email": "myglygen@gmail.com", "password":"g1l2y3g4e5n!"}'


curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/event/addnew/ -d '{"title":"TEST EVENT","description": "some description","start_date": "09/28/2023 15:30:00","end_date": "09/29/2023 15:30:00","venue": "some venue","url": "some url","url_name": "some url name","visibility": "visible"}'



#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userinfo/ -d '{"email": "myglygen@gmail.com"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userupdate/ -d '{"email":"myglygen@gmail.com","access":"write", "status":1, "password":"g1l2y3g4e5n!"}'
#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userdelete/ -d '{"email":"james.bond@gmail.com"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/addnew/ -d '{"url":"https://www.youtube.com/watch?v=W13gi7nVCWc"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/list/ -d '{}'


#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/delete/ -d '{"id":"64931ca224c1a2ab95ae0e03"}'
