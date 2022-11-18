# import json
# import boto3
# from botocore.vendored import requests
# import datetime


# def lambda_handler(event, context):
    
#     s3client = boto3.client('s3')
#     s3_info = event['Records'][0]['s3']

#     bucket_name = s3_info['bucket']['name']
#     key_name = s3_info['object']['key']
#     print("bucket", bucket_name, "key", key_name)
#     metadata = s3client.head_object(Bucket=bucket_name, Key=key_name)
#     print("metdata", metadata)
#     given_labels = metadata.get('Metadata').get("customlabel")
#     if given_labels:
#         given_labels = given_labels.split(",")
#     # given_labels = metadata['Metadata']["customlabel"].split(",")
#         given_labels = [x.strip() for x in given_labels]
#     else:
#         given_labels = []
#     print("given_labels", given_labels)
#     #print(bucket_name)
#     client = boto3.client('rekognition')
#     pass_object = {'S3Object':{'Bucket':bucket_name,'Name':key_name}}
    
#     resp = client.detect_labels(Image=pass_object)
#     #print('<---------Now response object---------->')
#     #print(json.dumps(resp, indent=4, sort_keys=True))
#     timestamp =str(datetime.datetime.now())
#     labels = []
#     labels += given_labels
#     #temp = resp['Labels'][0]['Name']
#     for i in range(len(resp['Labels'])):
#         labels.append(resp['Labels'][i]['Name'])
#     print('<------------Now label list----------------->')
#     print(labels)
#     format = {'objectKey':key_name,'bucket':bucket_name,'createdTimestamp':timestamp,'labels':labels}
#     required_json = json.dumps(format)
#     print(required_json)
#     #change url
#     url = "https://search-photos-dbypzpautg4of7jj4qwigzvqne.us-east-1.es.amazonaws.com"
#     headers = {"Content-Type": "application/json"}
#     r = requests.post(url, data=json.dumps(format).encode("utf-8"), headers=headers,auth=('sakshat', 'Skmusic234*98'))
    
#     print(r.text)
#     return {
#         'statusCode': 200,
#         'body': json.dumps('Hello from Lambda!')
#     }
import json
import boto3
import os
import requests
from datetime import *
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    print("EVENT ---- {}".format(json.dumps(event)))
    #TESTING PIPELINE
    headers = {"Content-Type": "application/json"}
    
    s3 = boto3.client('s3')
    rek = boto3.client('rekognition')
    
    #Getting Image information from S3
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(key)
        size = record['s3']['object']['size']
        metadata = s3.head_object(Bucket=bucket, Key=key)
        
        print("-----meta-----", metadata)
        
        #print("-----KEY-----", key)
        #Detecting the label of the current image
        labels = rek.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': str(key)
                }
            },
            MaxLabels=10,
            MinConfidence=50
        )
        
        print("IMAGE LABELS---- {}".format(labels['Labels']))
        print("META DATA---- {}".format(metadata))
        
        if metadata["Metadata"]:
            customlabels = (metadata["Metadata"]["customlabels"]).split(",")
        
        #Prepare JSON object
        obj = {}
        obj['objectKey'] = key
        obj['bucket'] = bucket
        obj['createdTimestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        obj['labels'] = []
        
        for label in labels['Labels']:
            obj['labels'].append(label['Name'])
            
        if metadata["Metadata"]:
            for c_labels in customlabels:
                c_labels = c_labels.strip()
                c_labels = c_labels.lower()
                if c_labels not in obj['labels']:
                    obj['labels'].append(c_labels)
                    
        print("FINAL LABELS -> ", obj['labels'])  #appends custom labels to final labels
            
        print("JSON OBJECT --- {}".format(obj))
        
        #Posting the JSON object into ElasticSearch, _id is automatically increased
        endpoint = 'https://search-photos-dbypzpautg4of7jj4qwigzvqne.us-east-1.es.amazonaws.com'
        region = 'us-east-1'
        service = 'es'
        credentials = boto3.Session(aws_access_key_id="",
                          aws_secret_access_key="", 
                          region_name="us-east-1").get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
        # awsauth = (os.environ['sakshat1'], os.environ['Skmusic234*'])
        
        #OpenSearch domain endpoint with https://
        index = 'photos'
        type = 'Photos'
        url = endpoint + '/' + index + '/' + type
        print("URL --- {}".format(url))
        
        obj = json.dumps(obj).encode("utf-8")
        req = requests.post(url, auth=awsauth, headers=headers, data=obj)
        
        print("Success Hello: ", req)
        # return {
        #     'statusCode': 200,
        #     'headers': {
        #         'Access-Control-Allow-Headers': '*',
        #         'Access-Control-Allow-Origin': '*',
        #         'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
        #     },
        #     'body': json.dumps("Image labels have been detected successfully!")
        # }
    # if response['ResponseMetadata']['HTTPStatusCode'] == 200 :
        return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
      
        }
    #Testing for pipeline
