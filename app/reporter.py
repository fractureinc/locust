#!/usr/bin/python
import json,csv,requests,os
#curl -F file=@cycling.jpeg -F "initial_comment=Hello, Leadville" -F channels=C0R7MFNJD -H "Authorization: Bearer xoxp-123456789" 

class SlackApp():

  def __init__(self):
    self.slack_upload_url = 'https://slack.com/api/files.upload'
    self.slack_hook = os.getenv('SLACK_HOOK')
    self.slack_token = os.getenv('SLACK_TOKEN')

  def send_message(self,json):
    response = requests.post(self.slack_hook,data=json,headers={'Content-Type':'application/json'})
    return response.text

  def upload_file(self,path):
    auth = 'Bearer %s' % self.slack_token
    response = requests.post(self.slack_upload_url,headers={'Authorization': auth})
    return repsonse.text

class LocustReporter(SlackApp):

  def __init__(self):
    super().__init__()
    self.users = os.getenv('USERS')
    self.time  = os.getenv('TIME')
    self.spawn = os.getenv('SPAWN')
    self.workers = os.getenv('WORKERS')
    self.target_host = os.getenv('TARGET_HOST')
    self.stats_csv = '/report_stats.csv'
    self.failures_csv = '/report_failures.csv'
    self.history_csv = '/report_stats_history.csv'

  def csv_cnt(self,filePath):
    with open(filePath, 'r') as fp:
      reader = csv.reader(fp)
      cnt = sum(1 for row in reader) - 1
    return cnt

  def reqs_totals(self):
    total=0.0
    with open(self.stats_csv, 'r') as fp:
      reader = csv.DictReader(fp)
      start = True
      for row in reader:
        if start == False:
          total += float(row["Requests/s"])
        else:
          start = False 
    return int(round(total))

  def results_mrkdwn(self):
    out = "*Test results for:* %s" % self.target_host
    out += "\n\n*Total Tests:* %s" % self.csv_cnt(self.stats_csv)
    out += "\n*Total Requests:* %s" % self.reqs_totals()
    fails = self.csv_cnt(self.failures_csv)
    out += "\n*Total Failures:* %s" % fails
    #out += "\n*Total Test Executions:* %s" % csv_cnt('/report_stats_history.csv')
    icon = ':x:' if fails > 0 else ':white_check_mark:'
    return out, icon

  def specs_mrkdwn(self):
    out = "" 
    out += "\n*Users:* %s" % self.users
    out += "\n*Test Length:* %s" % self.time
    out += "\n*User Spawn Rate:* %s" % self.spawn
    out += "\n*Worker Nodes:* %s" % self.workers
    return out

  def csv_text(self,path):
    with open(path, 'r') as fp:
      reader = csv.reader(fp)
      out=''
      head=True
      for row in reader:
        if head == True:
          out += ' | '.join(row)
          head = False
        else:
          out += ' | '.join(row)
    print(out)
    return 'test'  

  def message_json(self):
    results,results_icon = self.results_mrkdwn()
    message={
      'text': '%s New Load test results available for (%s)' % (results_icon, self.target_host),
      'blocks':[
        {
          "type": "header",
          "text": {
            "type": "plain_text",
            "text": "%s Test Results" % results_icon
          }
        },{
          'type':'section',
          'text':{
            'type':'mrkdwn',
            'text': results
          }
        },{
          "type": "header",
          "text": {
            "type": "plain_text",
            "text": ":gear: Test Specs"
          }
        },{
          'type':'section',
          'text':{
            'type':'mrkdwn',
            'text': self.specs_mrkdwn()
          }
        },
        {
          "type": "divider"
        },
        {
          'type':'header',
          'text': {
            'type': 'plain_text',
            'text': ':page_with_curl: Raw CSV Results'
          }
        },
        {
          'type':'section',
          'text':{
            'type': 'mrkdwn',
            'text': self.csv_text(self.stats_csv)
          }
        }
      ]
    }
    return json.dumps(message)

  def build_send_message(self):
    print('Sending report ...')
    message = self.message_json()
    response = self.send_message(message)
    print('Got response:')
    print(response)


if __name__ == "__main__":
  reporter = LocustReporter()
  reporter.build_send_message()