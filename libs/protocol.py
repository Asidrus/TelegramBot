class Protocol:
    header = [{'head': "message", "data": {"len": 4, "offset": 0, "value": None}},
              {'head': "text", "data": {"len": 4, "offset": 4, "value": None}},
              {'head': "image", "data": {"len": 8, "offset": 8, "value": None}}]

    raw = b''

    STOP_READING = False
    serial = 0
    data = {}

    def __headerLength__(self):
        count = 0
        for head in self.header:
            count = count + head['data']['len']
        return count

    def __bodyLength__(self):
        length = 0
        for head in self.header:
            if head['head'] != "message":
                length = length + head['data']['value']
        return length

    def set(self, key, value):
        for head in self.header:
            if head['head'] == key:
                head['data']['value'] = value
                return None

    def writeMessage(self, text: bytes, image: bytes):
        self.set("text", len(text))
        self.set("image", len(image))
        self.set("message", self.__headerLength__() + self.__bodyLength__())
        for head in self.header:
            self.raw = self.raw + (head['data']['value']).to_bytes(head['data']['len'], byteorder='big')
        self.raw = self.raw + text + image
        return self.raw

    def readMessage(self, s: bytes):
        for head in self.header:
            offset = head['data']['offset']
            length = head['data']['len']
            self.set(head['head'], int.from_bytes(s[offset:offset + length], 'big'))
        bl = self.__headerLength__()
        cursor = bl
        for head in self.header:
            if head['head'] != 'message':
                length = head['data']['value']
                self.data[head['head']] = s[cursor:cursor + length]
                cursor = cursor + length

    def setChunk(self, chunk):
        if self.serial == 0:
            self.raw = chunk
            offset = self.header[0]['data']['offset']
            length = self.header[0]['data']['len']
            self.header[0]['data']['value'] = int.from_bytes(self.raw[offset:offset + length], 'big')
            self.serial = self.serial + 1
        else:
            self.raw = self.raw + chunk
            self.serial = self.serial + 1
        if len(self.raw) >= self.header[0]['data']['value']:
            self.STOP_READING = True
            self.readMessage(self.raw)


if __name__ == "__main__":
    pass
