# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

import os

from .sub_utils.session import is_wayland_session
from .sub_utils.logging_utils import init_logger, log_function_calls
from .sub_utils.decorators import metrics, run_async
from .sub_utils.time_utils import get_fuzzy_timestamp
from .sub_utils.validators import validate_string_with_regex, is_valid_url, is_valid_unix_uri, is_valid_email, is_image_url

from .sub_utils.icons import get_mimetype_icon
from .sub_utils.ui import get_widget_by_name
from .sub_utils.colors import (
    is_valid_color_code,
    hsl_to_rgb,
    hex_to_rgb,
    is_light_color,
    get_css_background_color,
    get_css_text_color,
    to_rgb
)
from .sub_utils.app_data import get_all_apps, get_appinfo
from .sub_utils.active_app import get_active_appinfo
from .sub_utils.window import get_active_window, set_active_window
from .sub_utils.clipboard import copy_to_clipboard, copy_files_to_clipboard, paste_from_clipboard
from .sub_utils.crypto import do_encryption
from .sub_utils.auth import do_authentication
from .sub_utils.screenshot import do_webview_screenshot
from .sub_utils.web_utils import (
    get_domain,
    get_web_contents,
    get_web_title,
    get_web_favicon,
    get_web_data,
    get_web_data_threaded,
    open_url_gtk,
    open_file_gio,
    download_image
)
