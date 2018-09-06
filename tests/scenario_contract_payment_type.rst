=================
Contract Scenario
=================

Imports::

    >>> import datetime
    >>> from decimal import Decimal
    >>> from proteus import Model, Wizard, Report
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date(2015, 1, 1)

Install contract::

    >>> config = activate_modules('contract_payment_type')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company, today))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)

Create tax::

    >>> tax = create_tax(Decimal('.10'))
    >>> tax.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create payment type::

    >>> PaymentType = Model.get('account.payment.type')
    >>> payment_type = PaymentType(name='Receivable', kind='receivable',
    ...     account_bank='party')
    >>> payment_type.save()

Create bank account::

    >>> Party = Model.get('party.party')
    >>> party_bank = Party()
    >>> party_bank.save()

    >>> Bank = Model.get('bank')
    >>> bank = Bank()
    >>> bank.party = party_bank
    >>> bank.save()

    >>> BankAccount = Model.get('bank.account')
    >>> BankNumber = Model.get('bank.account.number')
    >>> bank_account = BankAccount()
    >>> bank_account.bank = bank
    >>> bank_account.numbers.append(BankNumber(type='other'))
    >>> bank_account.save()

Create party::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.customer_payment_term = payment_term
    >>> customer.customer_payment_type = payment_type
    >>> customer.bank_accounts.append(bank_account)
    >>> customer.save()

Configure contract::

    >>> ContractConfig = Model.get('contract.configuration')
    >>> Journal = Model.get('account.journal')

    >>> contract_config = ContractConfig(1)
    >>> contract_config.journal, = Journal.find([('type', '=', 'revenue')])
    >>> contract_config.payment_term = payment_term
    >>> contract_config.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> unit.rounding =  0.01
    >>> unit.digits = 2
    >>> unit.save()

    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> template = ProductTemplate()
    >>> template.name = 'service'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('40')
    >>> template.account_expense = accounts['expense']
    >>> template.account_revenue = accounts['revenue']
    >>> template.customer_taxes.append(tax)
    >>> template.save()
    >>> product, = template.products

    >>> Service = Model.get('contract.service')
    >>> service1 = Service(name='service1', product=product)
    >>> service1.save()
    >>> service2 = Service(name='service2', product=product)
    >>> service2.save()
    >>> service3 = Service(name='service3', product=product)
    >>> service3.save()
    >>> service4 = Service(name='service4', product=product)
    >>> service4.save()

Create Monthly Contract::

    >>> Contract = Model.get('contract')
    >>> contract = Contract()
    >>> contract.party = customer
    >>> contract.payment_term == payment_term
    True
    >>> contract.payment_type == payment_type
    True
    >>> contract.bank_account == bank_account
    True
    >>> contract.freq = 'monthly'
    >>> contract.interval = 1
    >>> contract.start_period_date = datetime.date(2015, 1, 1)
    >>> contract.first_invoice_date = datetime.date(2015, 1, 1)
    >>> line1 = contract.lines.new(
    ...     service=service1,
    ...     unit_price=Decimal(100),
    ...     start_date=datetime.date(2015, 1, 1),
    ...     end_date=datetime.date(2015, 3, 1))
    >>> line2 = contract.lines.new(
    ...     service=service2,
    ...     unit_price=Decimal(200),
    ...     start_date=datetime.date(2015, 1, 1),
    ...     end_date=datetime.date(2015, 2, 15))
    >>> line3 = contract.lines.new(
    ...     service=service3,
    ...     unit_price=Decimal(300),
    ...     start_date=datetime.date(2015, 2, 15),
    ...     end_date=datetime.date(2015, 2, 28))
    >>> line4 = contract.lines.new(
    ...     service=service4,
    ...     unit_price=Decimal(400),
    ...     start_date=datetime.date(2015, 2, 15),
    ...     end_date=None)
    >>> contract.save()

    >>> contract.click('confirm')
    >>> contract.state
    u'confirmed'

Create consumptions for 2015-01-31::

    >>> Consumption = Model.get('contract.consumption')
    >>> create_consumptions = Wizard('contract.create_consumptions')
    >>> create_consumptions.form.date = datetime.date(2015, 1, 31)
    >>> create_consumptions.execute('create_consumptions')

    >>> consumptions = Consumption.find([])
    >>> len(consumptions)
    2

Create consumptions for 2015-02-28::

    >>> create_consumptions = Wizard('contract.create_consumptions')
    >>> create_consumptions.form.date = datetime.date(2015, 2, 28)
    >>> create_consumptions.execute('create_consumptions')

    >>> consumptions = Consumption.find([])
    >>> len(consumptions)
    6

Create consumptions for 2015-04-01::

    >>> create_consumptions = Wizard('contract.create_consumptions')
    >>> create_consumptions.form.date = datetime.date(2015, 4, 1)
    >>> create_consumptions.execute('create_consumptions')

    >>> consumptions = Consumption.find([])
    >>> len(consumptions)
    9

Check consumptions dates::

    >>> consumptions = Consumption.find([])
    >>> [(c.contract_line.service.name,
    ...         str(c.init_period_date), str(c.end_period_date),
    ...         str(c.start_date), str(c.end_date),
    ...         str(c.invoice_date))
    ...     for c in consumptions] == \
    ... [('service1',
    ...         '2015-01-01', '2015-01-31',
    ...         '2015-01-01', '2015-01-31',
    ...         '2015-01-01'),
    ...     ('service2',
    ...         '2015-01-01', '2015-01-31',
    ...         '2015-01-01', '2015-01-31',
    ...         '2015-01-01'),
    ...     ('service1',
    ...         '2015-02-01', '2015-02-28',
    ...         '2015-02-01', '2015-02-28',
    ...         '2015-02-01'),  # XXX
    ...     ('service2',
    ...         '2015-02-01', '2015-02-28',
    ...         '2015-02-01', '2015-02-15',
    ...         '2015-02-01'),  # XXX
    ...     ('service3',
    ...         '2015-02-01', '2015-02-28',
    ...         '2015-02-15', '2015-02-28',
    ...         '2015-02-01'),
    ...     ('service4',
    ...         '2015-02-01', '2015-02-28',
    ...         '2015-02-15', '2015-02-28',
    ...         '2015-02-01'),
    ...     ('service1',
    ...         '2015-03-01', '2015-03-31',
    ...         '2015-03-01', '2015-03-01',
    ...         '2015-03-01'),  # XXX
    ...     ('service4',
    ...         '2015-03-01', '2015-03-31',
    ...         '2015-03-01', '2015-03-31',
    ...         '2015-03-01'),  # XXX
    ...     ('service4',
    ...         '2015-04-01', '2015-04-30',
    ...         '2015-04-01', '2015-04-30',
    ...         '2015-04-01'),
    ...     ]
    True

Create invoice on 2015-02-15::

    >>> Invoice = Model.get('account.invoice')
    >>> create_invoices = Wizard('contract.create_invoices')
    >>> create_invoices.form.date = datetime.date(2015, 2, 15)
    >>> create_invoices.execute('create_invoices')

    >>> invoices = Invoice.find([])
    >>> len(invoices)
    2

Create invoice on 2015-04-01::

    >>> create_invoices = Wizard('contract.create_invoices')
    >>> create_invoices.form.date = datetime.date(2015, 4, 1)
    >>> create_invoices.execute('create_invoices')

    >>> invoices = Invoice.find([])
    >>> len(invoices)
    4

Check invoice lines amount::

    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> lines = InvoiceLine.find([])
    >>> sorted([(l.origin.contract_line.service.name,
    ...         str(l.invoice.invoice_date), l.amount)
    ...     for l in lines]) == \
    ... sorted([(u'service1', '2015-01-01', Decimal('100.00')),
    ...     (u'service2', '2015-01-01', Decimal('200.00')),
    ...     (u'service1', '2015-02-01', Decimal('100.00')),
    ...     (u'service2', '2015-02-01', Decimal('107.14')),
    ...     (u'service3', '2015-02-01', Decimal('150.00')),
    ...     (u'service4', '2015-02-01', Decimal('200.00')),
    ...     (u'service4', '2015-03-01', Decimal('400.00')),
    ...     (u'service1', '2015-03-01', Decimal('3.23')),
    ...     (u'service4', '2015-04-01', Decimal('400.00')),
    ...     ])
    True
