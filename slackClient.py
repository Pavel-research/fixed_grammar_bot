import os
import time
import sys
import slackclient
# starterbot's ID as an environment variable
BOT_ID = "git"

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
import formatter
import queryEngine as qe;
engine=qe.QueryEngine();
#x=engine.query("repositories with more then 100 users").execute()
# instantiate Slack & Twilio clients
tk=os.environ['token'];
slack_client = slackclient.SlackClient(tk)

def handle_command(command, channel):
    try:
        q=engine.query(command);

        d=q.execute();
        try:
            header=str(q.executionRules)
        except Exception as q:
            header="can not build header"
        result=formatter.format(d)
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=result, header=str(q),as_user=True)
    except Exception as e:
        result="Exception Happened ";
        header="Error"


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    users=slack_client.server.users;
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if ("user" in output and output["user"]==u'U6EV0TZ9A'):
                return None,None

            if output and 'text' in output:
                # return text after the @ mention, whitespace removed
                return output['text'],output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")