class SharedMemoryRingBuffer:
    def __init__(self, capacity=1024):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.head = 0
        self.tail = 0

    def push(self, item):
        next_head = (self.head + 1) % self.capacity
        if next_head == self.tail:
            return False
        self.buffer[self.head] = item
        self.head = next_head
        return True

    def pop(self):
        if self.tail == self.head:
            return None
        item = self.buffer[self.tail]
        self.tail = (self.tail + 1) % self.capacity
        return item
