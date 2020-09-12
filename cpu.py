"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.reg = [0] * 8
        self.sp = 7
        self.reg[self.sp] = 0xf4  # 244
        self.ram = [0] * 256
        self.pc = 0
        self.running = False
        self.fl = 0b00000000

    def load(self):
        """Load a program into memory."""

        address = 0

        program = []

        # get file name from command line arguments
        if len(sys.argv) != 2:
            print("Usage: example_cpu.py <filename>")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split('#')
                    code_val = split_line[0].strip()
                    if code_val == '':
                        continue
                    num = int(code_val, 2)
                    program.append(num)
                    # address += 1
        except FileNotFoundError:
            print(f'{sys.argv[1]} file not found')
            sys.exit(1)

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        # Addition
        if op == 0b10100000:
            self.reg[reg_a] += self.reg[reg_b]
            self.pc += 3

        # Subtraction
        elif op == 0b10100001:
            self.reg[reg_a] -= self.reg[reg_b]
            self.pc += 3

        # Multiply
        elif op == 0b10100010:
            self.reg[reg_a] *= self.reg[reg_b]
            self.pc += 3

        # Division
        elif op == 0b10100011:
            if self.reg[reg_b] == 0:
                print("You cannot divide by zero.")
                sys.exit(1)
            # self.reg[reg_a] = self.reg[reg_a] / self.reg[reg_b]
            self.reg[reg_a] /= self.reg[reg_b]
            self.pc += 3

        # CMP
        elif op == 0b10100111:
            #  'equal' condition - a == b
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            # 'greater than' condition - a > b
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            # 'less than' condition - a < b
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            self.pc += 3

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # accept the address to read and return the value stored there
    def ram_read(self, MAR):
        MDR = self.ram[MAR]
        return MDR

    # MDR == value, MAR == ram address
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running is True:
            IR = self.ram[self.pc]
            is_alu = IR >> 5 & 0b1

            # If an ALU op is detected, send to alu method
            if is_alu == 1:
                self.alu(IR, self.ram[self.pc + 1], self.ram[self.pc + 2])

            # LDI - sets a specified register to a specified value
            if IR == 0b10000010:
                # register address
                op_a = self.ram[self.pc + 1]
                op_b = self.ram[self.pc + 2]
                self.reg[op_a] = op_b
                self.pc += 3

            # PRN - that prints the numeric value stored in a register.
            if IR == 0b01000111:
                op_a = self.ram[self.pc + 1]
                print(self.reg[op_a])
                self.pc += 2

            # HLT - halt
            if IR == 0b00000001:
                self.running = False

            # PUSH
            if IR == 0b01000101:
                # get register address
                given_register = self.ram[self.pc + 1]
                # retrieve value in register
                value_in_register = self.reg[given_register]
                # decrement sp
                self.reg[self.sp] -= 1
                # write value in given register to RAM at the SP location
                self.ram[self.reg[self.sp]] = value_in_register
                # increment program counter
                self.pc += 2

            # POP
            if IR == 0b01000110:
                # get register address
                given_register = self.ram[self.pc + 1]
                # retrieve value from RAM
                value_from_memory = self.ram[self.reg[self.sp]]
                # write value to the given register
                self.reg[given_register] = value_from_memory
                # increment sp
                self.reg[self.sp] += 1
                # increment program counter
                self.pc += 2

            # CALL
            if IR == 0b01010000:
                # get the given register in the operand
                given_register = self.ram[self.pc + 1]
                # STORE THE RETURN ADDRESS (PC + 2) ONTO THE STACK
                # decrement stack pointer
                self.reg[self.sp] -= 1
                # write return address to RAM
                self.ram[self.reg[self.sp]] = self.pc + 2
                # set PC to the value inside given register
                self.pc = self.reg[given_register]

            # RET
            if IR == 0b00010001:
                # set PC to the value at the top of the stack
                self.pc = self.ram[self.reg[self.sp]]
                # increment Stack Pointer
                self.reg[self.sp] += 1

            # JMP
            if IR == 0b01010100:
                # retrieve address from given register
                given_register = self.ram[self.pc + 1]
                # set program counter to address in given register
                self.pc = self.reg[given_register]

            # JEQ
            if IR == 0b01010101:
                # If 'equal' flag is True, set program counter to address in given register
                if self.fl & 0b1:
                    given_register = self.ram[self.pc + 1]
                    self.pc = self.reg[given_register]
                else:
                    self.pc += 2

            # JNE
            if IR == 0b01010110:
                # If 'equal' flaf is False, set program counter to address in given register
                if self.fl & 0b1:
                    self.pc += 2
                else:
                    given_register = self.ram[self.pc + 1]
                    self.pc = self.reg[given_register]
