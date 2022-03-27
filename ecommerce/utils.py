from http.cookies import SimpleCookie
import urllib
from urllib.parse import urlparse, parse_qs, urlencode,unquote
import urllib

def category(url) :
    url_parsed = urlparse(url)
    query_path = url_parsed.path
    category = query_path.replace('/categories/','')
    return category