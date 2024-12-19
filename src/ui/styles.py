MAIN_STYLE = """
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #1a1a2e, stop:1 #16213e);
    }
    QLabel {
        color: #00ff95;
        font-size: 24px;
        font-weight: bold;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
    }
    QTextEdit {
        background-color: rgba(26, 26, 46, 0.8);
        color: #00ff95;
        border: 2px solid #00ff95;
        border-radius: 10px;
        padding: 15px;
        font-family: 'Consolas';
        font-size: 13px;
        selection-background-color: #00ff95;
        selection-color: #1a1a2e;
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #00ff95, stop:1 #00b8ff);
        color: #1a1a2e;
        padding: 8px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        min-width: 200px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #00b8ff, stop:1 #00ff95);
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #008c67, stop:1 #0081b3);
        padding-left: 14px;
    }
    QPushButton:disabled {
        background: #2c3e50;
        color: #516170;
    }
    QLabel#copyright_label {
        color: #00ff95;
        font-size: 12px;
        font-weight: normal;
        padding: 5px;
        background: transparent;
    }
    QLabel#copyright_label:hover {
        color: #00b8ff;
        text-decoration: underline;
    }
    QPushButton#close_process_button {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ff4757, stop:1 #ff6b81);
        color: white;
    }
    QPushButton#close_process_button:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ff6b81, stop:1 #ff4757);
    }
    QPushButton#close_process_button:pressed {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ff1f30, stop:1 #ff4757);
    }
    QPushButton#reset_button {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #00ff95, stop:0.5 #00b8ff, stop:1 #7d2ae8);
        color: white;
    }
    QPushButton#reset_button:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #7d2ae8, stop:0.5 #00b8ff, stop:1 #00ff95);
    }
    QPushButton#reset_button:pressed {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #5a1ea8, stop:0.5 #0081b3, stop:1 #008c67);
    }
    QTabWidget::pane {
        border: 2px solid #00ff95;
        border-radius: 10px;
        background: rgba(26, 26, 46, 0.8);
    }

    QTabBar::tab {
        background: rgba(26, 26, 46, 0.8);
        color: #00ff95;
        padding: 8px 20px;
        margin: 2px;
        border: 2px solid #00ff95;
        border-radius: 5px;
    }

    QTabBar::tab:selected {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #00ff95, stop:1 #00b8ff);
        color: #1a1a2e;
    }

    QTabBar::tab:hover:!selected {
        background: rgba(0, 255, 149, 0.2);
    }

    QLabel#group_label {
        color: #00ff95;
        font-size: 14px;
        font-weight: bold;
        background: transparent;
        padding: 0px;
        margin: 0px;
    }

    /* Dialog styles */
    QDialog {
        background-color: #1a1a2e;
    }

    QDialog QTextEdit {
        background-color: rgba(26, 26, 46, 0.8);
        color: #00ff95;
        border: 2px solid #00ff95;
        border-radius: 10px;
        padding: 15px;
        font-family: 'Consolas';
        font-size: 13px;
    }

    QDialog QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #00ff95, stop:1 #00b8ff);
        color: #1a1a2e;
        padding: 12px;
        border: none;
        border-radius: 22px;
        font-size: 16px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    QDialog QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #00b8ff, stop:1 #00ff95);
    }

    QDialog QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #008c67, stop:1 #0081b3);
    }

    #language_button {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #00ff95, stop:1 #00b8ff);
        color: #1a1a2e;
        padding: 8px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: bold;
        min-width: 70px;
    }

    #language_button:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #00b8ff, stop:1 #00ff95);
    }

    #language_button:pressed {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #008c67, stop:1 #0081b3);
    }
"""
