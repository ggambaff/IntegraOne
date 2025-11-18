# -*- coding: utf-8 -*-

import integraone
from integraone import fields, models, modules


class SystemUser(models.BaseModel):
    _model_name = 'system_users'


    active = fields.BooleanField(
        default=True,
    )