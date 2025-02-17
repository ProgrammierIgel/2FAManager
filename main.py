import FAManager
import Output

class FAController:
  def __init__(self):
    self.console = Output.Console()
    self.manager = self.initialize_manager(path=".")
    self.main_points = ["get code", "add new token", "set new password", "exit"]
    self.state = ""

  def run(self):
    while True:
      self.state = self.console.selection_input(self.main_points)
      if self.state == self.main_points[0]:
        self.get_code_from_token()
      elif self.state == self.main_points[1]:
        self.add_new_token()
      elif self.state == self.main_points[2]:
        self.set_new_password()
      elif self.state == self.main_points[3]:
        self.console.returnToCommandLine()
        print("Thank you for using")
        break


  def input_password(self, pre_str: str) -> str:
    return self.console.input(f"{pre_str}{"\n"if not pre_str=="" else ""}Please put in the password:", type="password")

  def initialize_manager(self, path:str = ".")-> FAManager.FAManager:
    pre_str=""
    while True:
      try:
        self.console.console_clear()
        return FAManager.FAManager(path, self.input_password(pre_str=pre_str))
      except ValueError as ValueErrorInstance:
        if "Wrong password" in ValueErrorInstance.args:
          pre_str = "Wrong password! Try again!"
          continue
        else:
          raise ValueErrorInstance
      except Exception as ExceptionInstance:
        if isinstance(ExceptionInstance, ValueError):
          continue
        raise ExceptionInstance


  def get_code_from_token(self):
    while True:
      tokens = self.manager.get_all_names()
      tokens.append("return to main menu")
      token_to_get = self.console.selection_input(tokens, msg="Please select the account you want: ")
      if not token_to_get in tokens:
        raise ValueError("INTERNAL ERROR")
      if token_to_get == "return to main menu":
        return
      while True:
        totp_code = self.manager.get_totp_from_secret(token_to_get)
        self.console.console_clear()
        e = self.console.input(f"The code for account {token_to_get} is >{totp_code[:3]} {totp_code[3:]}< \nPress '/e' to escape!")
        if e == '/e':
          return


  def add_new_token(self):
    methods = ["Cam", "QR Code With Path", "Input Manual", "Input Automatic", "Return"]
    while True:
      method = self.console.selection_input(methods)
      if method == methods[0]:
        self.add_new_token_by_cam()
      elif method == methods[1]:
        self.add_new_token_by_image()
      elif method == methods[2]:
        self.add_new_token_by_input_manual()
      elif method == methods[3]:
        self.add_new_token_by_input_automatic()
      elif method == methods[4]:
        break
    return

  def add_new_token_by_cam(self):
    while True:
      name_types = ["issuer as name", "custom name", "return"]
      name_type = self.console.selection_input(name_types)
      if name_type == name_types[0]:
        self.console.console_clear()
        self.console.print('"ESCAPE" TO ESCAPE')
        self.manager.add_secret_from_cam(True)
      if name_type == name_types[2]:
        return
      else:
        pre_str = ""
        while True:
          name = self.console.input(f"{pre_str}Please give the name in:")
          if name != "":
            self.console.console_clear()
            self.console.print('"ESCAPE" TO ESCAPE')
            self.manager.add_secret_from_cam(False, name)
            return
          pre_str = "Try again!"


  def add_new_token_by_image(self):
    while True:
      name_types = ["issuer as name", "custom name", "return"]
      name_type = self.console.selection_input(name_types)
      is_name_issuer: bool | None = None
      name: None | str = None

      if name_type == name_types[0]:
        is_name_issuer =  True
        name = ""
      elif name_type == name_types[1]:
        pre_str = ""
        while True:
          name = self.console.input(f"{pre_str}Put in an name. return with '/e'")
          if name == "":
            pre_str = "Name cant be empty!"
            continue
          if name.startswith("/e"):
            return
        is_name_issuer = False

      elif name_type == name_types[2]:
        return
      exceptions = 0
      while True:
        self.console.console_clear()
        path = self.console.input("Give in the path. To exit '/e':")
        if path.startswith("/e"):
          break

        try:
          if name == None or is_name_issuer == None:
            raise RuntimeError("Name or status variabel is None")
          self.manager.add_secret_from_image(path, is_name_issuer, name=name)
          return
        except:
          exceptions+=1
          if exceptions >3:
            raise ValueError("More than 3 exceptions")

  def add_new_token_by_input_manual(self):
    was_activated:list[str] = []
    name = ""
    input: dict[str, bool | str] = {
      "issuer": "",
      "secret": "",
      "label": "",
      "is issuer name": False
    }
    while True:
      keys: list[str] = []
      for i in input:
        if not i in was_activated:
          keys.append(i)
      if len(keys) == 0:
        if not isinstance(input["issuer"], str) or not isinstance(input["secret"], str) or not isinstance(input["label"], str) or not isinstance(input["is issuer name"], bool):
          raise TypeError("Wrong type")
        self.manager.add_secret_from_input_manual(
          input["issuer"],
          input["secret"],
          input["label"],
          input["is issuer name"],
          name
        )
        return
      keys.append("return")
      selection = self.console.selection_input(keys)
      if selection.startswith("return"):
        return
      if selection in was_activated:
        raise RuntimeError("Cant set property that already is set")
      if selection == "is issuer name":
        pre_str = ""
        is_issuer_name = self.console.selection_input(["True", "False", "return"])
        if is_issuer_name == "return":
          continue
        elif bool(is_issuer_name) == False:
          while True:
            self.console.console_clear()
            name = self.console.input(f"{pre_str}Put in the name that you want. To escape '/e'")
            if name.startswith("/e"):
              break
            if name == "":
              pre_str = "Name cant be unset. Try again "
              continue
            input["is issuer name"] = False
            was_activated.append("is issuer name")
            break
          continue
        input["is issuer name"] = True
        was_activated.append("is issuer name")
        continue
      pre_str = ""
      while True:
        self.console.console_clear()
        selection_input = self.console.input(f"{pre_str}Please put in the item that you want to set for variable {selection}. /e to escape")
        if selection_input == "":
          pre_str = "Cant be Unset! Try again! "
          continue
        if selection_input.startswith('/e'):
          break
        input[selection] = selection_input
        was_activated.append(selection)
        break


  def add_new_token_by_input_automatic(self):
     while True:
      name_types = ["issuer as name", "custom name", "return"]
      name_type = self.console.selection_input(name_types)
      is_name_issuer: bool | None = None
      name: None | str = None

      if name_type == name_types[0]:
        is_name_issuer =  True
        name = ""
      elif name_type == name_types[1]:
        pre_str = ""
        while True:
          name = self.console.input(f"{pre_str}Put in an name. return with '/e'")
          if name == "":
            pre_str = "Name cant be empty!"
            continue
          if name.startswith("/e"):
            return
        is_name_issuer = False

      elif name_type == name_types[2]:
        return
      pre_str = ""
      while True:
        self.console.console_clear()
        secret = self.console.input(f"{pre_str}Give in the otpauth code. To exit '/e':")
        if secret.startswith("/e"):
          break

        try:
          if name == None or is_name_issuer == None:
            raise RuntimeError("Name or status variabel is None")
          self.manager.add_secret_from_input_auto(secret, is_name_issuer, name=name)
          return
        except ValueError as ValueErrorInstance:
          if "Not an otpauth URI" in ValueErrorInstance.args:
            pre_str = "Not an OTP Code. Try again!\n"
            continue
          raise ValueErrorInstance


  def set_new_password(self):
    self.console.console_clear()
    current_password = self.input_password("")
    if current_password.startswith('/e'):
      return
    if not self.manager.check_password(current_password):
      raise ValueError("WRONG PASSWORD")
    pre_str=""
    while True:
      self.console.console_clear()
      new_password = self.console.input(f"{pre_str}Put in a new password '/e' to escape:")
      if new_password == "/e":
        return
      if new_password == "":
        pre_str = "PASSWORD CANT BE UNSET!\n"
        continue
      if 32 % len(new_password) != 0:
        possible_numbers: list[int] = []
        for i in range(32):
          if 32%i == 0:
            possible_numbers.append(32)
        pre_str = f"INPUT MUST  BE  RETURN A INTEGER IF IT DIVIDE BY 32!({str(possible_numbers).replace("[", "").replace("]", "")}\n"
        continue
      if self.manager.check_password(new_password):
        pre_str = "YOU CANT SET THE SAME PASSWORD TWICE!\n"
      break
    pre_str = ""
    while True:
      self.console.console_clear()
      repeat_new_password = self.console.input(f"{pre_str}Please repeat password! '/e' to escape:")
      if repeat_new_password.startswith('/e'):
        return
      if new_password != repeat_new_password:
        pre_str = " YOU MUST INPUT THE SAME PASSWORD!\n"

      check = self.console.selection_input(["TRUE", "FALSE"], msg="ARE YOU SHURE THAT YOU WANT TO SET THIS NEW PASSWORD?")
      if check == "TRUE":
        self.manager.export_password(current_password, new_password)
      return




if __name__ == "__main__":
  manager = FAController()
  manager.run()
