from base import BaseService


class PaymentService(BaseService):

    def process_payment(self):
        validate_payment()
        return True


def validate_payment():
    return True
