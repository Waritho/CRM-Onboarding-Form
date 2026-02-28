def validate_razorpay(data: dict):
    required = [
        "razorpay_api_key",
        "key_name",
        "partner",
        "x_razorpay_account",
        "verify_url",
        "auth_key",
        "razorpay_secret",
        "order_url"
    ]
    for field in required:
        if field not in data:
            return False
    return True


def validate_easy_buzz(data: dict):
    required = [
        "merchant_key",
        "merchant_salt",
        "base_url",
        "environment",
        "retrieve_url"
    ]
    return all(field in data for field in required)


def validate_ezypay(data: dict):
    required = [
        "merchant_id",
        "encryption_key",
        "base_url",
        "verify_url"
    ]
    return all(field in data for field in required)


def validate_hdfc(data: dict):
    required = [
        "merchant_id",
        "customer_id",
        "key",
        "base_url",
        "environment",
        "retrieve_url"
    ]
    return all(field in data for field in required)


def validate_payu(data: dict):
    required = [
        "retrieve_url",
        "merchant_key",
        "merchant_salt"
    ]
    return all(field in data for field in required)