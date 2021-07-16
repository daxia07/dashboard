import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(1, parent_dir)


if __name__ == '__main__':
    from backend.utils.gmail_utils import get_email
    get_email()
