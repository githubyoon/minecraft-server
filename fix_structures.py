import gzip
import struct
import sys
import os
import shutil

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

class NBTParser:
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def read_byte(self):
        val = self.data[self.offset]
        self.offset += 1
        return val

    def read_bytes(self, n):
        val = self.data[self.offset:self.offset+n]
        self.offset += n
        return val

    def read_short(self):
        val = struct.unpack(">h", self.data[self.offset:self.offset+2])[0]
        self.offset += 2
        return val

    def read_int(self):
        val = struct.unpack(">i", self.data[self.offset:self.offset+4])[0]
        self.offset += 4
        return val

    def read_long(self):
        val = struct.unpack(">q", self.data[self.offset:self.offset+8])[0]
        self.offset += 8
        return val

    def read_float(self):
        val = struct.unpack(">f", self.data[self.offset:self.offset+4])[0]
        self.offset += 4
        return val

    def read_double(self):
        val = struct.unpack(">d", self.data[self.offset:self.offset+8])[0]
        self.offset += 8
        return val

    def read_string(self):
        length = self.read_short()
        val = self.read_bytes(length).decode('utf-8', errors='replace')
        return val

    def parse_tag(self, tag_type):
        if tag_type == TAG_END:
            return None
        elif tag_type == TAG_BYTE:
            return self.read_byte()
        elif tag_type == TAG_SHORT:
            return self.read_short()
        elif tag_type == TAG_INT:
            return self.read_int()
        elif tag_type == TAG_LONG:
            return self.read_long()
        elif tag_type == TAG_FLOAT:
            return self.read_float()
        elif tag_type == TAG_DOUBLE:
            return self.read_double()
        elif tag_type == TAG_BYTE_ARRAY:
            length = self.read_int()
            return self.read_bytes(length)
        elif tag_type == TAG_STRING:
            return self.read_string()
        elif tag_type == TAG_LIST:
            sub_type = self.read_byte()
            length = self.read_int()
            return (sub_type, [self.parse_tag(sub_type) for _ in range(length)])
        elif tag_type == TAG_COMPOUND:
            compound = {}
            while True:
                sub_type = self.read_byte()
                if sub_type == TAG_END:
                    break
                name = self.read_string()
                val = self.parse_tag(sub_type)
                compound[name] = (sub_type, val)
            return compound
        elif tag_type == TAG_INT_ARRAY:
            length = self.read_int()
            return [self.read_int() for _ in range(length)]
        elif tag_type == TAG_LONG_ARRAY:
            length = self.read_int()
            return [self.read_long() for _ in range(length)]
        else:
            raise ValueError(f"Unknown tag type {tag_type}")

class NBTSerializer:
    def __init__(self):
        self.data = bytearray()

    def write_byte(self, val):
        self.data.append(val)

    def write_bytes(self, b):
        self.data.extend(b)

    def write_short(self, val):
        self.data.extend(struct.pack(">h", val))

    def write_int(self, val):
        self.data.extend(struct.pack(">i", val))

    def write_long(self, val):
        self.data.extend(struct.pack(">q", val))

    def write_float(self, val):
        self.data.extend(struct.pack(">f", val))

    def write_double(self, val):
        self.data.extend(struct.pack(">d", val))

    def write_string(self, val):
        b = val.encode('utf-8')
        self.write_short(len(b))
        self.write_bytes(b)

    def write_tag(self, tag_type, val):
        if tag_type == TAG_END:
            return
        elif tag_type == TAG_BYTE:
            self.write_byte(val)
        elif tag_type == TAG_SHORT:
            self.write_short(val)
        elif tag_type == TAG_INT:
            self.write_int(val)
        elif tag_type == TAG_LONG:
            self.write_long(val)
        elif tag_type == TAG_FLOAT:
            self.write_float(val)
        elif tag_type == TAG_DOUBLE:
            self.write_double(val)
        elif tag_type == TAG_BYTE_ARRAY:
            self.write_int(len(val))
            self.write_bytes(val)
        elif tag_type == TAG_STRING:
            self.write_string(val)
        elif tag_type == TAG_LIST:
            sub_type, items = val
            self.write_byte(sub_type)
            self.write_int(len(items))
            for item in items:
                self.write_tag(sub_type, item)
        elif tag_type == TAG_COMPOUND:
            for k, (t, v) in val.items():
                self.write_byte(t)
                self.write_string(k)
                self.write_tag(t, v)
            self.write_byte(TAG_END)
        elif tag_type == TAG_INT_ARRAY:
            self.write_int(len(val))
            for x in val:
                self.write_int(x)
        elif tag_type == TAG_LONG_ARRAY:
            self.write_int(len(val))
            for x in val:
                self.write_long(x)

def modify_nbt(tag):
    modified = False
    if isinstance(tag, dict):
        if 'WorldGenSettings' in tag:
            t, v = tag['WorldGenSettings']
            if 'generate_features' in v:
                ft, fv = v['generate_features']
                if fv == 0:
                    v['generate_features'] = (ft, 1)
                    print("Changed generate_features from 0 to 1")
                    modified = True
        for k, (t, v) in tag.items():
            if modify_nbt(v):
                modified = True
    elif isinstance(tag, tuple) and len(tag) == 2 and isinstance(tag[1], list):
        for item in tag[1]:
            if modify_nbt(item):
                modified = True
    return modified

def process_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    print(f"Processing: {filepath}")
    with gzip.open(filepath, 'rb') as f:
        data = f.read()

    parser = NBTParser(data)
    root_type = parser.read_byte()
    if root_type != TAG_COMPOUND:
        print("Error: Root tag is not Compound")
        return

    root_name = parser.read_string()
    root_val = parser.parse_tag(root_type)

    if modify_nbt(root_val):
        # Backup first
        backup_path = filepath + ".bak"
        if not os.path.exists(backup_path):
            shutil.copy2(filepath, backup_path)
            print(f"Created backup at {backup_path}")

        # Serialize
        serializer = NBTSerializer()
        serializer.write_byte(root_type)
        serializer.write_string(root_name)
        serializer.write_tag(root_type, root_val)

        with gzip.open(filepath, 'wb') as f:
            f.write(serializer.data)
        print("Successfully modified and saved level.dat")
    else:
        print("generate_features was not found or already 1")

if __name__ == '__main__':
    target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world", "level.dat")
    process_file(target)
