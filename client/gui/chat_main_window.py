from client.gui.chat_main_interface import ChatInterface
from PyQt5 import QtWidgets, QtGui


class ChatMainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = ChatInterface()
        self.ui.setupUi(self)
        self.ui.chat_display_text_edit.setReadOnly(True)
        self.ui.message_plain_text.setReadOnly(True)

    def prepare_message_enter(self):
        self.ui.message_plain_text.setPlainText("")
        self.ui.message_plain_text.setReadOnly(False)

    def get_search_line(self) -> str:
        line = self.ui.search_line.text()
        return line

    def get_message_text(self) -> str:
        line = self.ui.message_plain_text.toPlainText()
        return line

    def check_message_not_empty(self):
        line = self.get_message_text()
        return len(line) > 0

    def set_chat_simple_text(self, text: str):
        self.ui.chat_display_text_edit.setPlainText(text)

    def set_chat_html_text(self, html: str):
        self.ui.chat_display_text_edit.setHtml(html)

    def append_to_end(self, text: str):
        # Получаем курсор из QTextEdit
        cursor = self.ui.chat_display_text_edit.textCursor()

        # Перемещаем курсор в конец документа
        cursor.movePosition(QtGui.QTextCursor.End)

        # Вставляем текст в позицию курсора (конец)
        cursor.insertText(text)

        # Обновляем курсор виджета
        self.ui.chat_display_text_edit.setTextCursor(cursor)

        # Обеспечиваем прокрутку к новому тексту
        self.ui.chat_display_text_edit.ensureCursorVisible()


    def append_text_to_chat_display(self, text: str):
        self.ui.chat_display_text_edit.insertPlainText(text)
