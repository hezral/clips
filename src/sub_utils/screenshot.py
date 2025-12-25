from .logging_utils import log_function_calls

@log_function_calls
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
        
        # Use a max-width of 1024px but allow content to be narrower
        default_css = weasyprint.CSS(string="""
            @page { 
                size: 1024px 5000px; 
                margin: 0; 
            }
            html, body {
                margin: 0 !important;
                padding: 0 !important;
                min-width: 0 !important;
                max-width: 1024px !important;
                display: inline-block !important;
            }
            body { 
                -webkit-print-color-adjust: exact; 
                print-color-adjust: exact; 
                word-wrap: break-word;
            }
        """)

        if os.path.exists(uri):
            html = HTML(filename=uri)
        else:
            html = HTML(url=uri)
            
        pdf_bytes = html.write_pdf(stylesheets=[default_css])
        # logger.debug(f"PDF generated ({len(pdf_bytes)} bytes).")

        # 2. Convert PDF to PNG using PyMuPDF
        # logger.debug("Converting PDF to PNG...")
        doc = fitz.open("pdf", pdf_bytes)
        if doc.page_count < 1:
            logger.error("Error: Empty PDF document")
            return

        page = doc.load_page(0)  # Get first page
        page_area = page.rect.get_area()

        # 2.1 Detect dominant background color
        # This fixes cases where individual elements have backgrounds but body is white
        paths = page.get_drawings()
        color_stats = {}
        for path in paths:
            fill = path.get("fill")
            if not fill: continue
            color_stats[fill] = color_stats.get(fill, 0) + path["rect"].get_area()
        
        if color_stats:
            dominant_color = max(color_stats, key=color_stats.get)
            # Inject a background rectangle behind everything
            # This fills transparent gaps between elements
            page.draw_rect(page.rect, color=None, fill=dominant_color, overlay=False)

        # 3. Calculate content bounding box for cropping
        content_rect = fitz.Rect(0, 0, 0, 0)
        
        # 3.1 Text blocks
        text_page = page.get_textpage()
        for block in text_page.extractBLOCKS():
            # Block format: (x0, y0, x1, y1, text, block_no, block_type)
            bbox = fitz.Rect(block[:4])
            if content_rect.is_empty:
                content_rect = bbox
            else:
                content_rect |= bbox

        # 3.2 Drawings (vector graphics)
        for path in paths:
            rect = path["rect"]
            rect_area = rect.get_area()

            # Ignore background drawings (> 60% of page)
            if rect_area > 0.60 * page_area:
                continue

            if content_rect.is_empty:
                content_rect = rect
            else:
                content_rect |= rect
        
        if content_rect.is_empty:
            # logger.debug("No content found to crop. Using full page.")
            content_rect = page.rect
        else:
            # DYNAMIC WIDTH: Use content coordinates with padding
            padding = 10
            content_rect.x0 -= padding
            content_rect.x1 += padding
            content_rect.y0 -= padding
            content_rect.y1 += padding
            
            # Clamp to page bounds
            content_rect &= page.rect
            
        # Use 96 DPI to match 1024px width (since WeasyPrint's 1024px is 768pt)
        # 768pt / 72 * 96 = 1024px
        pix = page.get_pixmap(clip=content_rect, dpi=96)
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
