"""
Author: Jeremey Ebenezer <jeremeyebenezer@gmail.com>

This script sends a recipient a text message with any new posts to a particular subreddit.
It takes Twilio account information, recipient cell phone number, subreddit, and poll time.
It will then use Twilio to send a text message to the recipient on a specific frequency with any new
submissions within the past poll time.
"""

import argparse
import json
import time

import requests
from twilio.rest import TwilioRestClient


class TwilioObj:
    """
    Twilio Object that contains methods and members to assist in sending texts.
    """
    def __init__(self, twilio_acc_details):
        """
        Initialize object with parsed arguments.
        :param twilio_acc_details: Parsed arguments containing details for creating Twilio client.
        :type twilio_acc_details: dict[account_id, auth_token, twilio_num, cell_num]
        """
        self.account_id = twilio_acc_details.account_id
        self.auth_token = twilio_acc_details.auth_token
        self.twilio_num = twilio_acc_details.twilio_num
        self.cell_num = twilio_acc_details.cell_num
        self.twilio_cli = TwilioRestClient(twilio_acc_details.account_id, twilio_acc_details.auth_token)

    def send_text(self, msg):
        """
        Sends message to recipient.
        :param msg: Message that needs to be sent.
        :type msg: str
        :return:
        """
        self.twilio_cli.messages.create(body=msg, from_=self.twilio_num, to=self.cell_num)


def parse_args():
    """
    Parses arguments containing information about twilio account, recipient, subreddit, and poll time.
    :return: Returns the dictionary containing parsed arguments.
    :rtype: dict
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-sid', '-account_id', type=str, action='store', dest='account_id', help='Store account id', required=True)
    parser.add_argument('-at', '-auth_token', type=str, action='store', dest='auth_token', help='Store authentication token', required=True)
    parser.add_argument('-tn', '-twilio_num', type=str, action='store', dest='twilio_num', help='Store twilio number', required=True)
    parser.add_argument('-cn', '-cell_num', type=str, action='store', dest='cell_num', help='Store recipient phone number', required=True)
    parser.add_argument('-sub', '-sub_reddit', type=str, action='store', dest='sub_reddit', help='Store sub reddit name', required=True)
    parser.add_argument('-pt', '-poll_time', type=int, action='store', dest='poll_time', help='Set poll interval', required=True)

    return parser.parse_args()


def create_freebie_text(freebie_data):
    """
    Creates and returns the message that needs to be sent.
    :param freebie_data: Contains title and link to the freebie.
    :type freebie_data: dict
    :return: Returns the message containing title and link to the freebie.
    :rtype: str
    """
    return '{} - www.reddit.com{}'.format(freebie_data['title'], freebie_data['permalink'])


def main():
    """
    First we parse the arguments, create the Twilio Object, set the poll time(300 by default), and create the
    subreddit url.  We then send a request to that subreddit and send a text if a new submission was submitted within
    the last poll time.  The script will continue as long as we get a HTTP response status code of 200 from reddit.
    """
    parsed_args = parse_args()
    messenger = TwilioObj(parsed_args)
    poll_time = int(parsed_args.poll_time)
    subreddit_url = "https://www.reddit.com/r/{}/new.json".format(parsed_args.sub_reddit)

    response = requests.get(subreddit_url, headers={'User-agent': 'Chrome'})
    while response.status_code == 200:
        freebie_json = json.loads(response.text)
        for i in range(10):
            if freebie_json['data']['children'][i]['data']['created_utc'] > time.time() - poll_time:
                messenger.send_text(create_freebie_text(freebie_json['data']['children'][i]['data']))
        time.sleep(poll_time)
        response = requests.get(subreddit_url, headers={'User-agent': 'Chrome'})

    messenger.send_text('Something bad happened to your freebies.')

if __name__ == "__main__":
    main()
