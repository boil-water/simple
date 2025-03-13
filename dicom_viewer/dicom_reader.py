import struct

class DicomData:
    def __init__(self):
        self.tags = {}
        self.pixel_data_offset = 0
        self.pixel_data_length = 0
        self.is_little_endian = True
        self.is_explicit_vr = True
        self.rows = 0
        self.cols = 0
        self.window_center = -600
        self.window_width = 1500
        self.image_data = None

    def get_vr(self, tag):
        vr_map = {
            "0010,1010": "AS",
            "0010,0040": "CS",
            "0010,2150": "LO",
            "0018,0060": "DS",
            "0018,1151": "IS",
            "0028,1050": "DS",
            "0028,1051": "DS",
            "0018,0050": "DS",
            "0028,1052": "DS",
            "0028,1053": "DS",
            "7fe0,0010": "OW",
            "0028,0010": "US",
            "0028,0011": "US",
        }
        return vr_map.get(tag, "UN")

    def parse_file(self, filepath):
        try:
            with open(filepath, "rb") as f:
                file_data = f.read()

            if file_data[128:132] != b"DICM":
                raise ValueError("Not a valid DICOM file")
            print("DICOM 文件头验证通过。")

            self._read_tags(file_data)
            print("标签读取完成。")
        except Exception as e:
            print(f"解析 DICOM 文件失败: {e}")
            raise

    def _read_tags(self, file_data):
        offset = 132
        while offset + 6 < len(file_data):
            group, element = struct.unpack("<HH", file_data[offset:offset + 4])
            tag = f"{group:04x},{element:04x}"
            offset += 4

            vr = self.get_vr(tag)
            if self.is_explicit_vr and len(file_data) >= offset + 2:
                vr = file_data[offset:offset + 2].decode("ascii")
                offset += 2

            if vr in ["OB", "OW", "SQ", "UN"]:
                offset += 2
                length = struct.unpack("<I", file_data[offset:offset + 4])[0]
                offset += 4
            else:
                length = struct.unpack("<H", file_data[offset:offset + 2])[0]
                offset += 2

            value = file_data[offset:offset + length]
            offset += length

            if tag == "0028,0010":
                self.rows = struct.unpack("<H", value)[0]
            elif tag == "0028,0011":
                self.cols = struct.unpack("<H", value)[0]
            elif tag == "0028,1050":
                value_str = value.decode("ascii").strip()
                self.window_center = float(value_str.split("\\")[0])
            elif tag == "0028,1051":
                value_str = value.decode("ascii").strip()
                self.window_width = float(value_str.split("\\")[0])
            elif tag == "7fe0,0010":
                self.pixel_data_offset = offset - length
                self.pixel_data_length = length

            self.tags[tag] = value

    def get_metadata(self):
        metadata = {
            "年龄": self.tags.get("0010,1010", b"").decode("ascii", "ignore"),
            "性别": self.tags.get("0010,0040", b"").decode("ascii", "ignore"),
            "居住地": self.tags.get("0010,2150", b"").decode("ascii", "ignore"),
            "电压": self.tags.get("0018,0060", b"").decode("ascii", "ignore"),
            "电流": self.tags.get("0018,1151", b"").decode("ascii", "ignore"),
            "层厚": self.tags.get("0018,0050", b"").decode("ascii", "ignore"),
            "斜率": self.tags.get("0028,1053", b"").decode("ascii", "ignore"),
            "截距": self.tags.get("0028,1052", b"").decode("ascii", "ignore"),
        }
        return metadata

    def get_image_data(self):
        if not self.pixel_data_offset or not self.pixel_data_length:
            raise ValueError("No pixel data found")

        pixels = struct.unpack(f"<{self.rows * self.cols}H", self.tags["7fe0,0010"])

        window_min = self.window_center - self.window_width // 2
        window_max = self.window_center + self.window_width // 2

        def apply_window(value):
            if value < window_min:
                return 0
            elif value > window_max:
                return 255
            return int((value - window_min) / self.window_width * 255)

        return [apply_window(p) for p in pixels]