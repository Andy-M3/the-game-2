from random import randint #импорт функции randit


#Класс точка
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eg__(self, other):        #данный метод отвечает за сравнение двух объектов
        return self.x == other.x and self.y == other.y

    def __repr__(self):            #вывод точек в консоль
        return f"Dot({self.x}, {self.y})"

#Классы исключений

class BoardException(Exception): #Общий класс исключений
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException): #исключение для размещения кораблей
    pass

#Класс корабля

class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l
    @property #свойство
    def dots(self): #Список точек для описания координат корабля
        ship_dots = []
        for i in range (self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append (Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):      #проверка попали мы в корабль или нет
        return shot in self.dots


#Класс игровое поле

class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0  #кол-во пораженных кораблей

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []   #занятые точки
        self.ships = []     #список кораблей на доске

    def __str__(self): #Метод вызова доски
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate ( self.field ) :
            res += f"\n{i + 1} | " + " | ".join ( row ) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res
    def out(self, d):       #Находится ли точка за пределами доски
        return not((0<= d.x < self.size) and (0<= d.y < self.size))
#Добавление корабля на доску
    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ] #объявляем сдвиги точки
        for d in ship.dots:
            for dx, dy in near: #проходим в цикле по neer
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship): #Размещение корабля

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d): #функция стрельбы
        if self.out(d): #проверка выхода за границы, если выходит выводим исключение
            raise BoardOutException()

        if d in self.busy: #проверка занята ли точка, если занята выводи исключение
            raise BoardUsedException()

        self.busy.append(d) #говорим что точка занята, если она еще не была занятой

        for ship in self.ships: #проходимся в цикле по кораблю
            if d in ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print ( "Корабль уничтожен!")
                    return False
                else :
                    print ( "Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    #Описываем класс игрока

class Player :
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI (Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User (Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите две координаты! ")
                continue

            x, y = cords

            if not (x.isdigit ()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)
#описываем класс игры
class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self): #в данном методе пытаемся расставить корабли на поле
        lens = [3, 2, 2, 1, 1, 1, 1] #длина кораблей
        board = Board(size=self.size) #создание доски
        attempts = 0
        for l in lens: #ставим корабли
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self): #функция создания доски
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("   War of Warships   ")
        print("----------------------")
        print(' Ввод координат:')
        print(" сначала номер строки  ")
        print(" потом  номер столбца ")

    def loop(self) :
        num = 0
        while True :
            print ( "-" * 20 )
            print ( "Поле игрока:" )
            print ( self.us.board )
            print("-" * 20)
            print("Поле компьютера:")
            print ( self.ai.board)
            if num % 2 == 0 :
                print("-" * 20)
                print("Ход пользователя!")
                repeat = self.us.move()
            else :
                print ( "-" * 20 )
                print ( "Ход компьютера!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20 )
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game ()
g.start ()




