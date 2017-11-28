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

    @unrestricted
    def signup(self, session,  password='', message='', **params):
        user = session.user(params, checkgroups=User.all_checkgroups, bools=User.all_bools)
        if user.is_new:
            message = check(user)
            if not message and 'first_name' in params:
                session.add(user)
                session.commit()
                password = password if password else genpasswd()
                admin_params = {
                    'access': '{}'.format(c.SODA),
                    'user_id': user.id,
                    'password': password
                }
                account = session.admin_account(admin_params, checkgroups=['access'])
                account.hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                message = check(account)
                if not message:
                    message = 'Account Created'
                    account.user = user
                    session.add(account)
                raise HTTPRedirect('index?message={}', message)
            return {
                'user': user
            }
        raise HTTPRedirect('index?message={}', message)
