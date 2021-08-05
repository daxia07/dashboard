```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

def setup_credentials():
    key_path = 'gmailsignatureproject-zzz.json'
    API_scopes =['https://www.googleapis.com/auth/gmail.settings.basic',
                 'https://www.googleapis.com/auth/gmail.settings.sharing']
    credentials = service_account.Credentials.from_service_account_file(key_path,scopes=API_scopes)
    return credentials


def test_setup_credentials():
    credentials = setup_credentials()
    assert credentials


def test_fetch_user_info():
    credentials = setup_credentials()
    credentials_delegated = credentials.with_subject("tim@vci.com.au")
    gmail_service = build("gmail","v1",credentials=credentials_delegated)
    addresses = gmail_service.users().settings().sendAs().list(userId='me').execute()
    assert gmail_service
```


### Note:
Make sure that project dir in the path to run programs
```python
import os
parent_dir = 'ROOT'
os.sys.path.insert(1, parent_dir)
```