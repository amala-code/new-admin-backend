from os import environ
import razorpay
SECRET_KEY=environ.get('SECRET_KEY')
DB_PASSWORD=environ.get('DB_PASSWORD')
DB_USERNAME=environ.get('DB_USERNAME')
RAZORPAY_KEY_ID=environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET=environ.get('RAZORPAY_KEY_SECRET')
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
