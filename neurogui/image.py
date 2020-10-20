import os
import logging
import json
import base64
import boto3
from flask import Blueprint, render_template, request, redirect, url_for
from neurogui.settings import settings
from neurogui.utils import stream_keys, dynamodb, get_session

logger = logging.getLogger(__name__)

api = Blueprint('image-api', __name__)

session = get_session()

s3 = session.client('s3', config=boto3.session.Config(signature_version='s3v4'))

meta_table = session.resource('dynamodb').Table(settings['ImageTableName'])
dynamo_tool = dynamodb(TableName=settings['ImageTableName'], Session=session)

this_dir = os.path.realpath(os.path.dirname(__file__))

@api.route('/images')
def list_images():
	images = list(dynamo_tool.scan())
	return render_template('images.html', images=images)

@api.route('/images/<image_id>')
def image(image_id):
	
	logger.info("Loading page for image {}".format(image_id))
	image_url = s3.generate_presigned_url(
		'get_object',
		Params={
			'Bucket': settings['ImageBucketName'],
			'Key': "images/{}".format(image_id)
		},
		ExpiresIn=600
	)
	return render_template('image.html', ImageUrl=image_url, ImageId=image_id)