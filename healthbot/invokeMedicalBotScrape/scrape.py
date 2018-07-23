from botocore.vendored import requests
import re
import string
import os, logging
from bs4 import BeautifulSoup as bs
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

BUCKET_NAME = 'medicalbot'
FILE_NAME = 'medicalDescription.txt'
#https://github.com/resurrexi/mayo-clinic-scraper
def process():
    body = ""
    letters = list(string.ascii_uppercase)
    for letter in letters:
        r = requests.get('http://www.mayoclinic.org/diseases-conditions/index?letter={}'.format(letter)).text
        soup = bs(r, "html.parser")
        items = soup.find("div", id="index").find("ol").find_all("li")
        for item in items:
            name = re.sub(u"\u2018|\u2019", "'", item.text).replace(u"\u2014", "-")
            name = name.strip()
            # remove '('
            if '(' in name:
                name = name[:name.find('(')].rstrip()
            link = "https://www.mayoclinic.org" + item.a['href']
            body += name + '#' + link + "\n"
    return body


def handler(event, context):
    body = process()

    client = boto3.client('s3',
             region_name="us-east-1"
            )
    client.put_object(Bucket=BUCKET_NAME, Key=FILE_NAME, Body=body)
    return 'Hello from Lambda'

def main():
    handler("", "")

if __name__ == "__main__":
    main()
    