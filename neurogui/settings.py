import math

settings = dict(
	ImageBucketName='sig-neuro-storage',
	ImageTableName='sig-neuro-meta',
	MaxFileSize=math.inf,
	AwsCredentials=dict(
		profile_name='personal'
	)
)