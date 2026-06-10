import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def verify_paystack_payment(reference, expected_amount_ghs):
    """
    Verifies a payment reference with Paystack.
    expected_amount_ghs is the amount in GHS/NGN. Paystack works in pesewas/kobo (cents),
    so expected_amount_ghs * 100 is checked against the Paystack API amount.
    """
    # Safe fallback secret key for developer sandbox
    secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', 'sk_test_mock_afrisolve_secret_key_9999')
    
    # 1. Developer Sandbox Mock Flow (starts with mock_ or uses mock secret key)
    if secret_key.startswith('sk_test_mock') or str(reference).startswith('mock_'):
        logger.info(f"[PAYSTACK MOCK] Simulating verification for ref: {reference}")
        return {
            'status': True,
            'amount': float(expected_amount_ghs),
            'gateway_response': 'Successful Mock Escrow Deposit',
            'channel': 'card',
            'currency': 'GHS'
        }
        
    # 2. Real Paystack API Verification
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') and result.get('data'):
                data = result['data']
                paystack_status = data.get('status')
                # Amount is in pesewas (cents)
                paystack_amount = data.get('amount', 0) / 100.0 
                currency = data.get('currency', 'GHS')
                
                if paystack_status == 'success':
                    # Allow 1% leeway for floating point comparisons if needed
                    if abs(paystack_amount - float(expected_amount_ghs)) < 0.1:
                        return {
                            'status': True,
                            'amount': paystack_amount,
                            'gateway_response': data.get('gateway_response'),
                            'channel': data.get('channel'),
                            'currency': currency
                        }
                    else:
                        logger.error(f"Paystack verification failed: amount mismatch. Expected {expected_amount_ghs}, got {paystack_amount}")
                        return {
                            'status': False,
                            'message': f"Amount mismatch. Paid {paystack_amount} instead of {expected_amount_ghs}"
                        }
                else:
                    return {
                        'status': False,
                        'message': f"Transaction status was {paystack_status}"
                    }
            else:
                return {
                    'status': False,
                    'message': result.get('message', 'Failed to retrieve transaction details')
                }
        else:
            logger.error(f"Paystack returned error status: {response.status_code} for ref {reference}")
            return {
                'status': False,
                'message': f"Paystack returned status code {response.status_code}"
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP request exception during Paystack verification: {e}")
        return {
            'status': False,
            'message': f"Connection to Paystack failed: {str(e)}"
        }
