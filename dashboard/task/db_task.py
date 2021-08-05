import os


def write_to_db(mail):
    # write to db 
    pass


def db_init():
    # loop over all emails and store in DB
    pass


def update_db():
    # loop over all unread emails and store in DB
    pass


if __name__ == '__main__':
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if parent_dir not in os.sys.path:
        os.sys.path.insert(1, parent_dir)
    try:
        from dashboard.task.utils.gmail_utils import get_email
        from dashboard.task.definitions import logger
    except ImportError as e:
        print('Error while importing packages', e)
    for mail in get_email():
        print(mail)
        break
    # get_email()
