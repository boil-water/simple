import struct

class RedcmData:
    def __init__(self, pixel_data, window_width, window_level, patient_info, annotations):
        self.pixel_data = pixel_data
        self.window_width = window_width
        self.window_level = window_level
        self.patient_info = patient_info
        self.annotations = annotations

    def to_binary(self):
        # Convert data to binary format
        binary_data = struct.pack('f', self.window_width)  # Example for float
        binary_data += struct.pack('f', self.window_level)
        # Add more fields as needed
        return binary_data

    @staticmethod
    def from_binary(binary_data):
        # Convert binary data back to RedcmData
        window_width = struct.unpack('f', binary_data[:4])[0]
        window_level = struct.unpack('f', binary_data[4:8])[0]
        # Extract more fields as needed
        return RedcmData(None, window_width, window_level, None, None)