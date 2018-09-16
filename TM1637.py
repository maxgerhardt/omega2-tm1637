import onionGpio
import time 

class TM1637: 

    # list mapping a digit to 
    # the segment bytes
    digit_to_segment = [
        0b00111111,    # 0
		0b00000110,    # 1
		0b01011011,    # 2
		0b01001111,    # 3
		0b01100110,    # 4
		0b01101101,    # 5
		0b01111101,    # 6
		0b00000111,    # 7
		0b01111111,    # 8
		0b01101111,    # 9
		0b01110111,    # A
		0b01111100,    # b
		0b00111001,    # C
		0b01011110,    # d
		0b01111001,    # E
		0b01110001     # F 
    ]

    # segment defines
    SEG_A = 0b00000001
    SEG_B = 0b00000010
    SEG_C = 0b00000100
    SEG_D = 0b00001000
    SEG_E = 0b00010000
    SEG_F = 0b00100000
    SEG_G = 0b01000000

    # static part of the bytes 
    TM1637_I2C_COMM1 = 0x40
    TM1637_I2C_COMM2 = 0xC0
    TM1637_I2C_COMM3 = 0x80

    # Constructor with CLK and DIO pin
    def __init__(self, pin_clk, pin_dio):
        # constructo GPIO objects from them
        self.pin_clk = onionGpio.OnionGpio(pin_clk)
        self.pin_dio = onionGpio.OnionGpio(pin_dio)
        self.set_brightness(5, 1)

    def set_brightness(self, brightness, on=True):
        """
        Sets the brightness and the on/off state of the display.
        Only saves changes locally. Must issue a new "display()"
        call to transfer these values.
            :param self: display object
            :param brightness: brightness between 0 to 7
            :param on: True for on, False else
        """
        self.brightness = (brightness & 0x7) | (0x08 if on else 0x00)

    def start(self):
        """
        Starts the transmission phase
        """
        #set DIO pin to output, low
        self.pin_dio.setOutputDirection(initial=0)
        self.bit_delay()

    def stop(self):
        """
        Ends the transmission phase.
        """
        self.pin_dio.setOutputDirection(initial=0)
        self.bit_delay()
        self.pin_clk.setInputDirection()
        self.bit_delay()
        self.pin_dio.setInputDirection()
        self.bit_delay()

    def bit_delay(self):
        """
        Waits one clock cycle. 
        """
        # wait 10 microseconds.
        # Python on the Omega2 is soo slow anyways
        # that we probably wouldn't even need the delay..
        time.sleep( 10 / 1000.0 / 1000.0)

    def write_byte(self, data):
        """
        Writes a byte to the data bus
            :param self: display object
            :param data: byte to write
        """

        # write all 8 bits
        for i in range(8):
            # CLK low
            self.pin_clk.setOutputDirection(initial=0)
            self.bit_delay()

            # set data bit 
            # remember that DIO is pulled-up.
            # if we set it to input, the line goes high.
            # else, we have to set the output active LOW.
            if data & 0x01 != 0:
                self.pin_dio.setInputDirection()
            else:
                self.pin_dio.setOutputDirection(initial=0) 

            # clock high 
            self.pin_clk.setInputDirection()
            self.bit_delay()

            # prepare next bit 
            data = data >> 1
        # wait for ACK
        # CLK to 0
        self.pin_clk.setOutputDirection(initial=0)
        self.pin_dio.setInputDirection()
        self.bit_delay()

        # CLK to 1
        self.pin_clk.setInputDirection()
        self.bit_delay()
        ack = self.pin_dio.getValue()
        #print("Ack: " + str(ack))
        if ack == 0:
            self.pin_dio.setOutputDirection(initial=0)
        
        self.bit_delay()
        self.pin_clk.setOutputDirection(initial=0)
        self.bit_delay()

        return ack

    def set_segments(self, segments, pos=0):
        """
        Display arbitrary segment data on the module.

        This function receives raw segment values as input and displays them. The segment data
        is given as a byte array, each byte corresponding to a single digit. Within each byte,
        bit 0 is segment A, bit 1 is segment B etc.
        The function may either set the entire display or any desirable part on its own. The first
        digit is given by the @ref pos argument with 0 being the leftmost digit. The 
        of the segments list is the number of digits to be set. Other digits are not affected.
        
            :param self: Display object
            :param segments: List of bytes 
            :param pos: position to start writing segment data to
        """

        # Write COMM1 
        self.start()
        self.write_byte(TM1637.TM1637_I2C_COMM1)
        self.stop()

        # Write COMM2 + first digit address 
        self.start()
        self.write_byte(TM1637.TM1637_I2C_COMM2 + (pos & 0x03))

        # write segment data 
        for i in range(len(segments)):
            self.write_byte(segments[i])

        self.stop()

        # write COMM3 and brightness 
        self.start()
        self.write_byte(TM1637.TM1637_I2C_COMM3 + (self.brightness & 0x0f))
        self.stop()

    def encode_digit(self, digit):
        """
        Returns the state of the segments when the given
        digit is to be displayed. 
            :param self: display object
            :param digit: digit to encode (0-15)
        """
        return TM1637.digit_to_segment[digit & 0x0f]

    def display(self, number, leading_zero = False, length = 4, pos = 0, dots = 0x00):
        """
        Displays a decimal number 

            :param self: display object 
            :param number: The number to  be shown
            :param lead_zero: When true, leading zeros are displayed. Otherwise unnecessary digits are 
                              blank
            :param length: The number of digits to set. The user must ensure that the number to be shown
                            fits to the number of digits requested (for example, if two digits are to be displayed,
                            the number must be between 0 to 99)
            :param pos: pos The position most significant digit (0 - leftmost, 3 - rightmost)
            :param dots: Dot/Colon enable. The argument is a bitmask, with each bit corresponding to a dot
                        between the digits (or colon mark, as implemented by each module). i.e.
                        For displays with dots between each digit:
                        * 0.000 (0b10000000)
                        * 00.00 (0b01000000)
                        * 000.0 (0b00100000)
                        * 0.0.0.0 (0b11100000)
                        For displays with just a colon:
                        * 00:00 (0b01000000)
                        For displays with dots and colons colon:
                        * 0.0:0.0 (0b11100000)
        """
        digits = [0, 0, 0, 0]
        divisors = [1, 10, 100, 1000]
        leading = True

        for k in range(4):
            divisor = divisors[4 - 1 - k]
            d = number // divisor
            digit = 0

            if d == 0:
                if leading_zero or not leading or k == 3:
                    digit = self.encode_digit(d)
                else: 
                    digit = 0
            else: 
                digit = self.encode_digit(d)
                number = number - (d * divisor)
                leading = False

            digit |= (dots & 0x80)
            dots <<= 1

            digits[k] = digit
        # construct new digits list
        self.set_segments(digits[4 - length::], pos)