import os
from dashboard.mails.gapi.gmail_utils import get_email
from dashboard.mails.definitions import logger


def rules():
    # before time, should receive email
    # no errors/exceptions
    # task list
    pass


def refine(mail):
    logger.info(f"Refining mail for {mail['subject']}")
    # ticket, status, flag, service, client
    if mail['subject'].startswith('INFO:'):
        mail['flag'] = 'success'
        return mail
    # keep going
    return


def write_to_db(mail):
    # write to db
    # filter on subject, add tags, connect to jira ticket, update status
    # create ticket for new event
    pass


def db_init():
    # loop over all emails and store in DB
    pass


def update_db():
    # loop over all unread emails and store in DB
    pass


if __name__ == '__main__':
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for mail in get_email():
        refine(mail)
    # get_email()
