import logging
from datetime import datetime
from .time_utils import get_fuzzy_timestamp
from ..constants import APP_ID

logger = logging.getLogger(APP_ID)
from .logging_utils import log_function_calls


@log_function_calls
def get_domain(url):

    ''' Function to get domain from url '''
    from urllib.parse import urlparse
    result = urlparse(url).netloc
    if len(result.split('.')) == 3:
        domain = '.'.join(result.split('.')[1:])
    else:
        domain = '.'.join(result.split('.'))
    return domain

@log_function_calls
def get_web_contents(url):

    ''' Function to get web contents '''
    import requests
    try:
        response = requests.get(url)
        # Ensure proper UTF-8 encoding
        response.encoding = response.apparent_encoding or 'utf-8'
        contents = response.text
        return contents
    except:
        return None

@log_function_calls
def get_web_title(contents, url):

    ''' Function to get web page title from url'''
    from urllib.parse import urlparse
    import html
    if contents is not None:
        title_tag_open = "<title>"
        title_tag_close = "</title>"
        title = str(contents[contents.find(title_tag_open) + len(title_tag_open) : contents.find(title_tag_close)])
        title = html.unescape(title)
    else:
        title = urlparse(url).netloc
    return title

@log_function_calls
def get_web_favicon(contents, url, download_path='./', checksum='na'):

    ''' Function to get web page favicon from a url '''
    LARGE_FAVICON = r"<link\srel\=\"(apple-touch-icon-precomposed|apple-touch-icon)\"\s(.*(\/.*)+?|href)\=\".*(\/.*)+?\""
    SMALL_FAVICON = r"<link\srel\=\"(icon|shortcut icon)\"\s(.*(\/.*)+?|href)\=\".*(\/.*)+?\""
    
    import re
    import requests
    from urllib.parse import urlparse

    domain = get_domain(url)
    icon_name = download_path + '/' + domain + '-' + checksum + '.ico'

    regex_result1 = re.search(LARGE_FAVICON, contents)
    regex_result2 = re.search(SMALL_FAVICON, contents)

    if regex_result1 is not None:
        regex_result = regex_result1
    else:
        regex_result = regex_result2

    if regex_result is not None:
        favicon_url = regex_result.group(0).split('href="')[1].split('"')[0].strip(">").strip("/")
        if "http" not in favicon_url:
            favicon_url = urlparse(url).scheme + '://' + domain + '/' + favicon_url
    else:
        favicon_url = urlparse(url).scheme + '://' + domain + '/' + 'favicon.ico'
    
    r = None
    try:
        r = requests.get(favicon_url, allow_redirects=True)
    except:
        pass

    if r is not None:
        open(icon_name, 'wb').write(r.content)
        return icon_name

@log_function_calls
def get_web_data(url, file_path=None, download_path='./', checksum='na'):

    ''' Function to get web data '''
    contents = get_web_contents(url)
    title = get_web_title(contents, url)
    icon_name = get_web_favicon(contents, url, download_path, checksum)

    if file_path is not None:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write("\n"+title)
            file.close
    return title, icon_name

@log_function_calls
def get_web_data_threaded(url, file_path, download_path='./'):

    ''' Function to get web data threaded '''
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_web_data, url, file_path, download_path)
        return_value = future.result()
        # print(return_value)
        logger.debug(get_fuzzy_timestamp(datetime.now()))

@log_function_calls
def open_url_gtk(url):

    ''' Function to view file using default application via Gtk'''
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk
    try:
        Gtk.show_uri_on_window(None, url, Gdk.CURRENT_TIME)
    except:
        logger.error("Unable to launch {url}".format(url=url))
        pass

@log_function_calls
def open_file_gio(filepath):

    ''' Function to view file using default application via Gio'''
    import gi
    from gi.repository import Gio
    view_file = Gio.File.new_for_path(filepath)
    if view_file.query_exists():
        try:
            Gio.AppInfo.launch_default_for_uri(uri=view_file.get_uri(), context=None)
        except:
            logger.error("Unable to launch {file}".format(file=view_file))
            pass
@log_function_calls
def download_image(url, out_file_path):

    ''' Function to download an image from a URL '''
    import requests
    try:
        response = requests.get(url, allow_redirects=True)
        if response.status_code == 200:
            with open(out_file_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            logger.error(f"Failed to download image from {url}: Status code {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error downloading image from {url}: {e}")
        return False
