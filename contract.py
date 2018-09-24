# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from __future__ import absolute_import
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.modules.account_bank.account import BankMixin

__all__ = [u'PaymentType', u'Contract', u'ContractConsumption']


class PaymentType(object):
    __metaclass__ = PoolMeta
    __name__ = u'account.payment.type'

    @classmethod
    def __setup__(cls):
        super(PaymentType, cls).__setup__()
        cls._check_modify_related_models.add((u'contract', u'payment_type'))


class Contract(BankMixin):
    __metaclass__ = PoolMeta
    __name__ = u'contract'

    payment_type = fields.Many2One(u'account.payment.type', u'Payment Type',
        domain=[
            (u'kind', u'in', [u'both', u'receivable']),
            ])

    @classmethod
    def default_payment_type(cls):
        PaymentType = Pool().get(u'account.payment.type')
        payment_types = PaymentType.search(cls.payment_type.domain)
        if len(payment_types) == 1:
            return payment_types[0].id

    @fields.depends(u'party')
    def on_change_party(self):
        self.payment_type = None
        self.bank_account = None
        super(Contract, self).on_change_party()
        if self.party and self.party.customer_payment_type:
            self.payment_type = self.party.customer_payment_type
        if self.payment_type:
            self._get_bank_account()

class ContractConsumption(object):
    __metaclass__ = PoolMeta
    __name__ = u'contract.consumption'

    @classmethod
    def _group_invoice_key(cls, line):
        consumption, invoice_line = line
        return super(ContractConsumption, cls)._group_invoice_key(line) + [
            (u'payment_type', consumption.contract.payment_type),
            (u'bank_account', consumption.contract.bank_account),
            ]

    @classmethod
    def _get_invoice(cls, keys):
        invoice = super(ContractConsumption, cls)._get_invoice(keys)
        values = dict(keys)
        invoice.payment_type = values[u'payment_type']
        invoice.bank_account = values[u'bank_account']
        return invoice
