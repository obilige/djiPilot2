from minio import Minio
import urllib3


class OSS:
    def __init__(self):
        # config
        self.server = "minio"
        self.port = "9000"
        self.access_key = ""
        self.secret_key = ""
        self.region = ""
        self.bucket = ""

    def oss(self):
        try:
            oss = Minio(
                f"{self.server}/{self.port}",
                access_key = self.access_key,
                secret_key = self.secret_key,
                secure = True,
                # http_client=urllib3.ProxyManager(
                #     "https://PROXYSERVER:PROXYPORT/",
                #     timeout=urllib3.Timeout.DEFAULT_TIMEOUT,
                #     cert_reqs="CERT_REQUIRED",
                #     retries=urllib3.Retry(
                #         total=5,
                #         backoff_factor=0.2,
                #         status_forcelist=[500, 502, 503, 504],
                # ),
            )
            return oss
        except:
            return {"message": "fail to connect oss. check oss config."}

    def first_connect(self):
        try:
            # 버킷 만들기
            if self.oss.bucket_exists(self.bucket):
                print("my-bucket exists")
                pass
            else:
                self.oss.make_bucket(self.bucket, self.region, object_lock=True)
                print("my-bucket does not exist. Now Make it")
        except:
            result = {"message": "fail first connect to oss"}
        
        return result


    def list_bucket(self):
        try:
            # 체크해보기
            buckets = self.oss.list_buckets()
            result = [bucket for bucket in buckets]
        except:
            result = {"message": "fail to get list of bucket"}
        return result


    def list_object(self):
        try:
            objects = self.oss.list_object(self.bucket, recrusive=True)
            result = [object for object in objects]
        except:
            result = {"message": "fail to get list of bucket"}
        return result


    def upload_file(self, object_name, data):
        try:
            result = self.oss.put_object(self.bucket, object_name, data, -1, progress=Progress())
            result = {"message": result}
        except:
            result = {"message": "fail to upload file"}
        return result


    def delete_file(self, object_name):
        try:
            result = self.oss.remove_object(self.bucket, object_name)
            result = {"message": result}
            return result
        except:
            result = {"message": "fail to delete files"}
        return result

    def download_file(self, object_name):
        try:
            url = self.oss.presigned_get_object(self.bucket, object_name)
            return url
        except:
            pass