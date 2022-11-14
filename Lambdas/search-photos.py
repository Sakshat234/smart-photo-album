import json
import boto3
import requests
import os
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    # TODO implement
    
    print("-----EVENT-----",event)
    query = event['queryStringParameters']['q']
    print(query)
    lex = boto3.client('lex-runtime')
    lex_resp = lex.post_text(
        botName = 'PhotoBotOne',
        botAlias = 'PhotoBotOne',
        userId = 'user01',
        inputText = query
        )
    
    print(lex_resp)
    slots = lex_resp['slots']
    print(slots)
    keywords = [v for _, v in slots.items() if v]
    print(keywords)
    
    #Getting the JSON object into ElasticSearch
    endpoint = 'https://search-photos-dbypzpautg4of7jj4qwigzvqne.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session(aws_access_key_id="AKIAXTM5C73AZUD7K2MP",
                          aws_secret_access_key="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", 
                          region_name="us-east-1").get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    #OpenSearch domain endpoint with https://
    index = 'photos'
    type = 'Photos'
    url = endpoint + '/' + index + '/' + type + '/_search'
    print("URL --- {}".format(url))
    
    headers = { "Content-Type": "application/json" }
    
    result = []
    for i in keywords:
        
        print("keyword --- {}".format(i))
        
        query = {
            "query": {
                "match": {
                    "labels":i
                }
            }
        }
        
        req = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
        data = json.loads(req.content)
        
        print("----DATA----", data)
        
        for idx in data['hits']['hits']:
            key = idx['_source']['objectKey']
            url_res = "https://photo-sk9428.s3.amazonaws.com/"+key
            if(url_res not in result):
                result.append(url_res)
        print("-----RESULT-----",result)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers':{
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS'
        }
    }