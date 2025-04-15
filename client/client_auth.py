from server_requests import register, login

register(
    username="user7",
    password="forexamplepassword123",
    email="exampleuser7@gmail.com",
    nickname="Daetoya"
)
print("----------------------------")
login(
    username="user7",
    password="forexamplepassword123"
)
