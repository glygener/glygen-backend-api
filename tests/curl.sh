#PORT="8082"
#PORT="4042"
PORT="4442"


ACCESS="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2ODczNjI0OTgsIm5iZiI6MTY4NzM2MjQ5OCwianRpIjoiNDVkMjRiMGQtZTNhNi00YWZjLTg4YTMtMjcxNjE4MjJlODI1IiwiZXhwIjoxNjg3NDQ4ODk4LCJpZGVudGl0eSI6Im15Z2x5Z2VuQGdtYWlsLmNvbSIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyIsImNzcmYiOiJkNThkYTk1MS1iZTI4LTQxMDgtYjVhOS1jMGViODkzZDIzZjQifQ.XD3V4e6_WHGrEMeWtb5I9aXlWk_wWYfN-RnAC9BVNqA"

#curl -H "Content-Type: application/json" http://localhost:$PORT/auth/login/ -d '{"email": "myglygen@gmail.com", "password":"g1l2y3g4e5n!"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userinfo/ -d '{"email": "myglygen@gmail.com"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userupdate/ -d '{"email":"myglygen@gmail.com","access":"write", "status":1, "password":"g1l2y3g4e5n!"}'
#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/auth/userdelete/ -d '{"email":"james.bond@gmail.com"}'

#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/addnew/ -d '{"url":"https://www.youtube.com/watch?v=W13gi7nVCWc"}'

curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/list/ -d '{}'


#curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:$PORT/video/delete/ -d '{"id":"64931ca224c1a2ab95ae0e03"}'
