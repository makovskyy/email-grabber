import logging.config
import os
from handlers import error_handler
from email_hunter.client import EmailHunterClient
from email_hunter.database_manager import *
import traceback

script_path = os.path.dirname(__file__)
path = os.path.join(script_path, 'logging_config.ini')
logging.config.fileConfig(path)
logger = logging.getLogger('root')
category_ids = ["4", "26", "62", "193", "219", "227", "235", "262", "269", "272", "291", "299"]
_client = EmailHunterClient('8ed878188f5d409dd037bbbe08499c2e1b156e55')


@error_handler(logger)
def main():
    for category_id in category_ids:
        rows = get_domains(category_id)
        i = 1
        for chunk in gen_chunk(rows, 100):
            process(chunk, category_id)
            print("Processed domains:{0}, category id: {1}".format(i*100, category_id))
            i += 1


@connector
def process(chunk, category_id, cur=None):
    for row in chunk:
        try:
            response = _client.search(row[0])
            emails_number = response['meta']['results']
            update_domain(row[0], category_id, emails_number, cur)
            if emails_number > 0:
                insert_emails(response['data'], category_id, emails_number, cur)
        except:
            logger.error(traceback.format_exc())
            break


def gen_chunk(iterable, size):
    chunk = []
    for i, line in enumerate(iterable):
        if i % size == 0 and i > 0:
            yield chunk
            del chunk[:]
        chunk.append(line)
    yield chunk


if __name__ == "__main__":
    main()