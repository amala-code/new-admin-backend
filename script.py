import pandas as pd
import requests
import json
import re
import os
from datetime import datetime
from typing import Optional, Tuple

# Configuration
API_BASE_URL = "http://0.0.0.0:8002"
CSV_FILE_PATH = "IKS Members List.xlsx"
ERROR_LOG_FILE = "failed_uploads_log.xlsx"

def is_empty_value(value) -> bool:
    """Check if a value is empty, None, NaN, or just whitespace"""
    if pd.isna(value):
        return True
    if value is None:
        return True
    if str(value).strip() in ['', 'nan', 'NaN', 'NULL', 'null', 'None']:
        return True
    return False

def clean_string(value) -> Optional[str]:
    """Clean string value and return None if empty"""
    if is_empty_value(value):
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None

def parse_date(date_str) -> Optional[int]:
    """Parse date string and return year"""
    if is_empty_value(date_str):
        return None
    
    try:
        # Handle pandas datetime objects
        if isinstance(date_str, pd.Timestamp):
            return date_str.year
        
        date_str = str(date_str).strip()
        
        # Try different date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y", 
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%d.%m.%Y",
            "%Y",
            "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.year
            except ValueError:
                continue
        
        # If it's already a year (4 digits)
        if date_str.isdigit() and len(date_str) == 4:
            year = int(date_str)
            if 1900 <= year <= 2030:
                return year
        
        print(f"Warning: Could not parse date '{date_str}'")
        return None
        
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None

def clean_phone_number(phone) -> str:
    """Clean phone number - remove spaces, dashes, etc."""
    if is_empty_value(phone):
        return ""
    
    # Handle numeric values from Excel
    if isinstance(phone, (int, float)):
        phone_str = str(int(phone))
    else:
        phone_str = str(phone).strip()
    
    # Remove common separators
    phone_clean = re.sub(r'[-\s\(\)\+]', '', phone_str)
    # Remove any non-digit characters except +
    phone_clean = re.sub(r'[^\d\+]', '', phone_clean)
    
    return phone_clean

def extract_email_and_blood_group(combined_field) -> Tuple[Optional[str], Optional[str]]:
    """Extract email and blood group from combined field"""
    if is_empty_value(combined_field):
        return None, None
    
    text = str(combined_field).strip()
    
    # Extract email using regex
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text, re.IGNORECASE)
    email = email_match.group(0) if email_match else None
    
    # Extract blood group
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    blood_group = None
    
    text_upper = text.upper()
    for bg in blood_groups:
        if bg in text_upper:
            blood_group = bg
            break
    
    return email, blood_group

def get_column_value(row, possible_names):
    """Get value from row using possible column names"""
    for name in possible_names:
        if name in row.index and not is_empty_value(row.get(name)):
            return row.get(name)
    return None

def create_member_data(row) -> dict:
    """Create member data dictionary from Excel row"""
    
    # Handle Membership No. -> ID mapping
    membership_no = None
    possible_id_columns = [
        "Member  ship No.",

    ]
    
    membership_no = get_column_value(row, possible_id_columns)
    if membership_no is not None:
        if isinstance(membership_no, (int, float)):
            membership_no = str(int(membership_no))
        else:
            membership_no = clean_string(membership_no)
    
    # Handle Name field
    name = get_column_value(row, [
        "Name of the Member",
        "Name",
        "Member Name",
        "Full Name"
    ])
    name = clean_string(name) if name else ""
    
    # Handle Address field
    address = get_column_value(row, [
        "Address",
        "Full Address",
        "Residential Address"
    ])
    address = clean_string(address) if address else ""
    
    # Handle Phone/Mobile field
    phone = get_column_value(row, [
        "Mobile",
        "Phone",
        "Contact",
        "Mobile No.",
        "Phone No."
    ])
    phone = clean_phone_number(phone)
    
    # Handle Date of Joining
    joining_date = get_column_value(row, [
        "Date of Joining",
        "Joining Date",
        "Join Date",
        "DOJ"
    ])
    year_of_joining = parse_date(joining_date)
    
    # Handle Area
    area = get_column_value(row, [
        "Area",
        "Location",
        "District"
    ])
    area = clean_string(area)
    
    # Handle City
    city = get_column_value(row, [
        "City",
        "Town"
    ])
    city = clean_string(city)
    
    # Handle Res.No.
    res_no = get_column_value(row, [
        "Res.No.",
        "Residence No.",
        "Res No",
        "Home No."
    ])
    res_no = clean_string(res_no)
    
    # Handle Remarks
    remarks = get_column_value(row, [
        "Remarks",
        "Notes",
        "Comments"
    ])
    remarks = clean_string(remarks)
    
    # Extract email and blood group from combined field
    email_blood_field = get_column_value(row, [
        "Email Blood Group",
        "Email & Blood Group",
        "Email/Blood Group",
        "Email",
        "Blood Group"
    ])
    
    if email_blood_field:
        email, blood_group = extract_email_and_blood_group(email_blood_field)
    else:
        # Try separate email and blood group columns
        email = clean_string(get_column_value(row, ["Email", "Email ID", "E-mail"]))
        blood_group = clean_string(get_column_value(row, ["Blood Group", "Blood Type", "BG"]))
    
    # Create base member data
    member_data = {
        "id": membership_no or "",
        "name": name,
        "address": address,
        "email": email or "placeholder@example.com",
        "phone": phone or "",
        "year_of_joining": year_of_joining,
        "area": area,
        "city": city,
        "res_no": res_no,
        "blood_grp": blood_group,
        "remarks": remarks,
        # Default values for required fields
        "amount_paid_total": 0.0,
        "member_true": True,
        "amount_paid_registration": 0.0,
        "amount_paid_subscription": 0.0,
        "amount_subscription": False
    }
    
    # Remove None values for optional fields (keep required fields even if empty)
    required_fields = {"id", "name", "address", "email", "phone"}
    cleaned_data = {}
    
    for key, value in member_data.items():
        if key in required_fields:
            # Keep required fields even if empty string
            cleaned_data[key] = value if value is not None else ""
        elif value is not None:
            # Only include optional fields if they have values
            cleaned_data[key] = value
    
    return cleaned_data

def upload_member(member_data: dict) -> Tuple[bool, str]:
    """Upload a single member to the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/register_member",
            json=member_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            return False, error_msg
            
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def validate_member_data(member_data: dict) -> Tuple[bool, str]:
    """Validate member data before sending to API"""
    # Check required fields
    required_fields = ["id", "name"]
    
    for field in required_fields:
        if field not in member_data:
            return False, f"Missing required field: {field}"
        
        # For ID field, allow empty string but warn
        if field == "id" and not member_data[field]:
            return False, f"Empty ID field"
        elif field != "id" and not member_data[field]:
            return False, f"Missing required field: {field}"
    
    # Validate email format
    email = member_data["email"]
    if email != "placeholder@example.com":
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        if not re.match(email_pattern, email):
            return False, f"Invalid email format: {email}"
    
    return True, "Valid"

def read_excel_file(file_path: str):
    """Read Excel file with proper handling"""
    try:
        # Try reading with openpyxl engine (default for .xlsx)
        df = pd.read_excel(file_path, engine='openpyxl')
        print("File read successfully with openpyxl engine")
        return df
    except Exception as e1:
        try:
            # Try with xlrd engine for older .xls files
            df = pd.read_excel(file_path, engine='xlrd')
            print("File read successfully with xlrd engine")
            return df
        except Exception as e2:
            try:
                # Try without specifying engine
                df = pd.read_excel(file_path)
                print("File read successfully with default engine")
                return df
            except Exception as e3:
                print(f"Error reading Excel file:")
                print(f"  openpyxl: {e1}")
                print(f"  xlrd: {e2}")
                print(f"  default: {e3}")
                raise e3

def save_failed_records_to_excel(failed_records):
    """Save failed records to Excel file with error details"""
    if not failed_records:
        print("✅ No failed records to save - all uploads were successful!")
        return
    
    try:
        # Get current working directory
        current_dir = os.getcwd()
        full_path = os.path.join(current_dir, ERROR_LOG_FILE)
        
        print(f"\n📁 Saving failed records to Excel...")
        print(f"   File path: {full_path}")
        
        # Create DataFrame from failed records
        df_failed = pd.DataFrame(failed_records)
        
        # Add timestamp column
        df_failed['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Reorder columns to put error info at the front
        error_columns = ['Error_Type', 'Error_Message', 'Member_ID', 'Timestamp']
        other_columns = [col for col in df_failed.columns if col not in error_columns]
        df_failed = df_failed[error_columns + other_columns]
        
        # Save to Excel with explicit engine
        with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
            df_failed.to_excel(writer, sheet_name='Failed_Records', index=False)
            
            # Add a summary sheet
            summary_data = {
                'Summary': ['Total Failed Records', 'Validation Errors', 'Upload Errors', 'Processing Errors'],
                'Count': [
                    len(failed_records),
                    sum(1 for r in failed_records if r.get('Error_Type') == 'Validation Error'),
                    sum(1 for r in failed_records if r.get('Error_Type') == 'Upload Error'),
                    sum(1 for r in failed_records if r.get('Error_Type') == 'Processing Exception')
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        # Verify file was created
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"✅ SUCCESS! Failed records saved to Excel")
            print(f"   📍 Location: {full_path}")
            print(f"   📊 Records: {len(failed_records)}")
            print(f"   💾 File size: {file_size} bytes")
            print(f"   📝 Sheets: 'Failed_Records' and 'Summary'")
            
            # Try to open the file location in file explorer (Windows)
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(current_dir)
                    print(f"   📂 Opened folder in file explorer")
            except:
                pass
        else:
            print(f"❌ ERROR: File was not created at {full_path}")
        
    except PermissionError as e:
        print(f"❌ Permission Error: {e}")
        print("   Try closing Excel if the file is open, or run as administrator")
        
        # Try alternative filename
        alt_filename = f"failed_uploads_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        alt_path = os.path.join(current_dir, alt_filename)
        try:
            df_failed = pd.DataFrame(failed_records)
            df_failed.to_excel(alt_path, index=False)
            print(f"✅ Saved with alternative name: {alt_path}")
        except Exception as e2:
            print(f"❌ Alternative save failed: {e2}")
            
    except Exception as e:
        print(f"❌ Error saving failed records to Excel: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Fallback: save as CSV in the same directory
        try:
            csv_file = ERROR_LOG_FILE.replace('.xlsx', '.csv')
            csv_path = os.path.join(os.getcwd(), csv_file)
            
            df_failed = pd.DataFrame(failed_records)
            df_failed.to_csv(csv_path, index=False)
            
            if os.path.exists(csv_path):
                print(f"✅ Fallback: Saved as CSV instead")
                print(f"   📍 Location: {csv_path}")
            else:
                print(f"❌ CSV fallback also failed")
                
        except Exception as e2:
            print(f"❌ CSV fallback error: {e2}")

def main():
    try:
        print("Starting Excel upload process...")
        
        # Read the Excel file
        try:
            df = read_excel_file(CSV_FILE_PATH)
        except Exception as e:
            print(f"Error reading file: {e}")
            print("\nMake sure you have the required packages installed:")
            print("pip install openpyxl xlrd")
            return
        
        print(f"Successfully loaded file with {len(df)} records")
        print("Columns found:", df.columns.tolist())
        
        # Clean column names - remove extra spaces
        df.columns = df.columns.str.strip()
        print("Cleaned columns:", df.columns.tolist())
        
        print("\nFirst few rows preview:")
        print(df.head())
        
        # Process only the first record for testing
        if len(df) == 0:
            print("No data found in file")
            return
            
        print(f"\n{'='*50}")
        print("PROCESSING FIRST RECORD FOR TESTING")
        print(f"{'='*50}")
        
        test_record = df.iloc[0]
        print("\nRaw record data:")
        for col in df.columns:
            value = test_record[col]
            print(f"  {col}: '{value}' (type: {type(value).__name__})")
        
        # Create member data
        member_data = create_member_data(test_record)
        
        print(f"\nProcessed member data:")
        print(json.dumps(member_data, indent=2, default=str))
        
        # Validate data
        is_valid, validation_msg = validate_member_data(member_data)
        if not is_valid:
            print(f"\nValidation Error: {validation_msg}")
            return
        
        print(f"\nValidation: {validation_msg}")
        
        # Upload the member
        print(f"\nUploading member to API...")
        success, result = upload_member(member_data)
        
        if success:
            print(f"\n✅ SUCCESS! Member uploaded successfully:")
            print(json.dumps(result, indent=2))
        else:
            print(f"\n❌ ERROR uploading member:")
            print(result)
            
        print(f"\n{'='*50}")
        print("TEST COMPLETED")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")
        import traceback
        traceback.print_exc()

def upload_all_records():
    """Function to upload ALL records with error logging"""
    try:
        # Read the file
        df = read_excel_file(CSV_FILE_PATH)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        print(f"\n🚀 PROCESSING ALL RECORDS")
        print(f"Total records in file: {len(df)}")
        print(f"Working directory: {os.getcwd()}")
        print(f"{'='*60}")
        
        success_count = 0
        error_count = 0
        failed_records = []
        
        for index, row in df.iterrows():
            record_num = index + 1
            print(f"\n[{record_num}/{len(df)}] Processing record...")
            
            # Create member data
            try:
                member_data = create_member_data(row)
                member_id = member_data.get('id', 'NO_ID')
                
                print(f"   Member ID: {member_id}")
                
                # Validate data
                is_valid, validation_msg = validate_member_data(member_data)
                if not is_valid:
                    print(f"   ❌ Validation Error: {validation_msg}")
                    
                    # Add to failed records with original data
                    failed_record = row.to_dict()
                    failed_record['Error_Type'] = 'Validation Error'
                    failed_record['Error_Message'] = validation_msg
                    failed_record['Member_ID'] = member_id
                    failed_record['Row_Number'] = record_num
                    failed_record['Processed_Data'] = json.dumps(member_data, default=str)
                    failed_records.append(failed_record)
                    
                    error_count += 1
                    continue
                
                # Upload member
                success, result = upload_member(member_data)
                
                if success:
                    print(f"   ✅ SUCCESS: Record uploaded")
                    success_count += 1
                        
                else:
                    print(f"   ❌ Upload Error: {str(result)[:100]}...")
                    
                    # Add to failed records with original data
                    failed_record = row.to_dict()
                    failed_record['Error_Type'] = 'Upload Error'
                    failed_record['Error_Message'] = str(result)
                    failed_record['Member_ID'] = member_id
                    failed_record['Row_Number'] = record_num
                    failed_record['Processed_Data'] = json.dumps(member_data, default=str)
                    failed_records.append(failed_record)
                    
                    error_count += 1
                    
            except Exception as e:
                print(f"   ❌ Processing Exception: {str(e)}")
                
                # Add to failed records with original data
                failed_record = row.to_dict()
                failed_record['Error_Type'] = 'Processing Exception'
                failed_record['Error_Message'] = str(e)
                failed_record['Member_ID'] = 'Could not extract'
                failed_record['Row_Number'] = record_num
                failed_record['Processed_Data'] = 'Could not process'
                failed_records.append(failed_record)
                
                error_count += 1
        
        # Save failed records to Excel
        save_failed_records_to_excel(failed_records)
        
        print(f"\n{'='*60}")
        print(f"🎯 FINAL SUMMARY")
        print(f"{'='*60}")
        print(f"📊 Total records processed: {len(df)}")
        print(f"✅ Successful uploads: {success_count}")
        print(f"❌ Failed uploads: {error_count}")
        print(f"📈 Success rate: {(success_count/len(df)*100):.1f}%")
        
        if failed_records:
            print(f"\n📋 Failed records have been saved to '{ERROR_LOG_FILE}'")
            print("   Review the errors and fix the data before retrying.")
            
            print(f"\n📊 Error breakdown:")
            validation_errors = sum(1 for r in failed_records if r.get('Error_Type') == 'Validation Error')
            upload_errors = sum(1 for r in failed_records if r.get('Error_Type') == 'Upload Error')
            processing_errors = sum(1 for r in failed_records if r.get('Error_Type') == 'Processing Exception')
            
            print(f"   🔍 Validation errors: {validation_errors}")
            print(f"   🌐 Upload errors: {upload_errors}")
            print(f"   ⚠️  Processing errors: {processing_errors}")
        else:
            print(f"\n🎉 PERFECT! All {success_count} records uploaded successfully!")
        
        print(f"\n{'='*60}")
        
    except Exception as e:
        print(f"Error in upload_all_records: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    
    upload_all_records()


