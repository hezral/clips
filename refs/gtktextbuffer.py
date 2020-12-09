import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GLib


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self):
        Gtk.Window.__init__(self, title = "TwoNote")
        self.grid = Gtk.Grid()
        self.toolbar = Gtk.Toolbar()
        self.grid.add(self.toolbar)

        #buttons for toolbar
        self.button_bold = Gtk.ToggleToolButton()
        self.button_italic = Gtk.ToggleToolButton()
        self.button_underline = Gtk.ToggleToolButton()
        self.button_save = Gtk.ToolButton()
        self.button_open = Gtk.ToolButton()

        self.mytext = TextSet(self.button_bold, self.button_italic, self.button_underline)

        self.button_bold.set_icon_name("format-text-bold-symbolic")
        self.toolbar.insert(self.button_bold, 0)

        self.button_italic.set_icon_name("format-text-italic-symbolic")
        self.toolbar.insert(self.button_italic, 1)

        self.button_underline.set_icon_name("format-text-underline-symbolic")
        self.toolbar.insert(self.button_underline, 2)

        self.toolbar.insert(self.button_save, 3)
        self.toolbar.insert(self.button_open, 4)

        self.button_open.set_icon_name("document-open-data")
        self.button_save.set_icon_name("document-save")

        self.button_save.connect("clicked", self.save_file)
        self.button_open.connect("clicked", self.open_file)
        self.button_bold.connect("toggled", self.mytext.on_button_clicked, "Bold", self.button_italic, self.button_underline)
        self.button_italic.connect("toggled", self.mytext.on_button_clicked, "Italic", self.button_bold, self.button_underline)
        self.button_underline.connect("toggled", self.mytext.on_button_clicked, "Underline", self.button_bold, self.button_italic)


        self.grid.attach_next_to(self.mytext, self.toolbar, Gtk.PositionType.BOTTOM, 10,30) 

        self.add(self.grid)

        filename = "Untitled"
    def open_file(self, widget):
        open_dialog = Gtk.FileChooserDialog("Open an existing file", self, Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        open_response = open_dialog.run()

        if open_response == Gtk.ResponseType.OK:
            filename = open_dialog.get_filename()
            buf = self.mytext.get_buffer()
            des_tag_format = buf.register_deserialize_tagset()
            result, des_content = GLib.file_get_contents(filename)
            text = buf.deserialize(buf, des_tag_format, buf.get_start_iter(), des_content)

            self.mytext.get_buffer().set_text(text)
            open_dialog.destroy()

        elif open_response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
            open_dialog.destroy()

    def save_file(self, widget):
        savechooser = Gtk.FileChooserDialog('Save File', self, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        allfilter = Gtk.FileFilter()
        allfilter.set_name('All files')
        allfilter.add_pattern('*')
        savechooser.add_filter(allfilter)

        txtFilter = Gtk.FileFilter()
        txtFilter.set_name('Text file')
        txtFilter.add_pattern('*.txt')
        savechooser.add_filter(txtFilter)
        response = savechooser.run()

        if response == Gtk.ResponseType.OK:
            filename = savechooser.get_filename()
            print(filename, 'selected.')
            buf = self.mytext.get_buffer()
            start, end = buf.get_bounds()
            tag_format = buf.register_serialize_tagset()
            content = buf.serialize(buf, tag_format, start, end) 



            try:
                GLib.file_set_contents(filename, content)
            except SomeError as e:
                print('Could not save %s: %s' % (filename, err))
            savechooser.destroy()

        elif response == Gtk.ResponseType.CANCEL:
            print('Closed, file not saved.')
            savechooser.destroy()



class TextSet(Gtk.TextView):
    def __init__(self, buttonBold, buttonItalic, buttonUnderline, interval = 1 ):
        # Textview Setup
        Gtk.TextView.__init__(self)
        self.set_vexpand(True)
        self.set_indent(10)
        self.set_top_margin(90)
        self.set_left_margin(20)
        self.set_right_margin(20)
        self.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.tb = TextBuffer()
        self.set_buffer(self.tb)
        # Thread setup
        self.button_bold = buttonBold
        self.button_italic = buttonItalic
        self.button_underline = buttonUnderline


    def on_button_clicked(self, widget, tagname, widget1, widget2):
        state = widget.get_active()
        name = widget.get_icon_name()
        bounds = self.tb.get_selection_bounds()
        self.tagname = tagname
        if(state):
            widget1.set_active(False)
            widget2.set_active(False)
        #highlighting
        if(len(bounds) != 0):
            start, end = bounds
            myIter = self.tb.get_iter_at_mark(self.tb.get_insert())
            myTags = myIter.get_tags()
            if(myTags == [] and state == True):
                self.tb.apply_tag_by_name(tagname, start, end)
            elif(myTags != [] and state == True):
                self.tb.remove_all_tags(start, end)
                self.tb.apply_tag_by_name(tagname, start, end)

            else: 
                for i in range(len(myTags)):
                    if(myTags[i].props.name == tagname):
                        self.tb.remove_tag_by_name(tagname,start,end)



        myTags = []
        self.tb.markup(widget, tagname)

    def mouse_clicked(self, window, event): 
        self.button_bold.set_active(False)
        self.button_italic.set_active(False)
        self.button_underline.set_active(False)



class TextBuffer(Gtk.TextBuffer):
    def __init__(self):
        Gtk.TextBuffer.__init__(self)
        self.connect_after('insert-text', self.text_inserted)
        # A list to hold our active tags
        self.taglist_on = []
        # Our Bold tag.
        self.tag_bold = self.create_tag("Bold", weight=Pango.Weight.BOLD)  
        self.tag_none = self.create_tag("None", weight=Pango.Weight.NORMAL)
        self.tag_italic = self.create_tag("Italic", style=Pango.Style.ITALIC)
        self.tag_underline = self.create_tag("Underline", underline=Pango.Underline.SINGLE)



    def get_iter_position(self):
        return self.get_iter_at_mark(self.get_insert())

    def markup(self, widget, tagname):
        self.tag_name = tagname
        self.check = True
        ''' add "bold" to our active tags list '''
        if(widget.get_active() == True):
            if(self.tag_name == 'Bold'):
                if 'Bold' in self.taglist_on:
                    del self.taglist_on[self.taglist_on.index('Bold')]
                else:
                    self.taglist_on.append('Bold')


            if(self.tag_name == 'Italic'):
                if 'Italic' in self.taglist_on:
                    del self.taglist_on[self.taglist_on.index('Italic')]
                else:   
                    self.taglist_on.append('Italic')

            if(self.tag_name == 'Underline'):
                if 'Underline' in self.taglist_on:
                    del self.taglist_on[self.taglist_on.index('Underline')]
                else:
                    self.taglist_on.append('Underline')      

        else:
            self.check = False



    def text_inserted(self, buffer, iter, text, length):
        # A text was inserted in the buffer. If there are ny tags in self.tags_on,   apply them
        #if self.taglist_None or self.taglist_Italic or self.taglist_Underline or self.taglist_Bold:
        if self.taglist_on:
            # This sets the iter back N characters
            iter.backward_chars(length)
            # And this applies tag from iter to end of buffer
            if(self.check == True):
                if(self.tag_name == 'Italic'):
                    self.apply_tag_by_name('Italic', self.get_iter_position(), iter)

                if(self.tag_name == 'Bold'):
                    self.apply_tag_by_name('Bold', self.get_iter_position(), iter)

                if(self.tag_name == 'Underline'):
                    self.apply_tag_by_name('Underline', self.get_iter_position(), iter)

            else:
                self.remove_all_tags(self.get_iter_position(), iter)


win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()