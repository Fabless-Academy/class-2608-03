# QT Designer 기반의 개발 환경 구축

QT designer를 기반으로 UI를 design 하고 이를 이용하여 application을 완성한다.

## QT Designer install

* Python `pyqt5-tools` package를 host pc에 install

```powershell
pip install pyqt5-tools
```

## `qt-designer` 실행

1. `Win` + `R` --> `%APPDATA%\Python\Python39\site-packages\qt5_applications\qt\bin` --> `enter`
2. `designer.exe` 실행 or `바로가기` 만들고 실행

    ```text  
    %APPDATA%\Python\Python39\site-packages\qt5_applications\qt\bin
    ```

## design이 하고 `.ui` file 생성

## proejct folder로 copy

---

## PyQt 환경 구축

### install `python3-pyqt5` on D3-G

```bash
sudo apt install python3-pyqt5
```

### `main.py` example

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic  # .ui 파일을 로드하는 모듈

# Qt Designer에서 생성한 .ui 파일 경로
form_class = uic.loadUiType("qt_hello.ui")[0]

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # UI 구성 요소 초기화

        # Designer에서 설정한 objectName(예: btn_click, label_title)으로 바로 접근
        # 예: 버튼 클릭 시 이벤트 연결
        if hasattr(self, 'btn_click'):
            self.btn_click.clicked.connect(self.on_button_clicked)

    def on_button_clicked(self):
        print("버튼이 클릭되었습니다!")
        if hasattr(self, 'label_title'):
            self.label_title.setText("Hello Python Qt!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
```
