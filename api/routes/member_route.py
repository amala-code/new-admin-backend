from bson import ObjectId
from fastapi import Depends, HTTPException, APIRouter, Body, Path,Query
from pydantic import BaseModel
from typing import Optional
from api.model.member_model import Member, MemberUpdate, NonMember
from api.utils.db import members_collection, non_members_collection

router = APIRouter()


class PhoneLookup(BaseModel):
    phone: str


MEMBER_ID_COUNTER = 2000

@router.post("/register_member", response_model=dict)
async def register_member(member: Member):
    # Check for duplicate ID or email
    if members_collection.find_one({"$or": [{"id": member.id}, {"email": member.email}]}):
        raise HTTPException(status_code=400, detail="Member with this ID or email already exists.")
    
    # Generate a new ID and make sure it's a string
    # global MEMBER_ID_COUNTER
    # member.id = str(MEMBER_ID_COUNTER)
    # MEMBER_ID_COUNTER += 1

    # Insert into collection
    result = members_collection.insert_one(member.model_dump())
    return {"message": "Member registered successfully", "member_id": str(result.inserted_id)}

@router.post("/register_new_user_request", response_model=dict)
async def register_member(member: Member):
    # Check for duplicate ID or email
    if members_collection.find_one({"$or": [{"phone": member.phone}, {"email": member.email}]}):
        raise HTTPException(status_code=400, detail="Member with this ID or email already exists.")
    
    # Generate a new ID and make sure it's a string
    global MEMBER_ID_COUNTER
    member.id = str(MEMBER_ID_COUNTER)
    MEMBER_ID_COUNTER += 1

    # Insert into collection
    result = members_collection.insert_one(member.model_dump())
    return {"message": "Member registered successfully", "member_id": str(result.inserted_id)}

@router.post("/member/phone", response_model=dict)
async def get_member_by_phone_body(payload: PhoneLookup = Body(...)):
    phone = payload.phone
    member = members_collection.find_one({
        "phone": phone,
        "member_true": True  # Ensure this condition is met
    })
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found with this phone number and member_true = true.")
    
    member["_id"] = str(member["_id"])
    return {
        "member_id": str(member["_id"]),
        "id": member.get("id"),
        "name": member.get("name")
    }





# @router.put("/member/update/{id}", response_model=dict)
# async def update_member(id: str = Path(...), update_payload: MemberUpdate = Body(...)):
#     updates = {k: v for k, v in update_payload.model_dump().items() if v is not None}

#     if not updates:
#         raise HTTPException(status_code=400, detail="No fields provided to update.")

#     result = members_collection.update_one({"id": id}, {"$set": updates})

#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail=f"Member with id '{id}' not found.")

#     return {"message": "Member updated successfully", "updated_fields": list(updates.keys())}

# @router.get("/all/members", response_model=dict)
# async def get_all_members():
#     members = []
#     for member in members_collection.find():
#         member["_id"] = str(member["_id"])  # Convert ObjectId to string
#         members.append(member)
    
#     return {"members": members}

# @router.get("/members/filter", response_model=dict)
# async def filter_members(
#     member_true: Optional[bool] = Query(None),
#     amount_subscription: Optional[bool] = Query(None)
# ):
#     query = {}

#     if member_true is not None:
#         query["member_true"] = member_true

#     if amount_subscription is not None:
#         query["amount_subscription"] = amount_subscription

#     filtered_members = []
#     for member in members_collection.find(query):
#         member["_id"] = str(member["_id"])
#         filtered_members.append(member)

#     return {"filtered_members": filtered_members}

# @router.get("/non_members", response_model=dict)
# async def get_non_members():
#     members = []
#     for member in members_collection.find({"member_true": False}):
#         member["_id"] = str(member["_id"])  # Convert ObjectId to string
#         members.append(member)
    
#     return {"members": members}


# from fastapi import Request

# @router.get("/members/search", response_model=dict)
# #GET /members/search?phone=1234567890
# async def search_members(request: Request):
#     # Extract query params from URL
#     query_params = dict(request.query_params)

#     if not query_params:
#         raise HTTPException(status_code=400, detail="No search parameters provided.")

#     query = {}

#     for key, value in query_params.items():
#         # Convert booleans and numbers from string if needed
#         if value.lower() == "true":
#             query[key] = True
#         elif value.lower() == "false":
#             query[key] = False
#         elif value.isdigit():
#             query[key] = int(value)
#         else:
#             query[key] = value

#     matched_members = []
#     for member in members_collection.find(query):
#         member["_id"] = str(member["_id"])
#         matched_members.append(member)

#     return {"matched_members": matched_members}

@router.delete("/member/delete/{id}", response_model=dict)
async def delete_member(id: str = Path(...)):
    result = members_collection.delete_one({"id": id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Member with id '{id}' not found.")
    
    return {"message": f"Member with id '{id}' deleted successfully."}


@router.get("/member/{id}", response_model=dict)
async def get_member_by_id(id: str = Path(...)):
    member = members_collection.find_one({"id": id})
    
    if not member:
        raise HTTPException(status_code=404, detail=f"Member with id '{id}' not found.")
    
    # Convert ObjectId to string for JSON serialization
    if "_id" in member:
        member["_id"] = str(member["_id"])
    
#     return member
# @router.get("/members/total-paid", response_model=dict)
# async def get_total_amount_paid():
#     members = list(members_collection.find())

#     total_paid = 0
#     for member in members:
#         total_paid += float(member.get("amount_paid", 0))  # Adjust key if needed

#     return {"total_members": len(members), "total_amount_paid": total_paid}
# @router.get("/members/no-subscription", response_model=list)
# async def get_members_no_subscription():
#     members = list(members_collection.find({"amount_paid_subscription": 0}))
#     for member in members:
#         member["_id"] = str(member["_id"])
#     return members


# @router.get("/members/no-membership", response_model=list)
# async def get_members_no_membership():
#     members = list(members_collection.find({"amount_paid_registration": 0}))
#     for member in members:
#         member["_id"] = str(member["_id"])
#     return members
# @router.get("/members/payment-totals", response_model=dict)
# async def get_payment_totals():
#     members = list(members_collection.find({}))
    
#     total_registration = 0
#     total_subscription = 0

#     for member in members:
#         total_registration += member.get("amount_paid_registration", 0)
#         total_subscription += member.get("amount_paid_subscription", 0)

#     return {
#         "total_registration": total_registration,
#         "total_subscription": total_subscription
#     }


from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from api.conf import SECRET_KEY
from utils.db import ALGORITHM

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.put("/member/update/{id}", response_model=dict)
async def update_member(id: str = Path(...), update_payload: MemberUpdate = Body(...), user=Depends(verify_token)):
    updates = {k: v for k, v in update_payload.model_dump().items() if v is not None}

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    result = members_collection.update_one({"id": id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Member with id '{id}' not found.")

    return {"message": "Member updated successfully", "updated_fields": list(updates.keys())}

@router.get("/all/members", response_model=dict)
async def get_all_members(user=Depends(verify_token)):
    members = []
    for member in members_collection.find():
        member["_id"] = str(member["_id"])
        members.append(member)
    
    return {"members": members}

@router.get("/members/filter", response_model=dict)
async def filter_members(
    member_true: Optional[bool] = Query(None),
    amount_subscription: Optional[bool] = Query(None),
    user=Depends(verify_token)
):
    query = {}

    if member_true is not None:
        query["member_true"] = member_true

    if amount_subscription is not None:
        query["amount_subscription"] = amount_subscription

    filtered_members = []
    for member in members_collection.find(query):
        member["_id"] = str(member["_id"])
        filtered_members.append(member)

    return {"filtered_members": filtered_members}

@router.get("/non_members", response_model=dict)
async def get_non_members(user=Depends(verify_token)):
    members = []
    for member in members_collection.find({"member_true": False}):
        member["_id"] = str(member["_id"])
        members.append(member)
    
    return {"members": members}

@router.get("/members/search", response_model=dict)
async def search_members(request: Request, user=Depends(verify_token)):
    query_params = dict(request.query_params)

    if not query_params:
        raise HTTPException(status_code=400, detail="No search parameters provided.")

    query = {}

    for key, value in query_params.items():
        if value.lower() == "true":
            query[key] = True
        elif value.lower() == "false":
            query[key] = False
        elif value.isdigit():
            query[key] = int(value)
        else:
            query[key] = value

    matched_members = []
    for member in members_collection.find(query):
        member["_id"] = str(member["_id"])
        matched_members.append(member)

    return {"matched_members": matched_members}

# @router.delete("/member/delete/{id}", response_model=dict)
# async def delete_member(id: str = Path(...), user=Depends(verify_token)):
#     result = members_collection.delete_one({"id": id})
    
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail=f"Member with id '{id}' not found.")
    
#     return {"message": f"Member with id '{id}' deleted successfully."}

# @router.get("/member/{id}", response_model=dict)
# async def get_member_by_id(id: str = Path(...), user=Depends(verify_token)):
#     member = members_collection.find_one({"id": id})
    
#     if not member:
#         raise HTTPException(status_code=404, detail=f"Member with id '{id}' not found.")
    
#     if "_id" in member:
#         member["_id"] = str(member["_id"])
    
#     return member

@router.get("/members/total-paid", response_model=dict)
async def get_total_amount_paid(user=Depends(verify_token)):
    members = list(members_collection.find())

    total_paid = 0
    for member in members:
        total_paid += float(member.get("amount_paid", 0))

    return {"total_members": len(members), "total_amount_paid": total_paid}

@router.get("/members/no-subscription", response_model=list)
async def get_members_no_subscription(user=Depends(verify_token)):
    members = list(members_collection.find({"amount_paid_subscription": 0}))
    for member in members:
        member["_id"] = str(member["_id"])
    return members

@router.get("/members/no-membership", response_model=list)
async def get_members_no_membership(user=Depends(verify_token)):
    members = list(members_collection.find({"amount_paid_registration": 0}))
    for member in members:
        member["_id"] = str(member["_id"])
    return members

@router.get("/members/payment-totals", response_model=dict)
async def get_payment_totals(user=Depends(verify_token)):
    members = list(members_collection.find({}))
    
    total_registration = 0
    total_subscription = 0

    for member in members:
        total_registration += member.get("amount_paid_registration", 0)
        total_subscription += member.get("amount_paid_subscription", 0)

    return {
        "total_registration": total_registration,
        "total_subscription": total_subscription
    }



@router.post("/register_non_member_request", response_model=dict)
async def register_non_member(non_member: NonMember):
    from utils.db import non_members_collection
    
    # Prevent duplicate requests
    if non_members_collection.find_one({"$or": [{"phone": non_member.phone}, {"email": non_member.email}]}):
        raise HTTPException(status_code=400, detail="Request with this phone/email already exists.")
    
    result = non_members_collection.insert_one(non_member.model_dump())
    return {"message": "Non-member request submitted successfully", "request_id": str(result.inserted_id)}


@router.post("/approve_non_member/{request_id}", response_model=dict)
async def approve_non_member(request_id: str, user=Depends(verify_token)):
    from utils.db import non_members_collection, members_collection
    
    non_member = non_members_collection.find_one({"_id": ObjectId(request_id)})
    
    if not non_member:
        raise HTTPException(status_code=404, detail="Non-member request not found.")
    
    # Ensure they aren’t already in members
    if members_collection.find_one({"$or": [{"phone": non_member["phone"]}, {"email": non_member["email"]}]}):
        raise HTTPException(status_code=400, detail="Already exists as a member.")
    
    # Move data into members collection
    non_member["member_true"] = True
    result = members_collection.insert_one(non_member)
    
    # Delete from non_members collection
    non_members_collection.delete_one({"_id": ObjectId(request_id)})
    
    return {"message": "Non-member approved and added as member", "member_id": str(result.inserted_id)}


@router.get("/non_member_requests", response_model=dict)
async def get_non_member_requests(user=Depends(verify_token)):
    
    from utils.db import non_members_collection
    
    requests = []
    for req in non_members_collection.find():
        req["_id"] = str(req["_id"])
        requests.append(req)
    
    return {"members": requests}
