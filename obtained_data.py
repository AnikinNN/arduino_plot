import numpy as np


class ObtainedData:
    def __init__(self, buffer_size=5 * 60 * 2):
        self.buffer_size = buffer_size

        self.p = np.full([buffer_size], np.nan)
        self.i = np.full([buffer_size], np.nan)
        self.d = np.full([buffer_size], np.nan)

        self.output = np.full([buffer_size], np.nan)
        self.set_point = np.full([buffer_size], np.nan)
        self.temperature = np.full([buffer_size], np.nan)
        self.datetime = np.full([buffer_size], np.datetime64('nat').astype('datetime64[us]'))

        self.dict = {'t': self.temperature,
                     's': self.set_point,
                     'p': self.p,
                     'i': self.i,
                     'd': self.d,
                     'o': self.output, }

    @staticmethod
    def parse_data(input_str: str):
        tuples = input_str.strip().split('    ')
        tuples = {i.split(': ')[0].lower(): float(i.split(': ')[1]) for i in tuples}
        return tuples

    def append_data(self, input_str, event_datetime):
        parsed = self.parse_data(input_str)

        def shift_and_put(array: np.ndarray, value):
            result = np.roll(array, -1)
            result[-1] = value
            return result

        self.temperature = shift_and_put(self.temperature, parsed['t'])
        self.set_point = shift_and_put(self.set_point, parsed['s'])
        self.output = shift_and_put(self.output, parsed['o'])

        self.p = shift_and_put(self.p, parsed['p'])
        self.i = shift_and_put(self.i, parsed['i'])
        self.d = shift_and_put(self.d, parsed['d'])

        self.datetime = shift_and_put(self.datetime, np.datetime64(event_datetime))

    def set_buffer_size(self, new_buffer_size):
        # todo implement
        pass
