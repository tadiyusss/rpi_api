class IRReader:
    def __init__(self):
        self.filetype = None
        self.version = None
        self.commands = {}

    def get_header(self, lines): 
        for line in lines:
            if line.startswith("#"):
                break
            if line.startswith("Filetype: "):
                self.filetype = line.split("Filetype: ")[1]
            elif line.startswith("Version: "):
                self.version = line.split("Version: ")[1]


    def read(self, filename) -> None:
        with open(filename, 'r') as ir_file:
            ir = ir_file.read()
        ir_lines = ir.split('\n')
        self.get_header(ir_lines)
        found_command = False
        current_command = None
        for line in ir_lines:
            if line.startswith("name: "):
                found_command = True
                current_command = line.split("name: ")[1]
            
            if found_command:
                if line.startswith("name: "):
                    self.commands[line.split("name: ")[1]] = {}
                
                if line.startswith("#"):
                    found_command = False
                    current_command = None
                
                if current_command:
                    key, value = line.split(": ")
                    self.commands[current_command][key] = value

    def get_command(self, name):
        return self.commands[name]
    
    def get_command_names(self):
        return self.commands.keys()

