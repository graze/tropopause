import re


def valid_url(url):
    regex = r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
    valid_url_re = re.compile(regex)
    if valid_url_re.match(url):
        return url
    else:
        raise ValueError("%s is not a valid url", url)
