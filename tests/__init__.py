# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.contract.tests.test_contract_payment_type import suite
except ImportError:
    from .test_contract_payment_type import suite

__all__ = ['suite']
