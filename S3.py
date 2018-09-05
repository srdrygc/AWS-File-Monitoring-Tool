import boto3

class S3:

    def __init__(self):
        self.AccessKey = ""
        self.SecretAccessKey = ""
        self.BucketName = ""

    def getAccessKey(self):
        return self.AccessKey

    def getSecretAccessKey(self):
        return self.SecretAccessKey

    def retrieveBuckets(self):
        s3 = boto3.resource('s3')
        buckets = s3.buckets.all()
        return buckets

    def getBucketName(self):
        return self.BucketName

    def uploadFileToBucket(self, _fileName, _localFilePath):
        boto3.resource('s3').Object(self.BucketName, _fileName).put(Body=open(_localFilePath, 'rb'), ACL='public-read')
        print("Finished uploading '{}' to bucket '{}'".format(_fileName, self.BucketName))
