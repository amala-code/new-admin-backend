# from os import environ
# import razorpay
# SECRET_KEY=environ.get('SECRET_KEY')
# DB_PASSWORD=environ.get('DB_PASSWORD')
# DB_USERNAME=environ.get('DB_USERNAME')
# RAZORPAY_KEY_ID=environ.get('RAZORPAY_KEY_ID')
# RAZORPAY_KEY_SECRET=environ.get('RAZORPAY_KEY_SECRET')
# client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# from os import environ

  

# import razorpay

  

# SECRET_KEY=environ.get('SECRET_KEY')

# DB_PASSWORD=environ.get('DB_PASSWORD')

# DB_USERNAME=environ.get('DB_USERNAME')

# RAZORPAY_KEY_ID=environ.get('RAZORPAY_KEY_ID')

# RAZORPAY_KEY_SECRET=environ.get('RAZORPAY_KEY_SECRET')

  

# client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# from os import environ

  

# SECRET_KEY=environ.get('SECRET_KEY')

  

# DB_PASSWORD=environ.get('DB_PASSWORD')

  

# DB_USERNAME=environ.get('DB_USERNAME')

  

# RAZORPAY_KEY_ID=""

  

# RAZORPAY_KEY_SECRET=""

  

from os import environ

  

import razorpay

  

SECRET_KEY=environ.get('SECRET_KEY',"4e886071d6517dbfa834272209ef4f28373ee8450635576be9f980220928602b")

  

DB_PASSWORD=environ.get('DB_PASSWORD','g70BjA1wsl5risW7')

  

DB_USERNAME=environ.get('DB_USERNAME','IKS')

  

RAZORPAY_KEY_ID="Q5rhl9B82m6NqR"

  

RAZORPAY_KEY_SECRET="your_key_secret"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))