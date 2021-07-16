import base64
import os
from datetime import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from task.utils import PACK_DIR
from task.definitions import logger

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.path.join(PACK_DIR, 'token.json')):
        creds = Credentials.from_authorized_user_file(os.path.join(PACK_DIR, 'token.json'), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(PACK_DIR, 'credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.path.join(PACK_DIR, 'token.json'), 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def parse_subject(headers):
    # Look for Subject and Sender Email in the headers
    for d in headers:
        if d['name'] == 'Subject':
            subject = d['value']
            subject = subject.replace('FW: ', '').replace('[SPAM]', '').strip()
            return subject
    raise ValueError('Empty subject found')


def parse_body(payload, service, msg):
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
    text = decoded_data.decode('utf').strip()
    # remove the FW header and keep raw data
    # soup = BeautifulSoup(decoded_data, "lxml")
    # body = soup.body()
    text_ele = text.split('\r\n')
    item = dict()
    header_idx = 0
    for idx, ele in enumerate(text_ele):
        if ele.startswith('From: '):
            item['sender'] = ele.replace('From: ', '')
        elif ele.startswith('Sent: '):
            sent_time = ele.replace('Sent: ', '')
            dt_elements = sent_time.split(',')
            if len(dt_elements) == 2:
                dt = datetime.strptime(f'{dt_elements[1].strip()}', '%d %B %Y %I:%M %p')
            else:
                dt_md = dt_elements[1].strip()
                dt_year = dt_elements[2].strip().split(' ')[0]
                dt_hms = dt_elements[2].strip().split(' ')[1] + ' ' + dt_elements[2].strip().split(' ')[2]
                dt = datetime.strptime(f'{dt_md} {dt_year} {dt_hms}', '%B %d %Y %I:%M:%S %p')
            item['sent'] = dt
        elif ele.startswith('Subject: '):
            item['subject'] = ele.replace('Subject: ', '')
            header_idx = idx
            break
    item['body'] = '\r\n'.join(text_ele[header_idx+1:]).strip()
    return item


def get_email(service=None, maxResults=200, query="is:unread label:INBOX from:gbst.com"):
    if service is None:
        service = get_service()
    # https://support.google.com/mail/answer/7190
    # from:someuser@example.com rfc822msgid:<somemsgid@example.com> is:unread ?q=in:sent after:1388552400 before:1391230800
    result = service.users().messages().list(maxResults=maxResults,
                                             userId='me',
                                             q=query)\
        .execute()
    messages = result.get('messages')
    next_page_token = result.get('nextPageToken')
    while next_page_token:
        n_result = service.users().messages()\
            .list(maxResults=maxResults, userId='me', q=query, pageToken=next_page_token)\
            .execute()
        n_messages = n_result.get('messages')
        if not len(n_messages):
            break
        messages += n_messages
        next_page_token = n_result.get('nextPageToken')
    # iterate through all the messages
    for msg in messages:
        # Get the message from its id
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        # Get value of 'payload' from dictionary 'txt'
        payload = txt['payload']
        headers = payload['headers']
        subject = parse_subject(headers)
        # Printing the subject, sender's email and message
        logger.info(f'Subject: {subject}')
        if 'globaldb ---> taxanalyser (uat) copy for security' in subject:
            continue
        # skip uat emails
        body = parse_body(payload, service, msg)
        if subject == 'Tax Analyser Mercer Load (Production)' and 'sender' not in body.keys():
            # special email to skip
            logger.warning(f'Skipping email with no body for {subject}')
        logger.info(f'Body: {body}')
        body['subject'] = subject
        yield body


if __name__ == '__main__':
    for mail in get_email(maxResults=200):
        print(mail)
        # get_email()
