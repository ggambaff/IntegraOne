# -*- coding: utf-8 -*-

import integraone
from integraone import fields, models, modules


class Module(models.BaseModel):
    _model_name = 'base_module_list'


    name = fields.CharField(
        description="fff",
        null=False,

    )

