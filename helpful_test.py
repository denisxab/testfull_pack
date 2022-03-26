from doctest import testmod
from subprocess import check_output, CalledProcessError, STDOUT
from types import ModuleType
from typing import Any
from unittest import TestCase

from logsmal import logger
from logsmal import loglevel

logger.testfull_pack_info = logger.info
logger.testfull_pack_info.title_logger = 'TEST_FULL_PACK INFO'
logger.testfull_pack_error = logger.error
logger.testfull_pack_error.title_logger = 'TEST_FULL_PACK ERROR'


def os_exe(
        command: list[str],
) -> tuple[bool, Any, int]:
    """
    Выполнить CLI команду и получить ответ
    :param command:
    :return: ПроизошлаЛиОшибка, Ответ, КодОтвета
    """
    try:
        _response: bytes = check_output(command, shell=True, stderr=STDOUT)
        return True, _response.decode('utf-8'), 0
    except CalledProcessError as e:
        return False, e.output.decode('utf-8'), e.returncode


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
        # Модули у которых нужно проводить док тесты
    )

    def setUp(self):
        # Отключаем логирование ``logsmal``
        loglevel.__call__ = lambda *args, **kwargs: None

    def test_docs_from_module(self):
        for _m in TestDoc.list_mod:
            # Выполняем док тесты
            self.assertEqual(testmod(_m).failed, 0)
