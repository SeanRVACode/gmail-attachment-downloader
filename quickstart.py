import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from icecream import ic
import email

# Remember to delete the file token .json. if these scopes are changed
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels."""

    creds = None

    # The file token.json stores the users access and refresh tokens and is created
    # automatically when the authorization flow completes for the first time

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")
    # if there are no (valid) credentails available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)

            creds = flow.run_local_server(port=0)
            # Save the credentials
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    try:
        # Call the gmail api
        service = build("gmail", "v1", credentials=creds)
        # Query to search for specific email
        query = f"from:{os.getenv('query_address')}"
        results = service.users().messages().list(userId="me", q=query, maxResults=10).execute()
        messages = results.get("messages", [])

        for message in messages:
            message_detail = service.users().messages().get(userId="me", id=message["id"], format="full").execute()
            # Attempt to find attachments

            parts = message_detail["payload"].get("parts", [])
            # Handle multiple attachments
            for part in parts:
                if part.get("filename"):
                    filename = part["filename"]
                    ic(filename)
                    attachment_id = part["body"].get("attachmentId")
                    if attachment_id:
                        ic(f"Found attachment: {filename}")
                        ic(f"Attachment ID: {attachment_id}")

            headers = message_detail["payload"]["headers"]
            subject = [i["value"] for i in headers if i["name"] == "Subject"]
            print(f"Subject: {subject[0] if subject else 'No Subject'}")
    except HttpError as e:
        # TODO (Dev) - handle errors from Gmail API
        print(f"An error occured: {e}")


if __name__ == "__main__":
    main()
