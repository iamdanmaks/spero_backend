from .basic_admin_view import BasicView


class UserView(BasicView):
    
    def __init__(self, *args, **kwargs):
        super(BasicView, self).__init__(*args, **kwargs)
    
    column_list = (
        'id', 
        'email', 
        'username', 
        'first_name', 
        'second_name', 
        'registered_on', 
        'date_of_birth',
        'admin', 
        'active',
        'subscriber', 
        'data_access',
        'height',
        'weight', 
        'public_id',
        'stripe_id'
    )
    column_searchable_list = ('username', 'email', 'public_id', 'id', )
    column_default_sort = ('registered_on', True)
    column_filters = ('admin',)
    can_create = False
