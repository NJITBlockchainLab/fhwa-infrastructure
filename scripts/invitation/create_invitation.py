import os
import requests
import qrcode
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
aws_access_key_id = os.getenv("ACCESS_KEY")
aws_secret_access_key = os.getenv("SECRET_KEY")

def get_public_ip():
    try:
        # Using a free API to get the public IP address
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text
        else:
            print("Failed to retrieve IP address. Status code:", response.status_code)
            return None
    except requests.RequestException as e:
        print("Error:", e)
        return None

def create_invitation(public_ip):
    try:
        url = f'http://{public_ip}:8054/connections/create-invitation?auto_accept=true&multi_use=true'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to create invitation. Status code:", response.status_code)
            return None
    except requests.RequestException as e:
        print("Error:", e)
        return None

def upload_to_s3(file_name, bucket, object_name=None):
    try:
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
        if object_name is None:
            object_name = file_name
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"File uploaded successfully to S3 bucket: {bucket}/{object_name}")
    except FileNotFoundError:
        print(f"The file '{file_name}' was not found.")
    except NoCredentialsError:
        print("AWS credentials not found.")

def generate_qr_code(invitation_url):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(invitation_url)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Save the image
    qr_image_path = "invitation.png"
    qr_image.save(qr_image_path)

    print("QR code saved as invitation.png")

def process_invitation():
    public_ip = get_public_ip()
    if public_ip:
        print("Your public IP address is:", public_ip)
        invitation = create_invitation(public_ip)
        if invitation:
            invitation_url = invitation.get('invitation_url')
            print("Invitation URL:", invitation_url)
            generate_qr_code(invitation_url)
        
if __name__ == "__main__":
    if os.path.exists("invitation.png"):
        # Check if the invitation QR code file exists
        print("QR code already exists.")
        reset = input("Do you want to reset it? (Y/N): ").strip().lower()
        if reset == "y":
            os.remove("invitation.png")
            process_invitation()
    else:
        process_invitation()
    upload = input("Do you want to upload the existing QR code to S3? (Y/N): ").strip().lower()
    if upload == "y":
        bucket_name = "fhwa-infrastructure-qr"
        upload_to_s3("invitation.png", bucket_name, object_name="invitation.png")
