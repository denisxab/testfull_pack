import os.path
from doctest import testmod
from hashlib import sha256
from os import environ
from os.path import exists
from pprint import pprint
from re import sub
from types import ModuleType
from typing import Optional
from unittest import TestCase

from logsmal import loglevel


def readAndSetEnv(*path_files: str):
    """
    Чтение переменных окружения из указанного файла,
    и добавление их в ПО `python`
    """
    for _path_file in path_files:
        if exists(_path_file):
            with open(_path_file, 'r', encoding='utf-8') as _file:
                res = {}
                for line in _file:
                    tmp = sub(r'^#[\s\w\d\W\t]*|[\t\s]', '', line)
                    if tmp:
                        k, v = tmp.split('=', 1)
                        # Если значение заключено в двойные кавычки, то нужно эти кавычки убрать
                        if v.startswith('"') and v.endswith('"'):
                            v = v[1:-1]

                        res[k] = v
            environ.update(res)
            pprint(res)
        else:
            logger.warning(f"No search file {_path_file}")


class BaseHash:

    @staticmethod
    def file(path_file: str):
        """
        Получить хеш сумму данных в файле, по его пути

        :param path_file: Путь к файлу
        """
        h = sha256()
        b = bytearray(128 * 1024)
        mv = memoryview(b)
        with open(path_file, 'rb', buffering=0) as f:
            for n in iter(lambda: f.readinto(mv), 0):
                h.update(mv[:n])
        return h.hexdigest()

    @staticmethod
    def text(text: str) -> str:
        """
        Получить хеш сумму текста
        """
        return sha256(text.encode()).hexdigest()

    @staticmethod
    def check_hash_sum(unknown_hash_sum: str, true_hash_sum: str):
        """
        Сравить хеш суммы

        :param unknown_hash_sum: Полученная(неизвестная) хеш сумма
        :param true_hash_sum: Требуемая хеш сумма
        """
        if unknown_hash_sum != true_hash_sum:
            raise ValueError(f"{unknown_hash_sum} != {true_hash_sum}")
        return True


def проверить_подлинность_файла(infile: str, hash_sum: str):
    return BaseHash.check_hash_sum(BaseHash.file(infile), hash_sum)


def проверить_подлиность_текст(text: str, hash_sum: str):
    return BaseHash.check_hash_sum(BaseHash.text(text), hash_sum)


class ТестовыйФайл:
    """
    Вернуть файл если хеш сумма верна
    """

    def __init__(self, path: str, hash_sum: Optional[str]):
        """
        Проверить подлинность файла

        :param path:
        :param hash_sum:
        """
        if hash_sum is not None:
            проверить_подлинность_файла(path, hash_sum)
        self.path = path
        self.full_path = os.path.abspath(self.path)

    def прочесть(self):
        with open(self.full_path, "r", encoding='utf-8') as _f:
            return _f.read()

    def обновить(self, text: str):
        with open(self.full_path, "w", encoding='utf-8') as _f:
            return _f.write(text)


class ПрочитанныйТестовыйФайл(ТестовыйФайл):
    """
    Вернуть данные из фала если хеш сумма верна
    """

    def __init__(self, path: str, hash_sum: Optional[str]):
        """
        Проверить подлинность файла

        :param path:
        :param hash_sum:
        """
        super().__init__(path, hash_sum)
        self.__текст = None

    @property
    def текст(self):
        # Записать данные в переменную из файла, только при первом обращении.
        if self.__текст is None:
            return self.прочесть()
        return self.__текст


class ОткатываемыйФайл(ПрочитанныйТестовыйФайл):
    """
    Файл с возможностью отката данных, на момент создания класса.
    Или удалить файл, если он не был создан, на момент создания класса.


    with ОткатываемыйФайл():
        ...
    """

    def __init__(self, path: str, hash_sum: Optional[str]):
        super().__init__(path, hash_sum)
        self.существование = os.path.exists(self.full_path)
        # Если файл не существовал, то удаляем его при откате
        if not self.существование:
            self.прошлые_данные_из_файла = ''
        else:
            self.прошлые_данные_из_файла: str = self.текст

    def откатить(self):
        if self.существование:
            with open(self.full_path, 'w', encoding='utf-8') as _f:
                _f.write(self.прошлые_данные_из_файла)
        else:
            os.remove(self.full_path)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.откатить()


class TestDoc(TestCase):
    """
    Протестировать документацию у модулей

    .. code-block::python

        import logic_helpful
        from configer.test.helpful_test import TestDoc

        # Док тесты
        TestDoc.list_mod = (
            logic_helpful,
        )
    """
    #: Список модулей
    list_mod: tuple[ModuleType] = (
        # МОДУЛИ
    )

    def setUp(self):
        # Отключаем логирование ``logsmal``
        loglevel.__call__ = lambda *args, **kwargs: None

    def test_docs_from_module(self):
        for _m in TestDoc.list_mod:
            # Выполняем док тесты
            self.assertEqual(testmod(_m).failed, 0)
