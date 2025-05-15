from pymodbus.client import ModbusTcpClient

from .register import Register


class Modbus:
    def __init__(self, ipAdress, ipPort=502, modbusUnit=3):
        self.registers: set[int] = set()
        self.available_registers: dict[int, Register] = {}
        self.unit = modbusUnit
        self._ipadress = ipAdress
        self._ipport = ipPort
        self.polling_groups = []

    # add to a set of polled registers
    def poll_register(self, register_id: int):
        if register_id not in self.available_registers:
            raise Exception(f"Register with the id {register_id} does not exist")
        else:
            self.registers.add(register_id)

    # add to the Dict of available registers
    def add_register(self, register: Register):
        self.available_registers[register.id] = register

    def start(self):
        if not self.registers:
            raise Exception("No register selected, can't poll inverter")

        self._group_register()

        return self._poll()

    def list_available_registers(self):
        for register in self.available_registers.values():
            print(register)

    def _poll(self):
        print("_poll")
        result = []

        # open socket every poll ... in case of network errors and deamon-mode the polling goes on
        with ModbusTcpClient(self._ipadress, port=self._ipport, timeout=10) as client:
            print(f"Client connected: {client.connected}")
            for group in self.polling_groups:
                start_id = group[0].id
                length = sum(reg.length for reg in group)

                print(f"Start_id: {start_id}, Length: {length}, Unit: {self.unit}")
                try:
                    response = client.read_holding_registers(
                        address=start_id,
                        count=length,
                        slave=self.unit
                    )
                except Exception as e:
                    print(f"Error: {e.message}")

                finally:
                    print("readholdingRegister done")

                if not response:
                    print("No response")
                    continue

                print(f"Response: {response}")

                for index, register in enumerate(group, start=0):
                    start_index = sum(register.length for register in group[0:index])
                    chunk = response.registers[start_index: start_index + register.length]
                    register.set_registers(chunk)  # set and decode values

                    result.append(register)

                    print(register)

        return result

    def _group_register(self):
        if not len(self.registers):
            return

        # self.registers is a set, all values are unique
        sorted_register = sorted(self.registers)

        polling_groups = [[]]  # new empty group

        next_id = sorted_register[0]
        for id in sorted_register:
            register = self.available_registers[id]

            if next_id != id:
                polling_groups.append([])  # New group, because too much distance between registers

            current_group = polling_groups[-1]  # get the Last group
            current_group.append(register)
            next_id = register.id + register.length

        self.polling_groups = polling_groups
