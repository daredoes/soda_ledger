from soda_ledger import *


class Soda(MainModel):
    lifetime_quantity = Column(Integer, default=0)
    current_quantity = Column(Integer, default=0)
    price = Column(Float, default=0.75)
    sale_price = Column(Float, default=0.75)
    lowest_sale_price = Column(Float, default=0.75)
    name = Column(UnicodeText, unique=True)
    purchase_history = relationship('CartItem', backref='soda')
    on_sale = Column(Boolean, default=False)

    def take(self, amount):
        if amount > 0 and self.current_quantity - amount >= 0:
            self.current_quantity -= amount
            return ''
        return "Not enough available."

    def is_available(self):
        if self.available_quantity > 0:
            return True

    @property
    def available_quantity(self):
        a_q = self.current_quantity
        for item in self.purchase_history:
            a_q -= 0 if item.completed else item.quantity
        return a_q

    @property
    def current_price(self):
        return self.sale_price if self.on_sale else self.price

    @presave_adjustment
    def _misc_adjustments(self):
        old_quantity = int(self.orig_value_of('current_quantity'))
        if old_quantity < self.current_quantity:
            self.lifetime_quantity += self.current_quantity - old_quantity
        self.lifetime_quantity = self.orig_value_of('lifetime_quantity') if self.lifetime_quantity < self.orig_value_of('lifetime_quantity') else self.lifetime_quantity
        if bool(self.orig_value_of('on_sale')) == False and self.on_sale == True:
            if self.sale_price < self.lowest_sale_price:
                self.lowest_sale_price = self.sale_price


@Session.model_mixin
class User:
    balance = Column(Float, default=0)
    total_withdrawn = Column(Float, default=0)
    total_deposited = Column(Float, default=0)
    minimum_balance = Column(Float, default=0)
    purchases = relationship('Cart', backref='user')

    def purchase(self, item):
        if self.balance - item.price >= self.minimum_balance:
            attempt_transaction = item.commit_transaction()
            if not attempt_transaction:
                self.balance -= item.price
                return ''
            return attempt_transaction
        return "Not Enough Funds"

    @property
    def current_cart(self):
        for p in self.purchases:
            if not p.checkout_time:
                return p


class CartItem(MainModel):
    soda_id = Column(UUID, ForeignKey('soda.id'))
    quantity = Column(Integer, default=1, nullable=False)
    cart_id = Column(UUID, ForeignKey('cart.id'), nullable=True)

    @property
    def price(self):
        return self.soda.current_price * self.quantity

    @property
    def completed(self):
        return True if self.cart.checkout_time else False

    def commit_transaction(self):
        return self.soda.take(self.quantity)


class Cart(MainModel):
    checkout_time = Column(UTCDateTime, default=None, nullable=True)
    user_id = Column(UUID, ForeignKey('user.id'))
    items = relationship('CartItem', backref='cart')

    def commit_transaction(self):
        for i in self.items:
            attempted_transaction = self.user.purchase(i)
            if attempted_transaction:
                with Session() as session:
                    session.rollback()
                return attempted_transaction
        self.checkout_time = datetime.now(UTC)
        return 'Purchase Successful!'

    @property
    def total_cost(self):
        cost = 0
        for item in self.items:
            cost += item.price
        return cost

    @property
    def total_items(self):
        count = 0
        for item in self.items:
            count += item.quantity
        return count
