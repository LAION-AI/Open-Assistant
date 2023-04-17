import re

# Adapted from
# https://www.geeksforgeeks.org/how-to-validate-ssn-social-security-number-using-regular-expression/
# https://docs.opswat.com/mdcore/proactive-dlp/sample-regular-expressions
# https://github.com/m4ll0k/SecretFinder/blob/master/BurpSuite-SecretFinder/SecretFinder.py

regex_patterns = {
    "google_api": r"AIza[0-9A-Za-z-_]{35}",
    "bitcoin_address": r"([13][a-km-zA-HJ-NP-Z0-9]{26,33})",
    "slack_api_key": r"xox.-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}",
    "google_cloud_platform_auth": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
    "google_cloud_platform_api": r"[A-Za-z0-9_]{21}--[A-Za-z0-9_]{8}",
    "gmail_auth_token": r"[0-9(+-[0-9A-Za-z_]{32}.apps.qooqleusercontent.com",
    "github_auth_token": r"[0-9a-fA-F]{40}",
    "Instagram_token": r"[0-9a-fA-F]{7}.[0-9a-fA-F]{32}",
    "google_captcha": r"6L[0-9A-Za-z-_]{38}|^6[0-9a-zA-Z_-]{39}$",
    "google_oauth": r"ya29\.[0-9A-Za-z\-_]+",
    "amazon_aws_access_key_id": r"A[SK]IA[0-9A-Z]{16}",
    "amazon_mws_auth_toke": r"amzn\\.mws\\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    "amazon_aws_url": r"s3\.amazonaws.com[/]+|[a-zA-Z0-9_-]*\.s3\.amazonaws.com",
    "facebook_access_token": r"EAACEdEose0cBA[0-9A-Za-z]+",
    "authorization_basic": r"basic\s*[a-zA-Z0-9=:_\+\/-]+",
    "authorization_bearer": r"bearer\s*[a-zA-Z0-9_\-\.=:_\+\/]+",
    "authorization_api": r"api[key|\s*]+[a-zA-Z0-9_\-]+",
    "mailgun_api_key": r"key-[0-9a-zA-Z]{32}",
    "paypal_braintree_access_token": r"access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}",
    "square_oauth_secret": r"sq0csp-[ 0-9A-Za-z\-_]{43}|sq0[a-z]{3}-[0-9A-Za-z\-_]{22,43}",
    "square_access_token": r"sqOatp-[0-9A-Za-z\-_]{22}|EAAA[a-zA-Z0-9]{60}",
    "stripe_standard_api": r"sk_live_[0-9a-zA-Z]{24}",
    "stripe_restricted_api": r"rk_live_[0-9a-zA-Z]{24}",
    "github_access_token": r"[a-zA-Z0-9_-]*:[a-zA-Z0-9_\-]+@github\.com*",
    "rsa_private_key": r"-----BEGIN RSA PRIVATE KEY-----",
    "ssh_dsa_private_key": r"-----BEGIN DSA PRIVATE KEY-----",
    "ssh_ec_private_key": r"-----BEGIN EC PRIVATE KEY-----",
    "pgp_private_block": r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
    "json_web_token": r"ey[A-Za-z0-9_-]*\.[A-Za-z0-9._-]*|ey[A-Za-z0-9_\/+-]*\.[A-Za-z0-9._\/+-]*",
    "social_security_number": r"(?!666|000|9\\d{2})\\d{3}-(?!00)\\d{2}-(?!0{4})\\d{4}$",
    "e_mail": r"(?:^|\s)[\w!#$%&'*+/=?^`{|}~-](\.?[\w!#$%&'*+/=?^`{|}~-])*@\w+[.-]?\w*\.[a-zA-Z]{2,3}\b",
}

# Used to query the type later since that is more efficient than doing it dynamically.
regexes_patterns_inverse = {
    r"AIza[0-9A-Za-z-_]{35}": "google_api",
    r"([13][a-km-zA-HJ-NP-Z0-9]{26,33})": "bitcoin_address",
    r"xox.-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}": "slack_api_key",
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}": "google_cloud_platform_auth",
    r"[A-Za-z0-9_]{21}--[A-Za-z0-9_]{8}": "google_cloud_platform_api",
    r"[0-9(+-[0-9A-Za-z_]{32}.apps.qooqleusercontent.com": "gmail_auth_token",
    r"[0-9a-fA-F]{40}": "github_auth_token",
    r"[0-9a-fA-F]{7}.[0-9a-fA-F]{32}": "Instagram_token",
    r"6L[0-9A-Za-z-_]{38}|^6[0-9a-zA-Z_-]{39}$": "google_captcha",
    r"ya29\.[0-9A-Za-z\-_]+": "google_oauth",
    r"A[SK]IA[0-9A-Z]{16}": "amazon_aws_access_key_id",
    r"amzn\\.mws\\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}": "amazon_mws_auth_toke",
    r"s3\.amazonaws.com[/]+|[a-zA-Z0-9_-]*\.s3\.amazonaws.com": "amazon_aws_url",
    r"EAACEdEose0cBA[0-9A-Za-z]+": "facebook_access_token",
    r"basic\s*[a-zA-Z0-9=:_\+\/-]+": "authorization_basic",
    r"bearer\s*[a-zA-Z0-9_\-\.=:_\+\/]+": "authorization_bearer",
    r"api[key|\s*]+[a-zA-Z0-9_\-]+": "authorization_api",
    r"key-[0-9a-zA-Z]{32}": "mailgun_api_key",
    r"access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}": "paypal_braintree_access_token",
    r"sq0csp-[ 0-9A-Za-z\-_]{43}|sq0[a-z]{3}-[0-9A-Za-z\-_]{22,43}": "square_oauth_secret",
    r"sqOatp-[0-9A-Za-z\-_]{22}|EAAA[a-zA-Z0-9]{60}": "square_access_token",
    r"sk_live_[0-9a-zA-Z]{24}": "stripe_standard_api",
    r"rk_live_[0-9a-zA-Z]{24}": "stripe_restricted_api",
    r"[a-zA-Z0-9_-]*:[a-zA-Z0-9_\-]+@github\.com*": "github_access_token",
    r"-----BEGIN RSA PRIVATE KEY-----": "rsa_private_key",
    r"-----BEGIN EC PRIVATE KEY-----": "ssh_ec_private_key",
    r"-----BEGIN DSA PRIVATE KEY-----": "ssh_dsa_private_key",
    r"-----BEGIN PGP PRIVATE KEY BLOCK-----": "pgp_private_block",
    r"ey[A-Za-z0-9_-]*\.[A-Za-z0-9._-]*|ey[A-Za-z0-9_\/+-]*\.[A-Za-z0-9._\/+-]*": "json_web_token",
    r"(?!666|000|9\\d{2})\\d{3}-(?!00)\\d{2}-(?!0{4})\\d{4}$": "social_security_number",
    r"(?:^|\s)[\w!#$%&'*+/=?^`{|}~-](\.?[\w!#$%&'*+/=?^`{|}~-])*@\w+[.-]?\w*\.[a-zA-Z]{2,3}\b": "e_mail",
}


class PIIDetector:
    # Pre compile regexes.
    def __init__(self):
        self.regex_list_compiled = []
        for regex in regex_patterns.values():
            regex_compiled = re.compile(regex, re.I)
            self.regex_list_compiled.append(regex_compiled)

    # Returns first pii match in input_text or ("", None).
    def get_pii(self, input_text: str):
        for reg in self.regex_list_compiled:
            match = re.search(reg, input_text)
            if match is None:
                continue
            else:
                return (reg.pattern, match.start())
        return ("", None)

    def formatted_output(self, match_list: list):
        for match in match_list:
            print("\nLinenumber: " + str(match[0]))
            # To query the actual name efficiently, use  inverted dictionary.
            print("Type: " + regexes_patterns_inverse.get(match[1][0]))
            print("Start Position: " + str(match[1][1]))
