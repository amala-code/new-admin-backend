# from fastapi import APIRouter, Body, HTTPException, Depends
# from pydantic import BaseModel
# from twilio.rest import Client
# import random
# import time
# from typing import Dict

# router = APIRouter()

# # Your Twilio credentials
# TWILIO_ACCOUNT_SID = "your_account_sid"
# TWILIO_AUTH_TOKEN = "your_auth_token"
# TWILIO_PHONE_NUMBER = "your_twilio_phone_number"

# # Initialize Twilio client
# twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# # In-memory store for OTP codes (in production, use Redis or another distributed cache)
# otp_store: Dict[str, Dict] = {}

# class PhoneLookup(BaseModel):
#     phone: str

# class OtpVerification(BaseModel):
#     phone: str
#     otp: str

# # Step 1: Request OTP for a phone number
# @router.post("/member/request-otp")
# async def request_otp(payload: PhoneLookup = Body(...)):
#     phone = payload.phone
    
#     # Check if the phone number exists in your database first
#     member = members_collection.find_one({"phone": phone})
#     if not member:
#         # We return a success message anyway to prevent phone number enumeration
#         return {"message": "If the phone number exists, an OTP has been sent."}
    
#     # Generate a 6-digit OTP
#     otp = ''.join(random.choices('0123456789', k=6))
    
#     # Store OTP with expiration time (5 minutes)
#     otp_store[phone] = {
#         "otp": otp,
#         "expires_at": time.time() + 300  # 5 minutes from now
#     }
    
#     # Send OTP via Twilio
#     try:
#         message = twilio_client.messages.create(
#             body=f"Your verification code is: {otp}. It will expire in 5 minutes.",
#             from_=TWILIO_PHONE_NUMBER,
#             to=phone
#         )
#         return {"message": "If the phone number exists, an OTP has been sent."}
#     except Exception as e:
#         # Log the error for debugging but don't expose it to the client
#         print(f"Error sending OTP: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to send OTP")

# # Step 2: Verify OTP and return member info
# @router.post("/member/verify-otp", response_model=dict)
# async def verify_otp_and_get_member(payload: OtpVerification = Body(...)):
#     phone = payload.phone
#     submitted_otp = payload.otp
    
#     # Check if there's an OTP for this phone number
#     if phone not in otp_store:
#         raise HTTPException(status_code=400, detail="No OTP requested for this number or OTP expired")
    
#     otp_data = otp_store[phone]
    
#     # Check if OTP has expired
#     if time.time() > otp_data["expires_at"]:
#         # Remove expired OTP
#         del otp_store[phone]
#         raise HTTPException(status_code=400, detail="OTP has expired")
    
#     # Verify OTP
#     if otp_data["otp"] != submitted_otp:
#         raise HTTPException(status_code=400, detail="Invalid OTP")
    
#     # OTP is valid, remove it from store to prevent reuse
#     del otp_store[phone]
    
#     # Return member data
#     member = members_collection.find_one({"phone": phone})
#     if not member:
#         raise HTTPException(status_code=404, detail="Member not found")
    
#     member["_id"] = str(member["_id"])
#     return member





# import React, { useState, useEffect } from 'react';
# import { RecaptchaVerifier, signInWithPhoneNumber } from 'firebase/auth';

# const PhoneVerification = () => {
#   // States for authentication flow
#   const [phoneNumber, setPhoneNumber] = useState('');
#   const [otp, setOtp] = useState('');
#   const [verificationId, setVerificationId] = useState('');
#   const [isPhoneSubmitted, setIsPhoneSubmitted] = useState(false);
#   const [isVerified, setIsVerified] = useState(false);
#   const [loading, setLoading] = useState(false);
#   const [error, setError] = useState('');
  
#   // User data after verification
#   const [userData, setUserData] = useState(null);

#   // Initialize recaptcha when component mounts
#   useEffect(() => {
#     if (!window.recaptchaVerifier) {
#       window.recaptchaVerifier = new RecaptchaVerifier('recaptcha-container', {
#         'size': 'invisible',
#       }, auth);
#     }
#   }, []);

#   // Handle phone number submission
#   const handlePhoneSubmit = async (e) => {
#     e.preventDefault();
#     setLoading(true);
#     setError('');
    
#     try {
#       const formattedPhone = phoneNumber.startsWith('+') ? phoneNumber : `+${phoneNumber}`;
#       const confirmationResult = await signInWithPhoneNumber(
#         auth, 
#         formattedPhone,
#         window.recaptchaVerifier
#       );
#       setVerificationId(confirmationResult.verificationId);
#       setIsPhoneSubmitted(true);
#       setLoading(false);
#     } catch (error) {
#       setError(`Error sending OTP: ${error.message}`);
#       setLoading(false);
#     }
#   };

#   // Handle OTP verification
#   const handleVerifyOtp = async (e) => {
#     e.preventDefault();
#     setLoading(true);
#     setError('');
    
#     try {
#       // Use the OTP and verification ID to confirm the code
#       await confirmationResult.confirm(otp);
#       setIsVerified(true);
      
#       // Fetch user data after verification
#       fetchUserData();
#     } catch (error) {
#       setError(`Invalid OTP: ${error.message}`);
#       setLoading(false);
#     }
#   };

#   // Fetch user data from API after verification
#   const fetchUserData = async () => {
#     try {
#       // Replace with your actual API endpoint
#       const response = await fetch('https://your-api-endpoint.com/user-data');
#       const data = await response.json();
#       setUserData(data);
#       setLoading(false);
#     } catch (error) {
#       setError(`Error fetching user data: ${error.message}`);
#       setLoading(false);
#     }
#   };

#   return (
#     <div className="verification-container">
#       <div id="recaptcha-container"></div>
      
#       <div className="content-wrapper">
#         <div className="left-section">
#           <h2>Welcome Back</h2>
#           <p className="subtitle">Please verify your identity to continue</p>
#           <div className="decoration-element"></div>
#           <div className="info-block">
#             <p>Secure authentication process</p>
#             <p>Your data is protected with end-to-end encryption</p>
#             <p>Quick and easy verification</p>
#           </div>
#         </div>
        
#         <div className="right-section">
#           {!isVerified ? (
#             <>
#               {!isPhoneSubmitted ? (
#                 <form onSubmit={handlePhoneSubmit} className="form-container">
#                   <h3>Phone Verification</h3>
#                   <p>Enter your phone number to receive a verification code</p>
                  
#                   <div className="input-group">
#                     <label htmlFor="phone">Phone Number</label>
#                     <input
#                       type="tel"
#                       id="phone"
#                       value={phoneNumber}
#                       onChange={(e) => setPhoneNumber(e.target.value)}
#                       placeholder="+1234567890"
#                       required
#                     />
#                   </div>
                  
#                   <button type="submit" className="submit-btn" disabled={loading}>
#                     {loading ? 'Sending...' : 'Send OTP'}
#                   </button>
#                 </form>
#               ) : (
#                 <form onSubmit={handleVerifyOtp} className="form-container">
#                   <h3>Enter OTP</h3>
#                   <p>We've sent a verification code to {phoneNumber}</p>
                  
#                   <div className="input-group">
#                     <label htmlFor="otp">Verification Code</label>
#                     <input
#                       type="text"
#                       id="otp"
#                       value={otp}
#                       onChange={(e) => setOtp(e.target.value)}
#                       placeholder="Enter 6-digit code"
#                       required
#                     />
#                   </div>
                  
#                   <button type="submit" className="submit-btn" disabled={loading}>
#                     {loading ? 'Verifying...' : 'Verify OTP'}
#                   </button>
                  
#                   <button 
#                     type="button" 
#                     className="back-btn"
#                     onClick={() => setIsPhoneSubmitted(false)}
#                   >
#                     Back
#                   </button>
#                 </form>
#               )}
#             </>
#           ) : (
#             <div className="user-data-container">
#               <h3>Your Profile</h3>
              
#               {loading ? (
#                 <p>Loading your data...</p>
#               ) : userData ? (
#                 <div className="user-details">
#                   <div className="detail-item">
#                     <span>Name:</span>
#                     <p>{userData.name}</p>
#                   </div>
#                   <div className="detail-item">
#                     <span>Email:</span>
#                     <p>{userData.email}</p>
#                   </div>
#                   <div className="detail-item">
#                     <span>Phone:</span>
#                     <p>{userData.phone || phoneNumber}</p>
#                   </div>
#                   {userData.additionalInfo && (
#                     <div className="detail-item">
#                       <span>Additional Info:</span>
#                       <p>{userData.additionalInfo}</p>
#                     </div>
#                   )}
#                 </div>
#               ) : (
#                 <p>No data available</p>
#               )}
#             </div>
#           )}
          
#           {error && <p className="error-message">{error}</p>}
#         </div>
#       </div>
#     </div>
#   );
# };

# // CSS styles
# const styles = `
# .verification-container {
#   display: flex;
#   justify-content: center;
#   align-items: center;
#   min-height: 100vh;
#   background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
#   font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
# }

# .content-wrapper {
#   display: flex;
#   width: 900px;
#   min-height: 500px;
#   background: white;
#   border-radius: 20px;
#   overflow: hidden;
#   box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
# }

# .left-section {
#   flex: 1;
#   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#   color: white;
#   padding: 40px;
#   display: flex;
#   flex-direction: column;
#   justify-content: center;
# }

# .left-section h2 {
#   font-size: 2.5rem;
#   margin-bottom: 10px;
#   font-weight: 300;
# }

# .subtitle {
#   font-size: 1.1rem;
#   margin-bottom: 30px;
#   opacity: 0.8;
# }

# .decoration-element {
#   width: 60px;
#   height: 4px;
#   background: rgba(255, 255, 255, 0.7);
#   margin-bottom: 30px;
# }

# .info-block {
#   margin-top: 40px;
# }

# .info-block p {
#   margin: 15px 0;
#   display: flex;
#   align-items: center;
# }

# .info-block p:before {
#   content: '✓';
#   margin-right: 10px;
#   font-weight: bold;
# }

# .right-section {
#   flex: 1;
#   padding: 40px;
#   display: flex;
#   flex-direction: column;
#   justify-content: center;
# }

# .form-container {
#   width: 100%;
# }

# .form-container h3 {
#   font-size: 1.8rem;
#   color: #333;
#   margin-bottom: 10px;
# }

# .form-container p {
#   color: #777;
#   margin-bottom: 30px;
# }

# .input-group {
#   margin-bottom: 20px;
# }

# .input-group label {
#   display: block;
#   margin-bottom: 8px;
#   color: #555;
#   font-weight: 500;
# }

# .input-group input {
#   width: 100%;
#   padding: 12px 15px;
#   border: 1px solid #ddd;
#   border-radius: 8px;
#   font-size: 16px;
#   transition: border-color 0.3s;
# }

# .input-group input:focus {
#   border-color: #667eea;
#   outline: none;
# }

# .submit-btn {
#   width: 100%;
#   padding: 14px;
#   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#   color: white;
#   border: none;
#   border-radius: 8px;
#   font-size: 16px;
#   cursor: pointer;
#   transition: opacity 0.3s;
# }

# .submit-btn:hover {
#   opacity: 0.9;
# }

# .submit-btn:disabled {
#   background: #ccc;
#   cursor: not-allowed;
# }

# .back-btn {
#   background: transparent;
#   border: none;
#   color: #667eea;
#   margin-top: 15px;
#   cursor: pointer;
#   text-align: center;
#   width: 100%;
# }

# .error-message {
#   color: #e74c3c;
#   margin-top: 15px;
#   text-align: center;
# }

# .user-data-container {
#   width: 100%;
# }

# .user-details {
#   margin-top: 20px;
# }

# .detail-item {
#   padding: 15px 0;
#   border-bottom: 1px solid #eee;
#   display: flex;
#   align-items: center;
# }

# .detail-item:last-child {
#   border-bottom: none;
# }

# .detail-item span {
#   font-weight: 500;
#   width: 120px;
#   color: #555;
# }

# .detail-item p {
#   margin: 0;
#   color: #333;
# }
# `;

# // Add styles to the document
# const styleElement = document.createElement('style');
# styleElement.innerHTML = styles;
# document.head.appendChild(styleElement);

# export default PhoneVerification;

# import { initializeApp } from "firebase/app";
# import { getAuth } from "firebase/auth";

# // Your web app's Firebase configuration
# // Replace with your actual config from the Firebase console
# const firebaseConfig = {
#   apiKey: "YOUR_API_KEY",
#   authDomain: "YOUR_AUTH_DOMAIN",
#   projectId: "YOUR_PROJECT_ID",
#   storageBucket: "YOUR_STORAGE_BUCKET",
#   messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
#   appId: "YOUR_APP_ID"
# };

# // Initialize Firebase
# const app = initializeApp(firebaseConfig);
# const auth = getAuth(app);

# export { auth };

# import { auth } from './firebase';
# import { RecaptchaVerifier, signInWithPhoneNumber } from 'firebase/auth';

# // Then in your component:
# const confirmationResult = await signInWithPhoneNumber(
#   auth, 
#   formattedPhone,
#   window.recaptchaVerifier
# );

# 9. Handle Production Environment
# For production:

# Set up your domain in the Firebase console under Authentication → Settings → Authorized domains
# Make sure your app is properly deployed to that domain