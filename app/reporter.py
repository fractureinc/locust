#!/usr/bin/python
import json,csv,requests,os,zipfile,time,re
import boto3

class SlackApp():

  def __init__(self):
    self.__slack_hook = os.getenv('SLACK_HOOK')

  def send_message(self,json):
    response = requests.post(self.__slack_hook,data=json,headers={'Content-Type':'application/json'})
    return response.text

class LocustReporter(SlackApp):

  def __init__(self):
    super().__init__()
    self.users = os.getenv('USERS')
    self.time  = os.getenv('TIME')
    self.spawn = os.getenv('SPAWN')
    self.workers = os.getenv('WORKERS')
    self.target_host = os.getenv('TARGET_HOST')
    self.release_name = os.getenv('RELEASE_NAME')
    self.s3_bucket = os.getenv('LOCUST_REPORTS_BUCKET').strip()
    self.locust_script = '/locust-tasks/locust-tasks.py'
    self.stats_csv = '/report_stats.csv'
    self.failures_csv = '/report_failures.csv'
    self.history_csv = '/report_stats_history.csv'
    self.zip_file = '/reports.zip'
    self.s3_key = "%s/%s.zip" % (re.sub('^http(s)?:\/\/','',self.target_host).replace('/','-'), int(time.time()))
    self.slack_files = []

  def csv_cnt(self,filePath):
    with open(filePath, 'r') as fp:
      reader = csv.reader(fp)
      cnt = sum(1 for row in reader) - 1
    return cnt

  def last_history(self):
    rows=[]
    with open(self.history_csv, 'r') as fp:
      reader = csv.DictReader(fp)
      for row in reader:
        rows.append(row)
    return rows[-1]

  def req_totals(self):
    last = self.last_history()
    return last['Total Request Count'], last['Total Failure Count']

  def task_count(self):
    sc = open(self.locust_script,'r').read()
    return sc.count('@task')

  def results_mrkdwn(self):
    totalr, totalf = self.req_totals()
    out = "*Test results for:* %s" % self.target_host
    out += "\n\n*Total Tasks:* %s" % self.task_count()
    out += "\n*URLs Tested:* %s" % self.csv_cnt(self.stats_csv)
    out += "\n*Total Requests:* %s" % totalr
    out += "\n*Total Failures:* %s" % totalf 
    icon = ':x:' if int(totalf) > 0 else ':white_check_mark:'
    return out, icon

  def specs_mrkdwn(self):
    out = "" 
    out += "\n*Users:* %s" % self.users
    out += "\n*Test Length:* %s" % self.time
    out += "\n*User Spawn Rate:* %s" % self.spawn
    out += "\n*Worker Nodes:* %s" % self.workers
    return out

  def csv_text(self):
    mrkdwn=''
    last = self.last_history()
    for key in last:
      mrkdwn += '\n*%s*: %s' % (key, last[key])
    mrkdwn+="\n\n The complete CSV data was uploaded to the S3 path\n`s3://%s/%s`\n\n" % (self.s3_bucket, self.s3_key)
    mrkdwn+="\n\n Check out the Locust docs for more info about testing and results. https://docs.locust.io/en/stable/what-is-locust.html"
    return mrkdwn 

  def upload_to_s3(self):
    zipf = zipfile.ZipFile(self.zip_file, 'w', zipfile.ZIP_DEFLATED)
    zipf.write(self.stats_csv)  
    zipf.write(self.failures_csv)  
    zipf.write(self.history_csv) 
    zipf.close()
    s3 = boto3.resource('s3')
    data = open(self.zip_file, 'rb')
    s3.Bucket(self.s3_bucket).put_object(Key=self.s3_key, Body=data)

  def summary_message(self): 
    results,results_icon = self.results_mrkdwn()
    message={
      'text': '%s New Load test results available for (%s)' % (results_icon, self.target_host),
      'blocks':[
        {
          "type": "header",
          "text": {
            "type": "plain_text",
            "text": "%s Test Summary" % results_icon
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
            "text": "Test Config"
          }
        },{
          'type':'section',
          'text':{
            'type':'mrkdwn',
            'text': self.specs_mrkdwn()
          }
        },
        {
          'type':'header',
          'text': {
            'type': 'plain_text',
            'text': 'Request History Totals'
          }
        },
        {
          'type':'section',
          'text':{
            'type': 'mrkdwn',
            'text': self.csv_text()
          }
        },
        {
          "type": "divider"
        }
      ]
    }
    return json.dumps(message)
  
  def send_report(self):
    print('Uploading files ...')
    self.upload_to_s3()
    print('Sending report ...')
    response = self.send_message(self.summary_message())
    print('Got response:')
    print(response)


if __name__ == "__main__":
  reporter = LocustReporter()
  reporter.send_report()