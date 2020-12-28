import json,sys,csv,requests,os

def gen_markdown(filePath):
  table=''
  with open(filePath, 'r') as fp:
    reader = csv.reader(fp)
    cnt=1
    for row in reader:
      if cnt==1:
        table += '|' + '|'.join(row) + '|\n'
        heads = []
        for i in range(1,len(row)):
          heads.append('-----')
        table += '|' + '|'.join(heads) + '|\n'
      else:
        table += '|' + '|'.join(row) + '|\n'
      cnt=2
  return table

message={'blocks':[{'type':'section','text':{'type':'mrkdwn','text': gen_markdown('/report_stats.csv')}}]}
print('Sending report ...')
print(json.dumps(message))
response = requests.post(os.getenv('SLACK_HOOK'),data=json.dumps(message),headers={'Content-Type':'application/json'})
print('Got response body')
print(response.text)