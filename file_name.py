from datetime import datetime
from pytz import timezone, utc
import uuid


def get_pst_time():
    # format
    date_format='%m-%d-%Y-%H-%M-%S'
    # current time in UTC
    date = datetime.now(tz=timezone('US/Eastern'))

    # date = date.astimezone(timezone('US/Pacific'))
    pstDateTime=date.strftime(date_format)
    return pstDateTime

def gen_file_name(extension):
    # check if there is a . at extension... if not add one
    if isinstance(extension, str) and extension[0] != '.':
        extension = '.' + extension
    # return file name
    return str(uuid.uuid1()) + '%' + get_pst_time() + extension


if __name__ == "__main__":
    # simple example
    print(gen_file_name('.txt'))