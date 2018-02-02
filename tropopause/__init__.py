__version__ = "1.1.1"
from troposphere import Tags as upstreamTags


class Tags(upstreamTags):
    """ extended upstream to prevent tag duplication """
    def __init__(self, *args, **kwargs):
        super(Tags, self).__init__(*args, **kwargs)
        self.tags = self._dedupe(self.tags)

    def __add__(self, newtags):
        newtags.tags = self._dedupe(self.tags + newtags.tags)
        return newtags

    def _dedupe(self, tags):
        interim = {}
        result = []
        for tag in self.tags + tags:
            interim[tag['Key']] = tag['Value']
        for key, val in interim.items():
            result.append({
                'Key': key,
                'Value': val
            })
        return result
