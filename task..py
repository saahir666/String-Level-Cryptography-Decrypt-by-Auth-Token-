class SecureReplace:
    def __init__(self, target_path, auth_check):
        if not callable(auth_check):
            raise TypeError("auth_check must be callable")
        if not isinstance(target_path, str):
            raise TypeError("target_path must be a string")

        self.target_path = target_path
        self.auth_check = auth_check
        self.enforce_encrypted_write = True

    def _reverse_text(self, s):
        """Simple reversible obfuscation."""
        return s[::-1]

    def replace_with_user_data(self, user_data, strip_auth_token=False):
        
        if not isinstance(user_data, str):
            raise TypeError("user_data must be a string")

        is_auth = bool(self.auth_check(user_data))

        to_write = user_data
        if is_auth and strip_auth_token:
            if "\n" in to_write:
                first, rest = to_write.split("\n", 1)
                if first.startswith("Token:") or first.startswith("TOKEN:") or first.startswith("token:"):
                    to_write = rest

        if is_auth:
            written_type = "original"
        else:
            to_write = self._reverse_text(to_write)
            written_type = "obfuscated"

      
        with open(self.target_path, "w", encoding="utf-8") as f:
            f.write(to_write)

        return {"status": "done", "written": written_type, "path": self.target_path}

    def write_plaintext(self, data):
        raise PermissionError("Direct plaintext writing is not allowed. Use replace_with_user_data().")



def demo_auth_check(data):
   
    if not isinstance(data, str):
        return False
    first_line = data.split("\n", 1)[0].strip()
    return first_line == "Token:Secret"


def main_demo():
    target = "example.txt"
    replacer = SecureReplace(target, auth_check=demo_auth_check)


    legit_payload = "Token:Secret\nThis is legitimate content.\nLine 2."
    res1 = replacer.replace_with_user_data(legit_payload, strip_auth_token=True)
    print("Legit result:", res1)
    print("File contents after legit write:")
    with open(target, "r", encoding="utf-8") as f:
        print("-----")
        print(f.read())
        print("-----\n")

    intruder_payload = "Attacker content that must be obfuscated.\nMore lines."
    res2 = replacer.replace_with_user_data(intruder_payload)
    print("Intruder result:", res2)
    print("File contents after intruder write:")
    with open(target, "r", encoding="utf-8") as f:
        print("-----")
        print(f.read())
        print("-----\n")


    try:
        replacer.write_plaintext("nope")
    except PermissionError as e:
        print("Blocked plaintext write:", e)


if __name__ == "__main__":
    main_demo()
