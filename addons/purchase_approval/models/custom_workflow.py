from odoo import api, fields, models

class CustomWorkflow(models.Model):
    _name = "custom.workflow"
    _description = "Custom workflow"

    name = fields.Char('Name', required=True, default='New')
    entity = fields.Char('Entity', required=True, index='trigram')
    step = fields.One2many('custom.workflow.step', 'workflow_id', string='Steps')

class CustomWorkflowStep(models.Model):
    _name = "custom.workflow.step"
    _description = "Custom workflow step"

    name = fields.Char('Name', required=True, default='New')
    sequence = fields.Integer(string='Sequence')
    user_ids = fields.Many2many('res.users', string='Users')
    manager_approval = fields.Boolean(string='Manager Approval', default = False)
    workflow_id = fields.Many2one('custom.workflow', string='Workflow', index=True, required=True, ondelete='cascade')

class CustomWorkflowApproval(models.Model):
    _name = "custom.workflow.approval"
    _description = "Custom workflow approval"
    
    order_id = fields.Many2one('purchase.order', string='Orden de compra', index=True, required=True, ondelete='cascade')
    step_id = fields.Many2one('custom.workflow.step', string='Workflow', index=True, required=True, ondelete='cascade')
    step_name = fields.Char(related='step_id.name', readonly=True)
    approved = fields.Boolean(string='Aprobada', default = False)
    completed = fields.Boolean(string='Finalizado', default = False)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    user_department = fields.Many2one(related='user_id.employee_id.department_id', readonly=True)
    department_manager = fields.Many2one(related='user_department.manager_id', readonly=True)
    workflow_approval = fields.One2many('custom.workflow.approval', 'order_id', string='Aprobaciones', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})

    @api.constrains('state')
    def _check_state(self):
        if self.state == 'to approve':
            workflows = self.env['custom.workflow'].search([('entity', '=', 'purchase.order')])

            if workflows[0]:
                # steps = self.env['custom.workflow.step'].search([('workflow_id', '=', workflow[0].id)])
                CustomWorkflowApproval = self.env['custom.workflow.approval']

                for step in workflows[0].step:
                    CustomWorkflowApproval.create({
                        'order_id': self.id,
                        'step_id': step.id
                    })