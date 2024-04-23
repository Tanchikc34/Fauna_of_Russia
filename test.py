from requests import get

print(get('http://127.0.0.1:8040/api/v2/users').json())
print(get('http://127.0.0.1:8040/api/v2/users/1').json())