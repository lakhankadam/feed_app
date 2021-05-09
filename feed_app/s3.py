import os
import tinys3

BASE_URL = 'http://lkadambucket.s3-ap-southeast-1.amazonaws.com'
ENDPOINT = "s3-ap-southeast-1.amazonaws.com"
SECRET_KEY = 'AKIAV3WEFJJRO752SD7X'
SECRET_ACCESS_KEY = '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'
def upload_to_s3(file_name, uuid, prefix):
    try:
        conn = tinys3.Connection(SECRET_KEY, SECRET_ACCESS_KEY, tls=True, endpoint=ENDPOINT)
        location = os.path.join(prefix,file_name)
        f = open(location,'rb')
        path = "/".join([uuid,file_name])
        conn.upload(path,f,'lkadambucket')
        return True
    except Exception as e:
        print(e)
        return False