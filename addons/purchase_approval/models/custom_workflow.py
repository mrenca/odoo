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
    sign_required = fields.Boolean(string='Firma Requerida', default = False)
    workflow_id = fields.Many2one('custom.workflow', string='Workflow', index=True, required=True, ondelete='cascade')

class CustomWorkflowApproval(models.Model):
    _name = "custom.workflow.approval"
    _description = "Custom workflow approval"
    
    order_id = fields.Many2one('purchase.order', string='Orden de compra', index=True, required=True, ondelete='cascade')
    order_department_manager = fields.Many2one(related='order_id.department_manager', readonly=True)
    step_id = fields.Many2one('custom.workflow.step', string='Workflow', index=True, required=True, ondelete='cascade')
    step_name = fields.Char(related='step_id.name', readonly=True)
    user_ids = fields.Many2many(related='step_id.user_ids', readonly=True)
    can_approve = fields.Boolean(compute="_compute_can_approve")
    manager_approval = fields.Boolean(related='step_id.manager_approval', readonly=True)
    sign_required = fields.Boolean(related='step_id.sign_required', readonly=True)
    is_signed = fields.Boolean(string='Firmada', default = False)
    state = fields.Selection([
        ('new', 'Nueva'),
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada')
    ], string='Status', readonly=True, index=True, default='new', tracking=True)

    def _check_approval(self, approval, user_id):
        if approval.state == 'pending':
            user_ids = approval.user_ids.mapped('id')
            manager_ids = list(map(lambda x: x.user_id.id, approval.order_department_manager))

            if user_id in user_ids or (approval.manager_approval and user_id in manager_ids):
                return True

        return False

    @api.depends('order_id', 'step_id')
    def _compute_can_approve(self):
        for approval in self:
            approval.can_approve = self._check_approval(approval, self.env.user.id)

    def button_approve(self):
        if self._check_approval(self, self.env.user.id):
            self.write({'state': 'approved'})

            next_step = self.env['custom.workflow.step'].search(
                [('workflow_id', '=', self.step_id.workflow_id.id), ('sequence', '>', self.step_id.sequence)],
                limit = 1,
                order = 'sequence ASC'
            )

            if next_step:
                next_approval = self.env['custom.workflow.approval'].search(
                    [('order_id', '=', self.order_id.id), ('step_id', '=', next_step.id)],
                    limit = 1,
                )
                next_approval.write({'state': 'pending'})

                # Notificar como actividad
                from datetime import date
                user_ids = next_approval.user_ids.mapped('id')
                todos = []

                for user_id in user_ids:
                    todos.append({
                        'res_id': self.order_id.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')]).id,
                        'user_id': user_id,
                        'summary': 'Solicitud de aprobación de compra',
                        'note': '',
                        'activity_type_id': 4,
                        'date_deadline': date.today(),
                    })

                self.env['mail.activity'].create(todos)

        return {}

    def button_reject(self):
        self.write({'state': 'rejected'})
        return {}

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    user_department = fields.Many2one(related='user_id.employee_id.department_id', readonly=True)
    department_manager = fields.Many2one(related='user_department.manager_id', readonly=True)
    workflow_approval = fields.One2many('custom.workflow.approval', 'order_id', string='Aprobaciones', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True, ondelete='set null')

    @api.constrains('state')
    def _check_state(self):
        workflows = self.env['custom.workflow'].search([('entity', '=', 'purchase.order')])
        CustomWorkflowApproval = self.env['custom.workflow.approval']

        # Si tiene un flujo asociado al modelo
        if workflows[0]:
            if self.state == 'to approve':
                for i, step in enumerate(workflows[0].step):
                    if not CustomWorkflowApproval.search([('order_id', '=', self.id), ('step_id', '=', step.id)]).exists():
                        CustomWorkflowApproval.create({
                            'order_id': self.id,
                            'step_id': step.id,
                            'state': 'pending' if i == 0 else 'new'
                        })
            elif self.state == 'purchase':
                try:
                    from datetime import datetime, timedelta
                    import pytz
                    import requests
                    import hashlib
                    import jwt
                    import base64

                    sclTz = pytz.timezone("America/Santiago")
                    now = datetime.now(sclTz)
                    now_plus_10 = now + timedelta(minutes=10)
                    pdf = self.env['ir.actions.report']._render_qweb_pdf('purchase.action_report_purchase_order', res_ids=[self.id])
                    b64_pdf = base64.b64encode(pdf[0])

                    for i, step in enumerate(workflows[0].step):
                        # Solo tenemos un usuario de pruebas
                        if step.sign_required:
                            step_approval = CustomWorkflowApproval.search([('order_id', '=', self.id), ('step_id', '=', step.id)])

                            # Obtener la firmagob
                            token_data = {
                                "entity": "Subsecretaría General de la Presidencia",
                                "run": "22222222",
                                "expiration": now_plus_10.strftime('%Y-%m-%dT%H:%M:%S'),
                                "purpose": "Desatendido"
                            }
                            secret = "27a216342c744f89b7b82fa290519ba0"

                            data = {
                                "api_token_key": "sandbox",
                                "token": jwt.encode(token_data, secret, algorithm='HS256').decode('utf-8'),
                                "files": [
                                    {
                                        "content-type": "application/pdf",
                                        "content": b64_pdf.decode('utf-8'),
                                        "description": "PO00018",
                                        "checksum": hashlib.sha256(str(b64_pdf).encode('utf-8')).hexdigest()
                                    }
                                ]
                            }

                            r = requests.post("https://api.firma.cert.digital.gob.cl/firma/v2/files/tickets", json=data)

                            if r.status_code == 200:
                                data = r.json()

                                if 'files' in data.keys():
                                    signature = data['files'][0]

                                    if signature['status'] == "OK":
                                        step_approval.write({'is_signed': True})
                                        b64_pdf = signature['content']

                    # Guarda el resultado como adjunto a la orden
                    self.env['ir.attachment'].create({
                        'name': self.name,
                        'type': 'binary',
                        'datas': b64_pdf,
                        'store_fname': self.name,
                        'res_model': 'purchase.order',
                        'res_id': self.id,
                        'mimetype': 'application/pdf'
                    })
                except Exception as error:
                    print(error)

# TODO: Purchase order line hereda analytic acount de Purchase Order


class User(models.Model):
    _inherit = ['res.users']

    digital_sign = fields.Binary(string='Firma')