from app.main.util.views.admin_view import AdminView
from flask_login import current_user
from flask import url_for, redirect


class BasicView(AdminView):

    def __init__(self, *args, **kwargs):
        super(BasicView, self).__init__(*args, **kwargs)

    create_modal = True
    edit_modal = True

    def is_accessible(self):
        try:
            return current_user.is_authenticated_admin()
        except:
            return False
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_me'))
