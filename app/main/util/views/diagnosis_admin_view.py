from .basic_admin_view import BasicView


class DiagnosisView(BasicView):
    
    def __init__(self, *args, **kwargs):
        super(BasicView, self).__init__(*args, **kwargs)
    
    column_list = ('id', 'result', 'checked_on', 'public_id')
    column_searchable_list = ('result', 'public_id', 'checked_on', )
    column_default_sort = ('checked_on', True)
    column_filters = ('result',)
    can_edit = False
    can_delete = False
    can_create = False
