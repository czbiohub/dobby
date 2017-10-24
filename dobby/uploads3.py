import boto3

s3 = boto3.resource('s3')

# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)

data = open('dobby/util.py', 'rb')
s3.Bucket('paola-dobbytest').put_object(Key='util.py', Body=data)
