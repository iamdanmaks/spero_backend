from .basic_admin_view import BasicView


class BlacklistView(BasicView):
    
    def __init__(self, *args, **kwargs):
        super(BasicView, self).__init__(*args, **kwargs)
    
    column_list = ('id', 'token', 'blacklisted_on')
    column_searchable_list = ('token', )
    column_default_sort = ('blacklisted_on', True)
