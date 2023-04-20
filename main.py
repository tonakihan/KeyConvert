#!/usr/bin/env python3

import logging # Для логирования программы
import codecs  # Для кодировки файла

logging.basicConfig(
            level    = logging.INFO,
            filename = "/tmp/trFile.log",
            encoding = "utf-8",
            filemode = 'w',
            format   = '%(asctime)s %(levelname)s: %(message)s',
            datefmt  = "%m-%d-%Y %H:%M:%S")

logger = logging.getLogger(__name__) # Создать экземпляр логера
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


class Keylog:
    containerLines = None # Отсортированные строки файла
    numLine = None        # Номер текущей строки 
    lenCont = None        # Кол-во строк в файле

    def __init__(self, container):
        logger.debug("Keylog: Created object...")
        self.containerLines = container
        self.numLine = 0
        self.lenCont = len(container)
        logger.debug(f'Keylog: Succes! Parameter object:\
                     \n\t{self.containerLines=}\
                     \n\t{self.numLine=} {self.lenCont=}')


    def getCodeSymbool(self, numLine:int = -1) -> int:
    # Принимает номер строки и возвращает код клавиши.
        if numLine == -1:
            numLine = self.numLine

        logger.debug("Keylog.getCodeSymbool: Completed")

        line = self.containerLines[numLine]
        if line[6] == '[':
            match line[line.find('[')+1:line.find(']')]:
                case 'SPACE':
                    return 32
                case 'WIN':
                    return 91
                case 'F1':
                    return 112
                case 'F2':
                    return 113
                case 'F3':
                    return 114
                case 'F4':
                    return 115
                case 'F5':
                    return 116
                case 'F6':
                    return 117
                case 'F7':
                    return 118
                case 'F8':
                    return 119
                case 'F9':
                    return 120
                case 'F10':
                    return 121
                case 'F11':
                   return 122
                case 'F12':
                    return 123
                case 'SHIFT':
                    return 16
                case 'ESC':
                    return 27
                case 'ALT':
                    return 18
                case 'left':
                    return 37
                case 'up':
                    return 38
                case 'right':
                    return 39
                case 'down':
                    return 40
                case 'BACKSPACE':
                    return 8
                case 'ENTER':
                    return 13
                case 'CTRL':
                    return 17
                case 'CAPSLOCK':
                    return 20
        else: 
            return ord(line[6])


    def statusKey(self, numLine:int = -1) -> str:
    """
    Проверяет по номеру строки, какой в ней статус клавиши.
    Возвращает 'down'/'up'/'nothing'
    """
        if numLine == -1:
            numLine = self.numLine

        logger.debug(f'Keylog.statusKey: Begining. Input: {numLine=}')

        if self.containerLines[numLine][0:4] == 'Down':
            logger.debug("Keylog.statusKey: Ending. Result - down")
            return 'down'
        if self.containerLines[numLine][0:2] == 'Up':
            logger.debug("Keylog.statusKey: Ending. Result - up")
            return 'up'
        else:
            logger.debug("Keylog.statusKey: Ending. Result - NOTHING!")
            return 'nothing'


    def searchNextLine(self, statusKey:str, numLine:int = -1) -> int:
    """
    Метод принимает аргумент - положение клавиши, 
    а после ищет нужную строку, которая содержит этот аргумент.
    Возвращает номер строки.
    """
        if numLine == -1:
            numLine = self.numLine
       
        logger.debug('Keylog.searchNextLine: Begining. Input: ')
        logger.debug(f'\t{statusKey=}')
        logger.debug(f'\t{numLine=}')
        logger.debug('(Keylog.searchNextLine) symbool=%s', symbool:=self.getCodeSymbool(numLine)) 

        while numLine < self.lenCont:
            numLine += 1
            if numLine == self.lenCont: #Нет больше строк
                break

            if self.statusKey(numLine) == statusKey: #Что-то насщупал
                if statusKey == 'down': #Нашел down
                    logger.debug(f'Keylog.searchNextLine: Ending. Result: {numLine=}  {statusKey=}')
                    return numLine
                elif self.getCodeSymbool(numLine) == symbool: #Нашел up
                    logger.debug(f'Keylog.searchNextLine: Ending. Result: {numLine=}  {statusKey=}')
                    return numLine

        logger.debug("Keylog.searchNextLine: Next line - does not exit!")
        return None


    def getTime(self, mode:str) -> int:
    """
    Принимает значение - какое найти время,
    после обращается в findTime и возвращает время.
    """
        logger.debug("Keylog.getTime: Begining")

        # Ищет в строке время и возвращает его.
        def findTime(line:str) -> int:
            logger.debug(f'Keylog.getTime.findTime: Begining. Input: {line=}')

            if line.count(':') == 0:
                logger.debug('Keylog.getTime.findTime: Part =0 - run')
                result = line[line.find(' ')+1:line.find('m')]
                logger.debug(f'Keylog.getTime.findTime: Ending. Result: {result}')
                return int(result)

            elif line.count(':') > 0:
                logger.debug('Keylog.getTime.findTime: Recursion')
                return findTime(line[line.find(':')+1:])

            else:
                logger.error("Keylog.getTime.findTime: EXCEPTION!")
                return None

        # Вернет как долго была нажата клавиша
        if mode == 'down': 
            logger.debug('Keylog.getTime: Mode "down" - run')

            line = self.containerLines[self.searchNextLine('up')]
            result = findTime(line)

            logger.debug(f'Keylog.getTime: Ending. Result: {line=} {result=}')
            return result

        # Вернет промежуток времени с момента нажатия прошлой клавиши до нажатия след.
        elif mode == 'wait': 
            logger.debug('Keylog.getTime: Mode "wait" - run')

            line = self.containerLines[self.numLine]
            currentTime = findTime(line)

            if self.searchNextLine('down') == None: # Конец файла, нет строки далее.
                return 0
            else:
                line = self.containerLines[self.searchNextLine('down')]
                nextTime = findTime(line)
                logger.debug(f"Keylog.getTime: Ending. Result: {currentTime=} {nextTime=}")
                return nextTime - currentTime

    def nextLine(self):
    # Сдвиает текущую строку на 1 шаг (глобально).
        global numLine
        self.numLine += 1
        logger.debug(f'Keylog.nextLine: Completed. Current line {self.numLine}')
    
    def getLenCont(self) -> int:
    # Возвращает значение кол-ва строк.
        logger.debug('Keylog.getLenCont: Completed')
        return self.lenCont

    def endOf(self) -> bool:
    # Проверка, окончен ли файл.
        res = self.lenCont - self.numLine
        logger.debug(f'Keylog.endOf: Completed. Result {res}')
        if res <= 0:
            return True
        return False


def main():
    logger.info("Started") # TEST
    patchToFileSrc = input("Введите путь до файла >> ")

    with codecs.open(
                patchToFileSrc, 
                'r', 
                "cp1251") as fSource, \
         codecs.open(
                "result.log", 
                'w', 
                "utf-8")  as fWrite:

            logger.debug("Sourse file - open.") 

            obj = Keylog(fSource.readlines())

            fWrite.write("<CodeKey>\t<TimeDownKey>\t<TimeWait>\n")

            while obj.endOf() == False:
                logger.debug("Begining while")

                if obj.statusKey() == "down":
                    fWrite.write(str(obj.getCodeSymbool()) + '\t' + 
                                 str(obj.getTime('down')) + '\t' + 
                                 str(obj.getTime('wait')) + '\n')
                    logger.debug("if \"down\": line write in file")
            
                obj.nextLine()
                logger.debug("Ending")

    logger.info("Finished")


if __name__ == "__main__":
    main()
