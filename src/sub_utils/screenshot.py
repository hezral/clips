def do_webview_screenshot(uri, out_file_path):
    """
    function to load html/url and save snapshot of the full page in png using WeasyPrint and PyMuPDF
    uri: can be local uri like a html file, or internet url
    out_file_path: full path to the png file export
    """
    import os
    import logging
    import weasyprint
    from weasyprint import HTML
    import fitz # PyMuPDF
    from ..constants import APP_ID

    logger = logging.getLogger(APP_ID)
    logger.debug(f"Generating screenshot v2 for {uri} -> {out_file_path}")

    try:
        # 1. Generate PDF in memory using WeasyPrint
        # logger.debug("Rendering HTML to PDF...")
        if os.path.exists(uri):
            html = HTML(filename=uri)
        else:
            html = HTML(url=uri)
            
        pdf_bytes = html.write_pdf()
        # logger.debug(f"PDF generated ({len(pdf_bytes)} bytes).")

        # 2. Convert PDF to PNG using PyMuPDF
        # logger.debug("Converting PDF to PNG...")
        doc = fitz.open("pdf", pdf_bytes)
        if doc.page_count < 1:
            logger.error("Error: Empty PDF document")
            return

        page = doc.load_page(0)  # Get first page
        pix = page.get_pixmap()
        pix.save(out_file_path)
        # logger.debug("Screenshot saved successfully.")
        
    except Exception as e:
        logger.error(f"Screenshot generation failed: {e}")
        import traceback
        traceback.print_exc()

# def do_webview_screenshot_webkit(uri, out_file_path):
#     """
#     function to load html/url in webview and save snapshot of the full page in png
#     uri: can be local uri like a html file, or internet url
#     out_file_path: full path to the png file export
#     """
#     import os
#     import chardet
#     import logging
#     import gi
#     gi.require_version('Gtk', '3.0')
#     from ..constants import APP_ID
# 
#     logger = logging.getLogger(APP_ID)
# 
#     try:
#         # Try different WebKit2 versions in order of preference
#         webkit_loaded = False
#         for version in ['4.1', '4.0']:
#             try:
#                 gi.require_version('WebKit2', version)
#                 from gi.repository import WebKit2, GLib
#                 webkit_loaded = True
#                 break
#             except (ValueError, ImportError):
#                 continue
# 
#         if not webkit_loaded:
#             logger.warning("WebKit2 not available, skipping URL screenshot")
#             return
# 
#         from gi.repository import Gtk, GLib
# 
#         def get_snapshot(webview, result, callback, *args):
#             snapshot = webview.get_snapshot_finish(result)
#             snapshot.write_to_png(out_file_path)
#             GLib.idle_add(self_destroy, (webview, offscreen_window))
# 
#         def loaded_handler(webview, event, offscreen_window):
#             if event.value_name == "WEBKIT_LOAD_FINISHED":
#                 try:
#                     webview.get_snapshot(WebKit2.SnapshotRegion.FULL_DOCUMENT, WebKit2.SnapshotOptions.TRANSPARENT_BACKGROUND, None, get_snapshot, None)
#                 except:
#                     import traceback
#                     traceback.print_exc()
#                     pass
# 
#         def self_destroy(data):
#             webview = data[0]
#             offscreen_window = data[1]
#             webview.try_close()
#             webview.destroy()
#             webview = None
#             # del webview
#             # print(webview)
#             offscreen_window.destroy()
#             offscreen_window = None
#             # del offscreen_window
#             # print(offscreen_window)
#             # file.close()
# 
#         webview = WebKit2.WebView()
#         webview.props.zoom_level = 1
#         webview.props.expand = True
# 
#         file = open(uri, "rb")
#         encoding_name = chardet.detect(file.read())["encoding"]
#         file.close()
# 
#         with open(uri, encoding=encoding_name) as file:
#             content  = file.read()
# 
#         # file = open(uri, "r", encoding=encoding_name)
#         # content = file.read()
#         webview.load_html(content)
# 
#         alt_file_uri = uri.replace("html", "txt")
#         if os.path.exists(alt_file_uri):
# 
#             alt_file = open(alt_file_uri, "rb")
#             encoding_name = chardet.detect(alt_file.read())["encoding"]
#             alt_file.close()
# 
#             with open(alt_file_uri, encoding=encoding_name) as alt_file:
#                 lines  = alt_file.readlines()
# 
#             # alt_file = open(uri.replace("html", "txt"), "r", encoding=encoding_name)
#             # lines = alt_file.readlines()
# 
#             line_char_counts = []
#             for line in lines:
#                 line_chars = line.split(' ')
#                 line_char_counts.append(len(' '.join(line_chars)))
# 
#             if max(line_char_counts) < 50:
#                 snapshot_width = 256
#             elif max(line_char_counts) < 100:
#                 snapshot_width = 512
#             else:
#                 snapshot_width = 1024
#         else:
#             snapshot_width = 256
# 
#         offscreen_window = Gtk.OffscreenWindow()
#         offscreen_window.set_size_request(snapshot_width, 160)
#         offscreen_window.add(webview)
#         offscreen_window.show_all()
# 
#         # Ensure the window is realized before WebKit tries to use it
#         offscreen_window.realize()
# 
#         webview.connect("load-changed", loaded_handler, offscreen_window)
# 
#     except Exception as e:
#         logger.error(f"Screenshot generation failed: {e}")
#         import traceback
#         traceback.print_exc()
