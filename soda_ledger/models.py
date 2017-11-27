from soda_ledger import *


class Soda(MainModel):
    lifetime_quantity = Column(Integer, default=0)
    current_quantity = Column(Integer, default=0)
    price = Column(Float, default=0.75)
    sale_price = Column(Float, default=0.75)
    lowest_sale_price = Column(Float, default=0.75)
    name = Column(UnicodeText, unique=True)
    purchase_history = relationship('Purchase', backref='soda')
    on_sale = Column(Boolean, default=False)

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
    purchases = relationship('Purchase', backref='student')


class Purchase(MainModel):
    time = Column(UTCDateTime, default=datetime.now(UTC))
    soda_id = Column(UUID, ForeignKey('soda.id'), nullable=True, index=True)
    was_on_sale = Column(Boolean, default=False)
    price = Column(Float, default=0)
    user_id = Column(UUID, ForeignKey('user.id'), nullable=True, index=True)

    @presave_adjustment
    def _misc_adjustments(self):
        the_soda = self.session.soda(self.soda_id)
        if the_soda.on_sale:
            self.was_on_sale = True
        self.price = the_soda.current_price
