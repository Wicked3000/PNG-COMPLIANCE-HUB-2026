try:
    import webauthn
    print("Main webauthn import OK")
    from webauthn.helpers.structs import (
        AuthenticatorSelectionCriteria,
        UserVerificationRequirement,
        AuthenticatorAttachment,
        RegistrationSelectionCriteria,
    )
    print("Structs import OK")
    from webauthn.helpers import options_to_json, verify_registration_response, verify_authentication_response
    print("Helpers import OK")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Other Error: {e}")
