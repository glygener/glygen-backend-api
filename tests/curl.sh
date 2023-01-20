ACCESS="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NzQyMzk4MTksIm5iZiI6MTY3NDIzOTgxOSwianRpIjoiNDJiNDQwZTgtZjBjZi00ZGQ4LTg5ODEtNmIzODkyNWI3ZDJlIiwiZXhwIjoxNjc0MzI2MjE5LCJpZGVudGl0eSI6InJ5a2Foc2F5QGd3dS5lZHUiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJjc3JmIjoiNTQ0ODAwYzQtNGY3OC00MmYxLWExMTAtMTQ4OGRlMmUxMTg5In0.L3LOVZ-m-8_GQpRLspqpR5FpSvuDl87iKI9-EJUPHvw"

curl -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" http://localhost:8082/auth/userinfo/ -d '{"email": "james.bond@gmail.com"}'

