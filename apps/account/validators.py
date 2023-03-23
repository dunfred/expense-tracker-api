from django.core.exceptions import ValidationError

def validate_username(value):
    # Check if username contains spaces
    if ' ' in value:
        raise ValidationError("Username must be separated by underscores instead of spaces.")

    # Check if username is not lowercase
    if value.lower() != value:
        raise ValidationError("Username must be in lowercase letters.")
