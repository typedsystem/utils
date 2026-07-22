import re

def _is_public_ssh_key_format(key_string, key_type=None):
    """
    Internal helper to check if a string matches the format of a public SSH key.
    Optionally, checks for a specific key type.
    """
    valid_key_types = [
        "ssh-rsa",
        "ssh-dss",
        "ecdsa-sha2-nistp256",
        "ecdsa-sha2-nistp384",
        "ecdsa-sha2-nistp521",
        "sk-ecdsa-sha2-nistp256@openssh.com",
        "ssh-ed25519",
        "sk-ssh-ed25519@openssh.com"
    ]

    if key_type:
        if not key_type.startswith("ssh-") and not key_type.startswith("ecdsa-") and not key_type.startswith("sk-"):
            type_regex = rf"(?:ssh-{re.escape(key_type.lower())}|ecdsa-sha2-nistp[235]?[0-9][0-9])" # Looser for ecdsa
            if key_type.lower() == "ecdsa":
                type_regex = r"(?:ecdsa-sha2-nistp256|ecdsa-sha2-nistp384|ecdsa-sha2-nistp521|sk-ecdsa-sha2-nistp256@openssh.com)"
            elif key_type.lower() == "ed25519":
                type_regex = r"(?:ssh-ed25519|sk-ssh-ed25519@openssh.com)"
            elif key_type.lower() == "rsa":
                type_regex = r"ssh-rsa"
            elif key_type.lower() == "dss":
                type_regex = r"ssh-dss"
            else:
                type_regex = re.escape(key_type)
        else:
            type_regex = re.escape(key_type.lower())

        if key_type.lower() not in [t.lower().replace("ssh-", "").replace("-sha2-nistp", "").replace("@openssh.com","") for t in valid_key_types] and \
           key_type.lower() not in [t.lower() for t in valid_key_types]:
            pass
    else:
        type_regex = r"|".join([re.escape(t) for t in valid_key_types])
        type_regex = f"(?:{type_regex})"

    base64_pattern = r"[A-Za-z0-9+/]+={0,2}"
    comment_pattern = r"(?:\s+.*)?"

    pattern = re.compile(rf"^{type_regex}\s+{base64_pattern}{comment_pattern}$", re.IGNORECASE)
    match = pattern.match(key_string)

    if match and key_type:
        matched_type = key_string.split(' ')[0].lower()
        if key_type.lower() == "rsa" and matched_type == "ssh-rsa":
            return True
        elif key_type.lower() == "dss" and matched_type == "ssh-dss":
            return True
        elif key_type.lower() == "ecdsa" and any(m in matched_type for m in ["ecdsa-sha2", "sk-ecdsa"]):
            return True
        elif key_type.lower() == "ed25519" and any(m in matched_type for m in ["ssh-ed25519", "sk-ssh-ed25519"]):
            return True
        elif matched_type == key_type.lower():
            return True
        elif matched_type == f"ssh-{key_type.lower()}":
            return True
        else:
            return False
    return bool(match)

def _is_ssh_key(key_string, key_type, private):
    if not isinstance(key_string, str) or not key_string.strip():
        return False

    key_string = key_string.strip()
    norm_key_type = (key_type or "").lower()
    if private:
        openssh_private_pattern = re.compile(
            r"-----BEGIN OPENSSH PRIVATE KEY-----\s*([A-Za-z0-9+/=\s]+)\s*-----END OPENSSH PRIVATE KEY-----",
            re.DOTALL
        )
        if norm_key_type:
            header_map = {
                "rsa": "RSA PRIVATE KEY",
                "dss": "DSA PRIVATE KEY",
                "ecdsa": "EC PRIVATE KEY",
                "ed25519": "OPENSSH PRIVATE KEY",
                "openssh": "OPENSSH PRIVATE KEY"
            }
            expected_header_suffix = header_map.get(norm_key_type, "").upper()
            if not expected_header_suffix:
                if norm_key_type in ["ssh-rsa", "ssh-dss", "ecdsa-sha2-nistp256", "ssh-ed25519", "sk-ecdsa-sha2-nistp256@openssh.com"]:
                    pass
                else:
                    return False

            if expected_header_suffix == "OPENSSH PRIVATE KEY":
                return bool(openssh_private_pattern.search(key_string))
            else:
                pem_private_pattern = re.compile(
                    rf"-----BEGIN {re.escape(expected_header_suffix)}-----\s*([A-Za-z0-9+/=\s]+)\s*-----END {re.escape(expected_header_suffix)}-----",
                    re.DOTALL
                )
                return bool(pem_private_pattern.search(key_string))
        else:
            if openssh_private_pattern.search(key_string):
                return True
            pem_any_private_pattern = re.compile(
                r"-----BEGIN (?:(RSA|DSA|EC|ENCRYPTED|OPENSSH) )?PRIVATE KEY-----\s*([A-Za-z0-9+/=\s]+)\s*-----END (?:(RSA|DSA|EC|ENCRYPTED|OPENSSH) )?PRIVATE KEY-----",
                re.DOTALL
            )
            return bool(pem_any_private_pattern.search(key_string))
    else:
        return _is_public_ssh_key_format(key_string, key_type)
