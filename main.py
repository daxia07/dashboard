import base64
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_email(service=None):
    if service is None:
        service = get_service()
    # https://support.google.com/mail/answer/7190
    # from:someuser@example.com rfc822msgid:<somemsgid@example.com> is:unread ?q=in:sent after:1388552400 before:1391230800
    result = service.users().messages().list(maxResults=200, userId='me', q="is:unread label:INBOX").execute()
    messages = result.get('messages')
    # iterate through all the messages
    for msg in messages:
        # Get the message from its id
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        # Get value of 'payload' from dictionary 'txt'
        payload = txt['payload']
        headers = payload['headers']

        # Look for Subject and Sender Email in the headers
        for d in headers:
            if d['name'] == 'Subject':
                subject = d['value']
            if d['name'] == 'From':
                sender = d['value']

        # The Body of the message is in Encrypted format. So, we have to decode it.
        # Get the data and decode it with base 64 decoder.
        if 'parts' in payload.keys():
            #
            parts = payload.get('parts')[0]
        else:
            parts = payload
        if 'data' in parts['body'].keys():
            data = parts['body']['data']
        elif 'attachmentId' in parts['body'].keys():
            a_id = parts['body']['attachmentId']
            attachment = service.users().messages().attachments().get(id=a_id, messageId=msg['id'], userId='me').execute()
            data = attachment['data']
        else:
            data = ''
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data)

        # Now, the data obtained is in lxml. So, we will parse
        # it with BeautifulSoup library
        soup = BeautifulSoup(decoded_data, "lxml")
        body = soup.body()

        # Printing the subject, sender's email and message
        print("Subject: ", subject)
        print("From: ", sender)
        print("Message: ", body)
        print('\n')


def main():
    get_email()
    pass

if __name__ == '__main__':
    main()
