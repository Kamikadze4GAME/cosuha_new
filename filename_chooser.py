
from PyQt4.QtGui import QFileDialog

keepalive_list = list()

class update_filename:
    def __init__(self, edit, caption=None):
        self.edit = edit
        self.caption = caption
    def do(self, button):
        fname = QFileDialog.getOpenFileName(
            caption = self.caption,
            filter = 'JSON (*.json)'
        )
        if fname != '':
            self.edit.setText(fname)

def init_fchooser(button, edit, caption=None):
    
    updater = update_filename(edit, caption)
    button.clicked.connect(updater.do)
    
    keepalive_list.append(updater)
