from soda_ledger import *


@all_renderable(c.SODA_ADMIN)
class Root:
    def index(self, session, message=''):
        return {
            'message': message
        }

    def users(self, session, message='', **params):
        user = session.user(params)
        if 'name' in params:
            session.add(user)
            session.commit()
        return {
            'message': message,
            'item': user,
            'items': session.query(User).all()
        }

    def add_soda(self, session, message='', new_entry=None, **params):
        soda = session.soda(params)
        if 'name' in params:
            session.add(soda)
            session.commit()
        return {
            'message': message,
            'item': soda,
            'new_entry': new_entry,
            'items': session.query(Soda).all()
        }

