from multiprocessing import Process, Queue
import sys

def start_client(gui_to_client_queue, client_to_gui_queue):
    import asyncio
    from delete_then import Client  # твой главный класс клиента

    client = Client(gui_to_client_queue, client_to_gui_queue)

    asyncio.run(client.start())

def start_gui(gui_to_client_queue, client_to_gui_queue):
    from PyQt5.QtWidgets import QApplication, QDialog
    from test import Ui_Dialog  # твой главный класс GUI

    app = QApplication(sys.argv)
    Dialog = QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog, gui_to_client_queue, client_to_gui_queue)

    Dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Инициализируем очереди для общения
    gui_to_client_queue = Queue()
    client_to_gui_queue = Queue()

    # Создаём процессы
    client_process = Process(target=start_client, args=(gui_to_client_queue, client_to_gui_queue))
    gui_process = Process(target=start_gui, args=(gui_to_client_queue, client_to_gui_queue))

    # Запускаем процессы
    client_process.start()
    gui_process.start()

    # Ждём завершения
    client_process.join()
    gui_process.join()
