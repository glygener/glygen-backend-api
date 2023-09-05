PORT="8082"
#PORT="4042"
#PORT="4442"


ACCESS="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2OTM2NzEyMzksIm5iZiI6MTY5MzY3MTIzOSwianRpIjoiM2EzZTFkZmQtMzdhZi00ZDcwLThiNzktMDhjMjI4MTdlZGU0IiwiZXhwIjoxNjkzNzU3NjM5LCJpZGVudGl0eSI6Im15Z2x5Z2VuQGdtYWlsLmNvbSIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyIsImNzcmYiOiI0MTcwNGExMS00NDlmLTQ1MzgtYjkxMS1iNWQzM2I3ZWNiYTkifQ.-N-SgildIIcSb8H05v34prwtWcnIP2bSYHA3PuPjXpg"

#curl -H "Content-Type: application/json" http://localhost:$PORT/auth/login/ -d '{"email": "myglygen@gmail.com", "password":"g1l2y3g4e5n!"}'


curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/event/addnew/ -d '{"title": "some title","description": "some description","start_date": "09/02/2023 12:00:00","end_date": "09/02/2023 12:20:00","venue": "some venue","url": "some url","url_name": "some url name","visibility": "visible"}'



#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userinfo/ -d '{"email": "myglygen@gmail.com"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userupdate/ -d '{"email":"myglygen@gmail.com","access":"write", "status":1, "password":"g1l2y3g4e5n!"}'
#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userdelete/ -d '{"email":"james.bond@gmail.com"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/addnew/ -d '{"url":"https://www.youtube.com/watch?v=W13gi7nVCWc"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/list/ -d '{}'


#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/delete/ -d '{"id":"64931ca224c1a2ab95ae0e03"}'
