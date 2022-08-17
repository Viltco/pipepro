# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class MrpWorkcenterInh(models.Model):
    _inherit = 'mrp.workcenter'

    man_power = fields.Float()
    machine_cost = fields.Float()
    oh_cost = fields.Float()

    @api.onchange('man_power', 'machine_cost', 'oh_cost')
    def onchange_man(self):
        self.costs_hour = self.oh_cost + self.man_power + self.machine_cost



class MrpInh(models.Model):
    _inherit = 'mrp.production'

    # picking_for_id = fields.Many2one('stock.picking')
    produced_lines = fields.One2many('produced.qty.line', 'mrp_id')
    # lot_lines = fields.One2many('unique.lot', 'mrp_id')
    reason_lines = fields.One2many('reason.line', 'mrp_id')
    entry_lines = fields.One2many('entry.line', 'mrp_id')

    def button_mark_done(self):
        self.compute_entry_lines()
        rec = super(MrpInh, self).button_mark_done()
        return rec

    def compute_entry_lines(self):
        for record in self:
            if record:
                mn_pwr = 0
                mchn_cst = 0
                oh_cst = 0
                tot_cst = 0
                for workline in record.workorder_ids:
                    mn_pwr = mn_pwr + workline.workcenter_id.man_power
                    mchn_cst = mchn_cst + workline.workcenter_id.machine_cost
                    oh_cst = oh_cst + workline.workcenter_id.oh_cost
                tot_cst = mn_pwr + mchn_cst + oh_cst
                record.update({
                    'entry_lines': [(0, 0, {
                        'mrp_id': record.id,
                        'mn_power': mn_pwr,
                        'machine_cost': mchn_cst,
                        'oh_cost': oh_cst,
                        'total_cost': tot_cst
                    })]
                })
            else:
                record.update({
                    'entry_lines': [(0, 0, {
                        'mrp_id': record.id,
                        'mn_power': 0,
                        'machine_cost': 0,
                        'oh_cost': 0
                    })]
                })
        self.create_draft_entry()

    def create_draft_entry(self):
        line_ids = []
        one_debit_sum = 0.0
        two_debit_sum = 0.0
        three_debit_sum = 0.0
        credit_sum = 0.0
        for line in self.entry_lines:
            move_dict = {
                'ref': self.name,
                'partner_id': self.user_id.partner_id.id,
                'date': datetime.today(),
                'state': 'draft',
            }
            one_debit_account = self.env['account.account'].search([('name', '=', 'Man Power Standard Cost')], limit=1)
            one_debit_line = (0, 0, {
                'name': 'Man Power Standard Cost',
                'debit': line.mn_power,
                'credit': 0.0,
                'partner_id': self.user_id.partner_id.id,
                'account_id': one_debit_account.id,
            })
            line_ids.append(one_debit_line)
            one_debit_sum += one_debit_line[2]['debit'] - one_debit_line[2]['credit']
            two_debit_account = self.env['account.account'].search([('name', '=', 'Machine Standard Cost')], limit=1)
            two_debit_line = (0, 0, {
                'name': 'Machine Standard Cost',
                'debit': line.machine_cost,
                'credit': 0.0,
                'partner_id': self.user_id.partner_id.id,
                'account_id': two_debit_account.id,
            })
            line_ids.append(two_debit_line)
            two_debit_sum += two_debit_line[2]['debit'] - two_debit_line[2]['credit']
            three_debit_account = self.env['account.account'].search([('name', '=', 'OH Standard Cost')], limit=1)
            three_debit_line = (0, 0, {
                'name': 'OH Cost',
                'debit': line.oh_cost,
                'credit': 0.0,
                'partner_id': self.user_id.partner_id.id,
                'account_id': three_debit_account.id,
            })
            line_ids.append(three_debit_line)
            three_debit_sum += three_debit_line[2]['debit'] - three_debit_line[2]['credit']
            credit_account = self.env['account.account'].search([('name', '=', 'Work In Process')], limit=1)
            credit_line = (0, 0, {
                'name': 'Work In Process',
                'debit': 0.0,
                'partner_id': self.user_id.partner_id.id,
                'credit': line.total_cost,
                'account_id': credit_account.id,
            })
            line_ids.append(credit_line)
            credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            line_ids = []
            break
            print('JV Created')



class ProducedQtyLine(models.Model):
    _name = 'produced.qty.line'

    mrp_id = fields.Many2one('mrp.production')
    workcenter_id = fields.Many2one('mrp.workcenter')
    # workcenter_machine_id = fields.Many2one('centre.machine')
    # employee_id = fields.Many2one('hr.employee')
    name = fields.Char('Operation')
    qty = fields.Float('Produced Quantity')
    start_date = fields.Datetime('Start Date')
    paused_date = fields.Datetime('End Date')


class ReasonLine(models.Model):
    _name = 'reason.line'

    mrp_id = fields.Many2one('mrp.production')
    workcenter_id = fields.Many2one('mrp.workcenter')
    # workcenter_machine_id = fields.Many2one('centre.machine')
    # employee_id = fields.Many2one('hr.employee')
    name = fields.Char('Operation')
    qty = fields.Float('Produced Quantity')
    start_date = fields.Datetime('Start Date')
    paused_date = fields.Datetime('End Date')
    # reason = fields.Char('Reason')
    reason = fields.Selection([
        ('wrong', 'Wrong Cutting'),
        ('burn', 'Burn'),
        ('hole', 'Hole'),
        ('shortage', 'Shortage of material during welding'),
        ('excess', 'Excess of material during welding'),
    ], string='Reason', default='', ondelete='cascade')


class MrpOrderInh(models.Model):
    _inherit = 'mrp.workorder'

    start_date_custom = fields.Datetime('Date Start')
    lot = fields.Char()
    # unique_lots = fields.Many2many('unique.lot')

    def button_finish(self):
        for rec in self:
            pre_order = self.env['mrp.workorder'].search([('id', '=', rec.id-1), ('production_id', '=', rec.production_id.id)])
            if pre_order:
                if pre_order.state != 'done':
                    raise UserError('This workorder is waiting for another operation to get done.')
            # record = super(MrpOrderInh, self).button_finish()
            # for rec in self:
            #     qty = 0
            #     for line in rec.production_id.produced_lines:
            #         if line.name == rec.name and line.workcenter_id.id == rec.workcenter_id.id:
            #             qty = qty + line.qty
            #     res = self.env['produced.qty.line'].create({
            #         'mrp_id': rec.production_id.id,
            #         'name': rec.name,
            #         'workcenter_id': rec.workcenter_id.id,
            #         'workcenter_machine_id': rec.workcenter_machine_id.id,
            #         'employee_id': rec.employee_id.id,
            #         'qty': rec.production_id.qty_producing - qty,
            #         'paused_date': datetime.today(),
            #         'start_date': rec.start_date_custom,
            #     })
            # if not self.production_id.product_id.is_process_b:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Done Quantity',
                'view_id': self.env.ref('pipe_overall.view_done_wizard_form', False).id,
                'target': 'new',
                'res_model': 'done.qty.wizard',
                'view_mode': 'form',
            }
            # else:
            #     return {
            #         'type': 'ir.actions.act_window',
            #         'name': 'Finish Lot',
            #         'view_id': self.env.ref('production_overall.view_finish_lot_wizard_form', False).id,
            #         'target': 'new',
            #         'res_model': 'finish.lot.wizard',
            #         'view_mode': 'form',
            #     }

        # return record

    def button_start(self):
        for rec in self:
            pre_order = self.env['mrp.workorder'].search([('id', '=', rec.id-1), ('production_id', '=', rec.production_id.id)])

            current_qty = sum(self.env['produced.qty.line'].search(
                [('mrp_id', '=', rec.production_id.id), ('workcenter_id', '=', rec.workcenter_id.id)]).mapped('qty'))
            pre_qty = 0
            if pre_order:
                pre_qty = sum(self.env['produced.qty.line'].search(
                    [('mrp_id', '=', pre_order.production_id.id), ('workcenter_id', '=', pre_order.workcenter_id.id)]).mapped('qty'))
                if pre_qty <= current_qty:
                    raise ValidationError('Produced Quantity can not be greater than Quantity to Produce!!!!!!')

            # if not rec.production_id.product_id.is_process_b:
            # for line in rec.production_id.move_raw_ids:
            #     if line.product_uom_qty != line.reserved_availability:
            #         raise UserError('Required components are not available to start this work order.')
            record = super(MrpOrderInh, self).button_start()
            rec.start_date_custom = datetime.today()
            # else:
                # print(self.unique_lots.mapped('id'))
                # return {
                #     'type': 'ir.actions.act_window',
                #     'name': 'Produced Lot',
                #     'view_id': self.env.ref('production_overall.view_produced_lot_wizard_form', False).id,
                #     'target': 'new',
                #     'context': {'default_production_id': rec.production_id.id},
                #     'res_model': 'produced.lot.wizard',
                #     'view_mode': 'form',
                # }

    def button_pending(self):
        record = super(MrpOrderInh, self).button_pending()
        # if not self.production_id.product_id.is_process_b:
        return {
            'type': 'ir.actions.act_window',
            'name': 'Produced Quantity',
            'view_id': self.env.ref('pipe_overall.view_produced_wizard_form', False).id,
            'target': 'new',
            'res_model': 'produced.qty.wizard',
            'view_mode': 'form',
        }
        # else:
        #     return {
        #         'type': 'ir.actions.act_window',
        #         'name': 'Done Lot',
        #         'view_id': self.env.ref('production_overall.view_done_lot_wizard_form', False).id,
        #         'target': 'new',
        #         'res_model': 'done.lot.wizard',
        #         'view_mode': 'form',
        #     }


class EntryLine(models.Model):
    _name = 'entry.line'

    mrp_id = fields.Many2one('mrp.production')
    # workcenter_id = fields.Many2one('mrp.workcenter')

    mn_power = fields.Float('Man Power')
    machine_cost = fields.Float('Machine')
    oh_cost = fields.Float('OH')
    total_cost = fields.Float('Total')

