from soda_ledger import *


@all_renderable(c.SODA, c.SODA_ADMIN)
class Root:
    def index(self, session, message=''):

        return {
            'message': message,
            'items': session.query(Soda).filter(Soda.current_quantity > 0).all()
        }

    def history(self, id=None, session=None, message=''):
        soda = session.soda(id) if id else None
        if not soda:
            message = 'No Soda Found.' if id else 'No Soda ID provided.'
        return {
            'message': message,
            'item': soda,
            'items': session.query(Soda).all()
        }

    def manage(self, session):
        return ''
