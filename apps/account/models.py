import uuid
from django.db import models
from apps.account.validators import validate_username
from apps.account.manager import UserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.password_validation import validate_password

# class UppercaseUUIDField(models.UUIDField):
#     def get_db_prep_value(self, value, connection, prepared=False):
#         if not prepared:
#             return str(uuid.UUID(str(value))).upper()
#         return value
    
# Create your models here.
class User(AbstractUser):
    username_validator = validate_username
    password_validator = validate_password

    id              = models.UUIDField(_("id"), primary_key=True, default=uuid.uuid4, editable=False)
    first_name      = models.CharField(_('First Name'), max_length=150)
    last_name       = models.CharField(_('Last Name'), max_length=150)
    phone_number    = PhoneNumberField(_("Phone number"), help_text=_("User's phone number "), unique=True)
    username        = models.CharField(
                        _('Username'),
                        max_length=150,
                        unique=True,
                        help_text='Required. 150 characters or fewer. Letters, digits and _ only.',
                        validators=[username_validator],
                        error_messages={
                            'unique': "A user with that username already exists.",
                        },
                    )
    email           = models.EmailField(_('Email'), unique=True)
    password        = models.CharField(_('Password'), max_length=254, validators=[password_validator])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'phone_number',
        'first_name',
        'last_name',
        ]

    objects = UserManager()

    def __str__(self):
        return str(self.email)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip().title()
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class Income(models.Model):
    id              = models.UUIDField(_("id"), primary_key=True, default=uuid.uuid4, editable=False)
    nameOfRevenue   = models.CharField(_("Name of Revenue"), max_length=100)
    amount          = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at      = models.DateTimeField(auto_now=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.amount}"
    
    class Meta:
        verbose_name = _('Income')
        verbose_name_plural = _('Incomes')

class Expenditure(models.Model):
    id              = models.UUIDField(_("id"), primary_key=True, default=uuid.uuid4, editable=False)
    category        = models.CharField(_("Category"), max_length=100)
    nameOfItem      = models.CharField(_("Name of Item"), max_length=100)
    estimatedAmount = models.DecimalField(_("Estimated Amount"), max_digits=10, decimal_places=2)
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at      = models.DateTimeField(auto_now=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.estimatedAmount}"
    
    class Meta:
        verbose_name = _('Expenditure')
        verbose_name_plural = _('Expenditures')
