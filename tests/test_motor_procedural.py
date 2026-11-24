"""Testes de integração do motor procedural, rotas Flask e exportadores."""

from __future__ import annotations

import unittest

from scripts import validar_motor_procedural


class MotorProceduralIntegracaoTests(unittest.TestCase):
    """Executa a suíte completa de validação de integração (56 conceitos, 29 heranças, Flask e exportação)."""

    def test_integracao_completa_motor_flask_e_exportadores(self) -> None:
        validar_motor_procedural.main()


if __name__ == "__main__":
    unittest.main()
