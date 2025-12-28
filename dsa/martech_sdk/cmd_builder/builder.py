from martech_sdk.cmd_builder.build_shortcut import BuildShortcut


CMD_MAP = {
    "build_shortcut": BuildShortcut
}


class CommandBuilder:
    def __init__(self):
        self.cmd_obj = None
        self.args = []
    
    def format(self, cmd_type):
        self.cmd_obj = eval(f"CMD_MAP['{cmd_type}']")()
        return self
    
    def option(self, operation, value):
        self.cmd_obj = eval(f"self.cmd_obj.{operation}({value})")
        return self

    def build(self):
        return self.cmd_obj.build()
        