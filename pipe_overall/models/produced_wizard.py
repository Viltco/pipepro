from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


# class FinishLotWizard(models.TransientModel):
#     _name = 'finish.lot.wizard'
#
#     qty = fields.Float('Quantity', default=1)
#     status = fields.Selection([
#         ('processed', 'Processed'),
#         ('rejected', 'Rejected'),
#     ], string='Status', default='', ondelete='cascade')
#     reason = fields.Selection([
#         ('wrong', 'Wrong Cutting'),
#         ('burn', 'Burn'),
#         ('hole', 'Hole'),
#         ('shortage', 'Shortage of material during welding'),
#         ('excess', 'Excess of material during welding'),
#     ], string='Reason', default='', ondelete='cascade')
#
#     def action_create(self):
#         model = self.env.context.get('active_model')
#         rec_model = self.env[model].browse(self.env.context.get('active_id'))
#         lot = self.env['unique.lot'].search([('name', '=', rec_model.lot), ('mrp_id', '=', rec_model.production_id.id)])
#         lot.status = self.status
#         if self.status == 'rejected':
#             reject = self.env['reason.line'].create({
#                 'mrp_id': rec_model.production_id.id,
#                 'name': rec_model.name,
#                 'workcenter_id': rec_model.workcenter_id.id,
#                 'workcenter_machine_id': rec_model.workcenter_machine_id.id,
#                 'employee_id': rec_model.employee_id.id,
#                 'qty': self.qty,
#                 'reason': self.reason,
#                 'paused_date': datetime.today(),
#                 'start_date': rec_model.start_date_custom,
#             })
#         else:
#             rec = self.env['produced.qty.line'].create({
#                 'mrp_id': rec_model.production_id.id,
#                 'name': rec_model.name,
#                 'workcenter_id': rec_model.workcenter_id.id,
#                 'workcenter_machine_id': rec_model.workcenter_machine_id.id,
#                 'employee_id': rec_model.employee_id.id,
#                 'qty': self.qty,
#                 'paused_date': datetime.today(),
#                 'start_date': rec_model.start_date_custom,
#             })
#         record = self.button_finish(rec_model)
#
#     def button_finish(self, order):
#         end_date = datetime.now()
#         for workorder in order:
#             if workorder.state in ('done', 'cancel'):
#                 continue
#             workorder.end_all()
#             vals = {
#                 'state': 'done',
#                 'date_finished': end_date,
#                 'date_planned_finished': end_date
#             }
#             if not workorder.date_start:
#                 vals['date_start'] = end_date
#             if not workorder.date_planned_start or end_date < workorder.date_planned_start:
#                 vals['date_planned_start'] = end_date
#             workorder.write(vals)
#
#             workorder._start_nextworkorder()
#         return True
#
#
# class DoneLotWizard(models.TransientModel):
#     _name = 'done.lot.wizard'
#
#     qty = fields.Float('Quantity', default=1)
#     status = fields.Selection([
#         ('processed', 'Processed'),
#         ('rejected', 'Rejected'),
#     ], string='Status', default='', ondelete='cascade')
#     reason = fields.Selection([
#         ('wrong', 'Wrong Cutting'),
#         ('burn', 'Burn'),
#         ('hole', 'Hole'),
#         ('shortage', 'Shortage of material during welding'),
#         ('excess', 'Excess of material during welding'),
#     ], string='Reason', default='', ondelete='cascade')
#
#     def action_create(self):
#         model = self.env.context.get('active_model')
#         rec_model = self.env[model].browse(self.env.context.get('active_id'))
#         lot = self.env['unique.lot'].search([('name', '=', rec_model.lot), ('mrp_id', '=', rec_model.production_id.id)])
#         lot.status = self.status
#         if self.status == 'rejected':
#             reject = self.env['reason.line'].create({
#                 'mrp_id': rec_model.production_id.id,
#                 'name': rec_model.name,
#                 'workcenter_id': rec_model.workcenter_id.id,
#                 'workcenter_machine_id': rec_model.workcenter_machine_id.id,
#                 'employee_id': rec_model.employee_id.id,
#                 'qty': self.qty,
#                 'reason': self.reason,
#                 'paused_date': datetime.today(),
#                 'start_date': rec_model.start_date_custom,
#             })
#         else:
#             rec = self.env['produced.qty.line'].create({
#                 'mrp_id': rec_model.production_id.id,
#                 'name': rec_model.name,
#                 'workcenter_id': rec_model.workcenter_id.id,
#                 'workcenter_machine_id': rec_model.workcenter_machine_id.id,
#                 'employee_id': rec_model.employee_id.id,
#                 'qty': self.qty,
#                 'paused_date': datetime.today(),
#                 'start_date': rec_model.start_date_custom,
#             })
#
#
# class ProductLotWizard(models.TransientModel):
#     _name = 'produced.lot.wizard'
#
#     # unique_lot_id = fields.Many2one('unique.lot')
#     production_id = fields.Many2one('mrp.production')
#     # unique_lot_ids = fields.Many2many('unique.lot')
#
#     def action_create(self):
#         model = self.env.context.get('active_model')
#         rec_model = self.env[model].browse(self.env.context.get('active_id'))
#         # rec_model.lot = self.unique_lot_id.name
#         lot_list = []
#         for rec in rec_model.unique_lots:
#             lot_list.append(rec.id)
#         # lot_list.append(self.unique_lot_id.id)
#         # rec_model.unique_lots = lot_list
#         rec_model.start_date_custom = datetime.today()
#         return self.button_starts(rec_model)
#
#     def button_starts(self, order):
#         order.ensure_one()
#         # As button_start is automatically called in the new view
#         if order.state in ('done', 'cancel'):
#             return True
#
#         if order.product_tracking == 'serial':
#             order.qty_producing = 1.0
#
#         self.env['mrp.workcenter.productivity'].create(
#             order._prepare_timeline_vals(order.duration, datetime.now())
#         )
#         if order.production_id.state != 'progress':
#             order.production_id.write({
#                 'date_start': datetime.now(),
#             })
#         if order.state == 'progress':
#             return True
#         start_date = datetime.now()
#         vals = {
#             'state': 'progress',
#             'date_start': start_date,
#         }
#         if not order.leave_id:
#             leave = self.env['resource.calendar.leaves'].create({
#                 'name': order.display_name,
#                 'calendar_id': order.workcenter_id.resource_calendar_id.id,
#                 'date_from': start_date,
#                 'date_to': start_date + relativedelta(minutes=order.duration_expected),
#                 'resource_id': order.workcenter_id.resource_id.id,
#                 'time_type': 'other'
#             })
#             vals['leave_id'] = leave.id
#             return order.write(vals)
#         else:
#             if order.date_planned_start > start_date:
#                 vals['date_planned_start'] = start_date
#             if order.date_planned_finished and order.date_planned_finished < start_date:
#                 vals['date_planned_finished'] = start_date
#             return order.write(vals)


class ProductQuantityWizard(models.TransientModel):
    _name = 'produced.qty.wizard'

    qty = fields.Float('Produced Quantity')

    def action_create(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        workorder = self.env['mrp.workorder'].browse([rec_model.id])
        # if self.qty > production.production_id.qty_producing:
        #     raise ValidationError('Produced Quantity can not be greater than Quantity to Produce')
        pre_order = self.env['mrp.workorder'].search(
            [('id', '=', workorder.id - 1), ('production_id', '=', workorder.production_id.id)])
        # ///////////////////////////////////
        current_qty = sum(self.env['produced.qty.line'].search(
            [('mrp_id', '=', workorder.production_id.id), ('workcenter_id', '=', workorder.workcenter_id.id),
             ]).mapped('qty'))
        pre_qty = 0
        if pre_order:
            pre_qty = sum(self.env['produced.qty.line'].search(
                [('mrp_id', '=', pre_order.production_id.id), ('workcenter_id', '=', pre_order.workcenter_id.id),
                 ]).mapped('qty'))

            if self.qty > pre_qty-current_qty:
                raise ValidationError('Produced Quantity can not be greater than Quantity to Produce!!!!!!')
            # ////////////////////////////////////////

        qty_producing = 0
        if pre_order:
            for pre in pre_order.production_id.produced_lines:
                if pre.name == pre_order.name and pre.workcenter_id.id == pre_order.workcenter_id.id:
                    # print(pre.qty)
                    qty_producing = qty_producing + pre.qty
        else:
            qty_producing = workorder.production_id.qty_producing
        if self.qty > qty_producing:
            raise ValidationError('Produced Quantity can not be greater than Quantity to Produce')

        qty = 0
        for line in workorder.production_id.produced_lines:
            if line.name == workorder.name and line.workcenter_id.id == workorder.workcenter_id.id:
                qty = qty + line.qty
        if self.qty > (qty_producing - qty):
            raise ValidationError('You are trying to produce more quantity than initial demand.')

        rec = self.env['produced.qty.line'].create({
            'mrp_id': workorder.production_id.id,
            'name': rec_model.name,
            'workcenter_id': rec_model.workcenter_id.id,
            # 'employee_id': rec_model.employee_id.id,
            'qty': self.qty,
            'paused_date': datetime.today(),
            'start_date': rec_model.start_date_custom,
        })


class QuantityDoneWizard(models.TransientModel):
    _name = 'done.qty.wizard'

    qty = fields.Float('Produced Quantity')
    # reason = fields.Char('Reason')
    reason = fields.Selection([
        ('wrong', 'Wrong Cutting'),
        ('burn', 'Burn'),
        ('hole', 'Hole'),
        ('shortage', 'Shortage of material during welding'),
        ('excess', 'Excess of material during welding'),
    ], string='Reason', default='', ondelete='cascade')

    def action_create(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        workorder = self.env['mrp.workorder'].browse([rec_model.id])
        pre_order = self.env['mrp.workorder'].search(
            [('id', '=', workorder.id - 1), ('production_id', '=', workorder.production_id.id)])

        # ///////////////////////////////////
        current_qty = sum(self.env['produced.qty.line'].search(
            [('mrp_id', '=', workorder.production_id.id), ('workcenter_id', '=', workorder.workcenter_id.id)]).mapped('qty'))
        pre_qty = 0
        if pre_order:
            pre_qty = sum(self.env['produced.qty.line'].search(
                [('mrp_id', '=', pre_order.production_id.id), ('workcenter_id', '=', pre_order.workcenter_id.id)]).mapped('qty'))

            if self.qty > pre_qty - current_qty:
                raise ValidationError('Produced Quantity can not be greater than Quantity to Produce!!!!!!')
        # ////////////////////////////////////////

        qty_producing = 0
        if pre_order:
            for pre in pre_order.production_id.produced_lines:
                if pre.name == pre_order.name and pre.workcenter_id.id == pre_order.workcenter_id.id:
                    qty_producing = qty_producing + pre.qty
        else:
            qty_producing = workorder.production_id.qty_producing
        if self.qty > qty_producing:
            raise ValidationError('Produced Quantity can not be greater than Quantity to Produce')
        qty = 0
        for line in workorder.production_id.produced_lines:
            if line.name == workorder.name and line.workcenter_id.id == workorder.workcenter_id.id:
                qty = qty + line.qty
        if self.qty > (qty_producing - qty):
            raise ValidationError('You are trying to produce more quantity than initial demand.')
        if self.qty + qty < qty_producing:
            if not self.reason:
                raise UserError('Please add reason of rejection.')
            reject = self.env['reason.line'].create({
                'mrp_id': workorder.production_id.id,
                'name': workorder.name,
                'workcenter_id': workorder.workcenter_id.id,
                # 'qty': workorder.production_id.qty_producing - qty,
                'qty': qty_producing - (self.qty + qty),
                'reason': self.reason,
                'paused_date': datetime.today(),
                'start_date': workorder.start_date_custom,
            })
        if self.qty > 0:
            res = self.env['produced.qty.line'].create({
                'mrp_id': workorder.production_id.id,
                'name': workorder.name,
                'workcenter_id': workorder.workcenter_id.id,
                # 'qty': workorder.production_id.qty_producing - qty,
                'qty': self.qty,
                'paused_date': datetime.today(),
                'start_date': workorder.start_date_custom,
            })
        work_list = []
        for w_line in workorder.production_id.workorder_ids:
            work_list.append(w_line.id)
        p_qty = 0
        if work_list:
            if work_list[-1] == workorder.id:
                for p_line in workorder.production_id.produced_lines:
                    if p_line.name == workorder.name and p_line.workcenter_id.id == workorder.workcenter_id.id:
                        p_qty = p_qty + p_line.qty
                workorder.production_id.qty_producing = p_qty
        record = self.button_finish(workorder)

    def button_finish(self, order):
        end_date = datetime.now()
        for workorder in order:
            if workorder.state in ('done', 'cancel'):
                continue
            workorder.end_all()
            vals = {
                'state': 'done',
                'date_finished': end_date,
                'date_planned_finished': end_date
            }
            if not workorder.date_start:
                vals['date_start'] = end_date
            if not workorder.date_planned_start or end_date < workorder.date_planned_start:
                vals['date_planned_start'] = end_date
            workorder.write(vals)
            workorder._start_nextworkorder()
        return True
