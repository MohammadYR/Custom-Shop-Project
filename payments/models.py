from django.db import models
from core.models import BaseModel
from sales.models import Order


class Payment(BaseModel):
    """
    Represents a payment for an order.

    Attributes:
        STATUS (tuple): possible statuses of a payment
        order (Order): the order that this payment is for
        amount (DecimalField): the amount of the payment
        provider (CharField): the provider of the payment
        authority (CharField): the tracking code of the payment
        status (CharField): the status of the payment
        paid_at (DateTimeField): the datetime when the payment was made
    """
    STATUS = [("INITIATED","Initiated"),("CALLBACK_OK","Callback Ok"),("VERIFIED","Verified"),("FAILED","Failed")]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider = models.CharField(max_length=30)
    authority = models.CharField(max_length=80, blank=True) # tracking code
    status = models.CharField(max_length=15, choices=STATUS, default="INITIATED")
    paid_at = models.DateTimeField(null=True, blank=True)


class Transaction(BaseModel):
    """
    Represents a transaction for a payment.

    Attributes:
        payment (Payment): the payment that this transaction is for
        ref_id (CharField): the reference id of the transaction (if applicable)
        raw_payload (JSONField): the raw payload of the transaction
        status (CharField): the status of the transaction

    Notes:
        status is one of the following values:
            - INITIATED: the transaction has been initialized
            - CALLBACK_OK: the transaction has been successfully processed
            - VERIFIED: the transaction has been successfully verified
            - FAILED: the transaction has failed
    """
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="transactions")
    ref_id = models.CharField(max_length=100, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default="INITIATED")
