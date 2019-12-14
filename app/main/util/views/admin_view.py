from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, url_for, request
from flask_admin.model import typefmt
from datetime import datetime

class AdminView(ModelView):

    def __init__(self, *args, **kwargs):
        super(AdminView, self).__init__(*args, **kwargs)
        self.static_folder = 'static'

        self.column_formatters = dict(typefmt.BASE_FORMATTERS)
        self.column_formatters.update({
                type(None): typefmt.null_formatter,
                datetime: self.date_format
            })

        self.column_type_formatters = self.column_formatters

    def date_format(self, view, value):
          return value.strftime('%d.%m.%Y %H:%M:%S')
