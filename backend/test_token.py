from jose import jwt
import os
from datetime import datetime

SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-jwt-key-change-this-in-production')
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MTIzIiwiZXhwIjoxNzU1Nzc5MDE0fQ.6J13jbEr4u9fY7uxEMlcpzhS-tYK2Zpv4nGOTZfWdW4'

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    print('Token valid:', payload)
    
    # 检查过期时间
    exp_timestamp = payload.get('exp')
    if exp_timestamp:
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        current_datetime = datetime.now()
        print(f'Token expires at: {exp_datetime}')
        print(f'Current time: {current_datetime}')
        print(f'Token expired: {current_datetime > exp_datetime}')
        
except Exception as e:
    print('Token invalid:', e)