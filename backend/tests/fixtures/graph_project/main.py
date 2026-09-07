from payment import PaymentService
from repository import PaymentRepository


def main():
    service = PaymentService()
    repository = PaymentRepository()

    service.process_payment()
    repository.save()
