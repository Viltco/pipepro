# -*- coding: utf-8 -*-

import datetime
from lxml import etree
from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import float_compare


class CustomReport(models.AbstractModel):
    _name = "report.vlc_cost_analysis_report.cost_analysis_template"

    def check_balance(self, partner_id, date_from, date_to ):
        partner_ledger = self.env['account.move.line'].search(
                    [('partner_id', '=',partner_id.id),
                     ('date', '>=', date_from),
                     ('date', '<=', date_to),
                     ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
                     ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
                     ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
        bal = 0
        db = 0
        cr = 0
        values = dict()
        for par_rec in partner_ledger:
            db = db + par_rec.debit
            cr = cr + par_rec.credit
            bal = bal + (par_rec.debit - par_rec.credit)
        values['debit'] = db
        values['credit'] = cr
        values['balance'] = bal
        return values

    def _get_report_values(self, docids, data=None):
        record = self.env['pdc.payment'].browse(data['context']['active_id'])
        return {
            'doc_ids': self.ids,
            'doc_model': 'partner.ledger',
            'bal': self.check_balance,
            'record': record,
            'data': data,
        }

