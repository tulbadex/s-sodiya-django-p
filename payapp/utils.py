def get_currency_symbol(user):
    if user.currency == 'GBP':
        return '£'
    elif user.currency == 'USD':
        return '$'
    elif user.currency == 'EUR':
        return '€'
    else:
        return ''  # Return empty string if currency is not recognized
