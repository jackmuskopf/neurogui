import os
import boto3
import uuid
import tempfile
import logging
from boto3.dynamodb.conditions import Key, Attr
from neurogui.settings import settings


logger = logging.getLogger(__name__)

s3 = boto3.client('s3')
meta_table = boto3.resource('dynamodb').Table(settings['ImageTableName'])

logger = logging.getLogger(__name__)

def get_session():
    return boto3.session.Session(**settings['AwsCredentials'])

def new_id():
    while True:
        new_id = uuid.uuid4()
        response = meta_table.get_item(Key=dict(id=str(new_id)))
        if response.get('Item') is None:
            return str(new_id)

def file_size(file):

    file.seek(0)
    temp = tempfile.NamedTemporaryFile()
    for line in file:
        temp.write(line)
    size = os.stat(temp.name).st_size
    temp.close()

    file.seek(0)
    return size

def file_too_big(file):

    size = file_size(file)

    logger.info("File size {}".format(size))

    return size > settings['MaxFileSize']

def upload_file_to_s3(file, bucket, key):

    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """

    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)

    s3_uri = "s3://{}/{}".format(bucket, key)

    logger.info("Uploading to {}".format(s3_uri))

    try:

        res = obj.put(Body=file)

    except Exception as e:
        logger.error("Error uploading to S3: ", e)
        raise

    return s3_uri

def stream_keys(bucket, prefix=None, client=None):

    client = client or s3

    more_objects = True
    next_token = None

    args = dict(Bucket=bucket)

    if prefix:
        args['Prefix'] = prefix

    while more_objects:

        if next_token is not None:
            args['ContinuationToken'] = next_token

        # list the objects
        response = client.list_objects_v2(**args)
        object_list = response.get('Contents', list())
        for obj in object_list:
            yield obj['Key']

        # check if there are more objects
        if response.get('IsTruncated'):
            next_token = response['NextContinuationToken']
        else:
            more_objects = False
            next_token = None



class dynamodb:
    
    logger = logger
    
    def __init__(self, **kwargs):
        
        if 'TableName' not in kwargs:
            raise ValueError("Missing keyword argument: {}".format('TableName'))

        self.session = kwargs.get('Session', boto3.session.Session())
        
        self.resource = self.session.resource('dynamodb')
        
        self.table = self.resource.Table(kwargs['TableName'])
        
        self.logger = kwargs.get('Logger') or self.logger

        self.key_fields = kwargs.get('KeyField', ['id',])
        
    
    def scan(self, **scan_args):
        
        capacity_consumed = 0
        is_more = True
        last_key = None

        while is_more:
            self.logger.debug('new scan request')

            # start where left off in scan
            if last_key is not None:
                scan_args.update(dict(ExclusiveStartKey=last_key))

            # get next batch
            scan_args['ReturnConsumedCapacity'] = 'TOTAL'
            response = self.table.scan(**scan_args)
            
            # debug the response
            # self.logger.debug(json.dumps(response, indent=2, default=str))
            
            capacity_consumed += response['ConsumedCapacity']['CapacityUnits']
            self.logger.info("scan total consumed capacity: {}".format(capacity_consumed))

            # yield them
            for i in response['Items']:
                yield i
            
            # there are more to yield if this key is present
            is_more = 'LastEvaluatedKey' in response
            last_key = response.get('LastEvaluatedKey')
            
    def query(self, **query_args):
        
        capacity_consumed = 0
        is_more = True
        last_key = None

        while is_more:
            self.logger.debug('new query request')

            # start where left off in scan
            if last_key is not None:
                query_args.update(dict(ExclusiveStartKey=last_key))

            # get next batch
            query_args['ReturnConsumedCapacity'] = 'TOTAL'
            response = self.table.query(**query_args)
            
            capacity_consumed += response['ConsumedCapacity']['CapacityUnits']
            self.logger.debug("query total consumed capacity: {}".format(capacity_consumed))

            # yield them
            for i in response['Items']:
                yield i
            
            # there are more to yield if this key is present
            is_more = 'LastEvaluatedKey' in response
            last_key = response.get('LastEvaluatedKey')
    

    def get(self, _id):

        matches = list(self.query(KeyConditionExpression=Key('id').eq(_id)))

        if len(matches) == 0:
            return None

        elif len(matches) == 1:
            return matches[0]

        else:
            raise ValueError("Multiple matches for id {}".format(_id))


        
        
