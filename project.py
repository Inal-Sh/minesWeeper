import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QMessageBox, QVBoxLayout


class DifficultySelection(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выберите сложность")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        easy_button = QPushButton("Легкий")
        medium_button = QPushButton("Средний")
        hard_button = QPushButton("Сложный")

        easy_button.clicked.connect(lambda: self.start_game(10, 10, 10))  # 10x10, 10 мин
        medium_button.clicked.connect(lambda: self.start_game(16, 16, 40))  # 16x16, 40 мин
        hard_button.clicked.connect(lambda: self.start_game(20, 20, 99))  # 20x20, 99 мин

        layout.addWidget(easy_button)
        layout.addWidget(medium_button)
        layout.addWidget(hard_button)

        self.setLayout(layout)

    def start_game(self, rows, cols, mines):
        self.game_window = Minesweeper(rows, cols, mines)
        self.game_window.show()
        self.close()  # Закрываем окно выбора сложности


class Cell(QPushButton):
    def __init__(self, x, y, size):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.is_mine = False
        self.is_revealed = False
        self.neighbor_mines = 0
        self.flagged = False
        self.setFixedSize(size, size)
        self.setStyleSheet("font-size: 20px; background-color: lightblue;")

    def reveal(self):
        if not self.is_revealed and not self.flagged:
            self.is_revealed = True
            if self.is_mine:
                self.setText('*')
                self.setStyleSheet("background-color: red; color: white;")
                return False  # Game Over
            else:
                self.setStyleSheet("background-color: lightgrey;")
                if self.neighbor_mines > 0:
                    self.setText(str(self.neighbor_mines))
                return True  # Continue game
        return True  # Already revealed

    def toggle_flag(self):
        if not self.is_revealed:
            self.flagged = not self.flagged
            if self.flagged:
                self.setText('🚩')
                self.setStyleSheet("font-size: 20px; background-color: lightblue; color: red;")
            else:
                self.setText('')
                self.setStyleSheet("font-size: 20px; background-color: lightblue;")

    def contextMenuEvent(self, event):
        self.toggle_flag()


class Minesweeper(QMainWindow):
    def __init__(self, rows=10, cols=10, mines=10):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.cells = [[Cell(r, c, 40) for c in range(cols)] for r in range(rows)]
        self.initUI()
        self.place_mines()
        self.calculate_neighbors()

    def initUI(self):
        self.setWindowTitle("Сапер")
        central_widget = QWidget()
        layout = QGridLayout()

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[r][c]
                cell.clicked.connect(self.cell_clicked)
                layout.addWidget(cell, r, c)

        central_widget.setLayout(layout)

        # Установка цвета фона для главного окна
        self.setStyleSheet("background-color: lightgreen;")

        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет

    def cell_clicked(self):
        button = self.sender()
        if button is not None:
            if not button.flagged:
                if not button.reveal():
                    self.game_over()
                else:
                    if button.neighbor_mines == 0:
                        self.reveal_adjacent_cells(button.x, button.y)
                    self.check_win()

    def reveal_adjacent_cells(self, x, y):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                neighbor_x = x + dr
                neighbor_y = y + dc
                if 0 <= neighbor_x < self.rows and 0 <= neighbor_y < self.cols:
                    neighbor_cell = self.cells[neighbor_x][neighbor_y]
                    if not neighbor_cell.is_revealed and not neighbor_cell.flagged:
                        if neighbor_cell.reveal() and neighbor_cell.neighbor_mines == 0:
                                            # Рекурсивно раскрываем соседние клетки
                            self.reveal_adjacent_cells(neighbor_x, neighbor_y)

    def place_mines(self):
        mine_positions = random.sample(range(self.rows * self.cols), self.mines)
        for pos in mine_positions:
            row = pos // self.cols
            col = pos % self.cols
            self.cells[row][col].is_mine = True

    def calculate_neighbors(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c].is_mine:
                    continue
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        neighbor_row = r + dr
                        neighbor_col = c + dc
                        if 0 <= neighbor_row < self.rows and 0 <= neighbor_col < self.cols:
                            if self.cells[neighbor_row][neighbor_col].is_mine:
                                self.cells[r][c].neighbor_mines += 1

    def game_over(self):
        QMessageBox.warning(self, "Игра окончена", "Вы попали на мину! Игра окончена!")
        self.reset_game()

    def check_win(self):
        revealed_cells = sum(cell.is_revealed for row in self.cells for cell in row)
        if revealed_cells == (self.rows * self.cols - self.mines):
            QMessageBox.information(self, "Поздравляем!", "Вы очистили поле!")
            self.reset_game()

    def reset_game(self):
        for row in self.cells:
            for cell in row:
                cell.is_revealed = False
                cell.is_mine = False
                cell.neighbor_mines = 0
                cell.flagged = False
                cell.setText('')
                cell.setStyleSheet("font-size: 20px; background-color: lightblue;")

        self.place_mines()
        self.calculate_neighbors()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    difficulty_selection = DifficultySelection()
    difficulty_selection.show()
    sys.exit(app.exec())
