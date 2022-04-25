import datetime
import os.path
import sys


class Recorder:
    def __init__(self):
        self.name = None
        self.name = self.get_name()
        self.file = open(self.name, 'w')
        self.header_written = False

    def get_name(self):
        if self.name is None:
            path = os.path.join(os.path.dirname(sys.argv[0]), 'logs')
            if not os.path.exists(path):
                os.mkdir(path)

            datetime_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            path = os.path.join(path, f'record_{datetime_str}.csv')
            return path
        else:
            return self.name

    def close(self):
        self.file.close()
        self.name = None

    def write(self, data: str, datetime_: datetime.datetime):
        if not self.header_written:
            header = ['datetime']
            header.extend([i.split(': ')[0] for i in data.split('    ')])
            header = ','.join(header) + '\n'
            self.file.write(header)
            self.header_written = True

        self.file.write(
            f'{datetime_.strftime("%Y%m%d_%H%M%S_%f")},{",".join([i.split(": ")[1] for i in data.split("    ")])}\n')
