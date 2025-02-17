import base64
import json
import cv2
from cryptography.fernet import Fernet
from Crypto.Hash import SHA256
import pyotp


class FAManager:

    def __init__(self, path: str, password: str):
        self.path = path
        self.set_password(password)
        self.cam_config = {"camera_id": 0}

    def import_password(self) -> str:
        return json.load(open(f"{self.path}/secrets.json"))["password"]

    def export_password(self, old_password: str, new_password: str):
        if self.password != old_password:
            raise ValueError("Wrong password")
        if self.password == new_password:
            return
        if 32%len(new_password) != 0:
            raise ValueError("MUST BE POSSIBLE TO DIVIDE 32 BY LENGTH")
        json_dict = json.load(open(f"{self.path}/secrets.json"))
        json_dict["password"] = SHA256.new(new_password.encode()).hexdigest()
        json.dump(json_dict, open(f"{self.path}/secrets.json", "w"), indent=2)

    def set_password(self, password_to_check: str) -> str:

        if not self.check_password(password_to_check):
            raise ValueError(("Wrong password"))
        self.password = password_to_check
        return password_to_check

    def import_secret(self, name: str):
        password_hash = (json.load(open(f"{self.path}/secrets.json", "r"))["secrets"])[
            name
        ]
        key = self.stretch_with_numbers(self.password, 32)
        return (
            Fernet(base64.urlsafe_b64encode(key.encode()))
            .decrypt(bytes.fromhex(password_hash))
            .decode()
        )

    def export_secret(self, name: str, secret: str):
        secrets_already = json.load(open(f"{self.path}/secrets.json"))
        key = self.stretch_with_numbers(self.password, 32)
        (secrets_already["secrets"])[name] = (
            Fernet(base64.urlsafe_b64encode(key.encode()))
            .encrypt(secret.encode())
            .hex()
        )
        json.dump(secrets_already, open(f"{self.path}/secrets.json", "w"), indent=2)

    def stretch_with_numbers(self, password: str, length: int) -> str:
        s = ""
        if password == "" or length % len(password) != 0:
            raise ValueError(
                "Incorrect input", password == "", length % len(password) == 0
            )
        to_add = (length // len(password)) - 1
        for letter in password:
            s += letter
            for count in range(to_add):
                s += str(count)
        return s

    def get_totp_from_secret(self, name: str):
        secret = self.import_secret(name)
        parsed = pyotp.parse_uri(secret)
        totp = pyotp.TOTP(
            parsed.secret, parsed.digits, parsed.digest, parsed.name, parsed.issuer
        )
        return totp.now()

    def add_secret_from_cam(self, is_name_issuer: bool, name: str="") -> None:
        if not is_name_issuer and  name == "":
            raise ValueError("Name not defined")
        cv2.namedWindow("QR Code Reader")
        qcd = cv2.QRCodeDetector()
        cap = cv2.VideoCapture(self.cam_config["camera_id"])
        while True:
            ret, frame = cap.read()
            if ret:
                ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
                if ret_qr:
                    for s, p in zip(decoded_info, points):
                        if s:
                            if is_name_issuer:
                                issuer = pyotp.parse_uri(decoded_info[0]).issuer
                                if issuer == None:
                                  raise ValueError("No issuer set")
                            else:
                                issuer = name
                            self.export_secret(issuer, decoded_info[0])
                            cv2.destroyAllWindows()
                            return
                        frame = cv2.polylines(
                            frame, [p.astype(int)], True, (0, 0, 255), 8
                        )

                cv2.imshow("QR Code Reader", frame)
            key = cv2.waitKey(1)
            if key == 27:
                cv2.destroyAllWindows()
                return

    def add_secret_from_image(self, path: str, is_name_issuer: bool, name: str="")-> None:
      if not is_name_issuer and name  == "":
        raise ValueError("Name not defined")
      qcd = cv2.QRCodeDetector()
      frame = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
      is_qr_code, decoded_info, _, _ = qcd.detectAndDecodeMulti(frame)
      if not is_qr_code:
          raise ValueError("No qrcode found")
      issuer = name
      if is_name_issuer:
        issuer = pyotp.parse_uri(decoded_info[0]).issuer
        if issuer == None:
          raise ValueError("No issuer set")
      self.export_secret(issuer, decoded_info[0])

    def add_secret_from_input_manual(self, issuer: str, secret: str, label: str, is_name_issuer: bool, name: str= "") -> None:
      if not is_name_issuer and name == "":
        raise ValueError("Name is not defined")
      if is_name_issuer:
        name = issuer
      self.export_secret(name, f"otpauth://totp/{label}?secret={secret}&issuer={issuer}")

    def add_secret_from_input_auto(self, otpauth: str, is_name_issuer: bool, name: str= "") ->None:
      if not is_name_issuer and name == "":
        raise ValueError("Name is not defined")
      issuer = name
      if is_name_issuer:
        issuer = pyotp.parse_uri(otpauth).issuer
        if not issuer:
          raise ValueError("No issuer set")
        self.export_secret(issuer, otpauth)

    def get_all_names(self) -> list[str]:
      names: list[str] = []
      dict = json.load(open(f"{self.path}/secrets.json"))["secrets"]
      for name in dict:
        names.append(name)
      return names

    def check_password(self, password: str) -> bool:
        if SHA256.new(password.encode()).hexdigest() != self.import_password():
            return False
        return True
