from soda_ledger import *


@all_renderable(c.SODA, c.SODA_ADMIN)
class Root:
    def index(self, session, message='', **params):
        user = session.user(c.CURRENT_ADMIN['id'])
        cart = user.current_cart
        if not cart:
            cart = session.cart({'user_id': user.id}, ignore_csrf=True)
            session.add(cart)
            session.commit()

        return {
            'message': message,
            'items': session.query(Soda).filter(Soda.current_quantity > 0).all(),
            'cart': cart
        }

    def confirm(self, session, message='', **params):
        user = session.user(c.CURRENT_ADMIN['id'])
        cart = user.current_cart
        if not cart or cart.total_items == 0:
            message = 'No Items To Purchase'
            raise HTTPRedirect("index?message={}".format(message))
        message = cart.commit_transaction()
        session.commit()
        return {
            'message': message,
            'cart': cart,
            'user': user
        }

    @ajax
    def confirm_items(self, session, message='', **params):
        user = session.user(c.CURRENT_ADMIN['id'])
        cart = user.current_cart
        prior_balance = user.balance
        if not cart or cart.total_items == 0:
            message = 'No Items To Purchase'
            raise HTTPRedirect("index?message={}".format(message))
        message = cart.commit_transaction()
        session.commit()
        code = render('/partials/confirm_items.html', {'items': cart, 'balance': prior_balance}).decode('utf-8')
        return {
            'status': True,
            'message': message,
            'code': code
        }



    @ajax
    def update_cart(self, session, message='', **params):
        user = session.user(c.CURRENT_ADMIN['id'])
        cart = user.current_cart
        code = ''
        is_new = False
        if not cart:
            return {
                'status': False,
                'message': 'No cart present.'
            }
        if 'quantity' in params and 'id' in params:
            cart_item = session.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.soda_id == params['id']).first()
            if not cart_item:
                cart_item = session.cart_item({
                    'soda_id': params['id'],
                    'cart_id': cart.id
                })
            if int(params['quantity']) <= 0:
                session.delete(cart_item)
                message = 'Item deleted from cart'
            else:
                added_message = 'Item already in cart.' if cart_item.quantity == int(params['quantity']) else 'Item quantity updated.'
                cart_item.quantity = params['quantity']
                is_new = cart_item.is_new
                session.add(cart_item)

                message = 'Item added to cart' if is_new else added_message
            session.commit()
            code = render('/partials/cart_item.html', {'item': cart_item}).decode('utf-8') if is_new else ''
        return {
            'status': True,
            'message': message,
            'code': code
        }

    @ajax
    def empty_cart(self, session, **params):
        user = session.user(c.CURRENT_ADMIN['id'])
        cart = user.current_cart
        if not cart:
            return {
                'status': False,
                'message': 'No cart present.'
            }
        for i in cart.items:
            session.delete(i)
        session.commit()
        return {
            'status': True,
            'message': 'Cart Emptied'
        }

    @ajax
    def remove_item(self, session, **params):
        user = session.user(c.CURRENT_ADMIN['id'])
        cart = user.current_cart
        status = False
        message = 'No cart present.'
        if cart:
            if 'id' in params:
                cart_item = session.cart_item(params['id'])
                if cart_item:
                    session.delete(cart_item)
                    session.commit()
                    message = 'Item deleted.'
                    status = True
                else:
                    message = 'No matching item found.'

            else:
                message = 'No item id given.'
        return {
            'status': status,
            'message': message
        }

    @ajax_gettable
    def user_balance(self, session, message='', **params):
        user = session.user(c.CURRENT_ADMIN['id'])
        cart = user.current_cart
        status = False
        if not cart:
            message = 'No cart present.'
        r_b = user.balance - cart.total_cost
        if r_b >= 0:
            message = "${:,.2f}".format(r_b)
            status = True
        else:
            message = "Not enough funds"
        return {
            'status': status,
            'message': message
        }

    @ajax_gettable
    def cart_total(self, session, message='', **params):
        user = session.user(c.CURRENT_ADMIN['id'])
        cart = user.current_cart
        if not cart:
            return {
                'status': False,
                'message': 'No cart present.'
            }
        return {
            'status': True,
            'message':  "${:,.2f}".format(cart.total_cost)
        }

    @ajax_gettable
    def cart_total_items(self, session, message='', **params):
        user = session.user(c.CURRENT_ADMIN['id'])
        cart = user.current_cart
        if not cart:
            return {
                'status': False,
                'message': 'No cart present.'
            }
        return {
            'status': True,
            'message': cart.total_items
        }


    @ajax
    def checkout(self, session, message='', **params):
        user = session.user(c.CURRENT_ADMIN['id'])
        cart = user.current_cart
        if not cart:
            return {
                'status': False,
                'message': 'No cart present.'
            }
        return {
            'status': cart.commit_transaction(),
            'message': message
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

    def purchase(self, session, message='', **params):
        pass

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
