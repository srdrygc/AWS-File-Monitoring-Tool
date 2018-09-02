import hashlib

class ETag:
    def __init__(self):
        self.LocalFilePath = ""
        self.Etag = ""

    def getLocalFileEtag(self, localFilePath):

        self.LocalFilePath = localFilePath
        md5s = []
        etag = ""

        with open(localFilePath, 'rb') as fp:
            while True:
                data = fp.read(8 * 1024 * 1024)
                if not data:
                    break
                md5s.append(hashlib.md5(data))

        if len(md5s) == 1:
            localFileEtag = '"{}"'.format(md5s[0].hexdigest())
        else:
            digests = b''.join(m.digest() for m in md5s)
            digests_md5 = hashlib.md5(digests)
            localFileEtag = '"{}-{}"'.format(digests_md5.hexdigest(), len(md5s))

        self.Etag = localFileEtag

        return localFileEtag