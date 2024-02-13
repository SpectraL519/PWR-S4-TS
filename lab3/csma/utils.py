from enum import Enum
import re
import argparse
import random
import pygame



class SignalFront:
    def __init__(self, channel, position, dir, signal_name, active):
        self.channel = channel
        self.position = position
        self.dir = dir
        self.signal_name = signal_name
        self.active = active

    def tick(self):
        signals = self.channel.cells[self.position].signals
        if self.active:
            signals.add(self.signal_name)
        else:
            if self.signal_name in signals:
                signals.remove(self.signal_name)

        self.position += self.dir
        
        if self.position == -1 or self.position == len(self.channel.cells):
            self.channel.signal_fronts.remove(self)

class Channel:
    class Cell:
        def __init__(self, id):
            self.id = id
            self.signals = set()
            self.node_present = False

        def is_free(self):
            return not self.signals

        def has_collision(self):
            return len(self.signals) > 1
        
    def __init__(self, length):
        self.length = length
        self.cells = [Channel.Cell(i) for i in range(length)]
        self.signal_fronts = []
        self.nodes = []

    def tick(self):
        for signal_front in self.signal_fronts:
            signal_front.tick()

        for node in self.nodes:
            node.tick()

    def add_node(self, name, position):
        cell = self.cells[position]
        cell.node_present = True
        node = Node(self, cell, name)
        self.nodes.append(node)
        return node

    def add_signal_fronts(self, position, phase, name):
        self.signal_fronts += [
            SignalFront(self, position, -1, name, phase),
            SignalFront(self, position, 1, name, phase)
        ]

    def size(self):
        return 2 * self.length

    def draw(self, surface, position, size):
        color = (255, 255, 255)

        step = int(size / len(self.cells))
        rect_size = int(0.9 * step) 

        big_font = pygame.font.Font(pygame.font.get_default_font(), int(rect_size / 1.5))
        small_font = pygame.font.Font(pygame.font.get_default_font(), rect_size // 2)


        for i, cell in enumerate(self.cells):
            text = ';'.join(cell.signals)
            rect_position = (position[0] + i * step, position[1])
            rect = pygame.Rect(rect_position, (rect_size, rect_size))
            if cell.node_present:
                pygame.draw.rect(surface, color, rect, 3)
            else:
                pygame.draw.rect(surface, color, rect, 1)
            surface.blit(small_font.render(text, True, color), rect_position)


        for node in self.nodes:
            x = position[0] + node.cell.id * step
            y = position[1] + rect_size + 10
            lines = node.get_status().splitlines()
            for i, l in enumerate(lines):
                surface.blit(big_font.render(l, True, color), (x, y + rect_size * i))


class Node:
    class State(str, Enum):
        RECIEVING = "Recieving"
        TRANSMITTING = "Transmitting"
        WAIT_SIGNAL = "Waiting - signal detected"
        WAIT_COLISION = "Waiting - colision detected"

    def __init__(self, channel: Channel, cell: Channel.Cell, name: str):
        self.channel = channel
        self.cell = cell
        self.state = Node.State.RECIEVING
        self.counter = 0
        self.fails_count = 0
        self.wait_ticks = 0
        self.name = name

    @staticmethod
    def parse(value: str):
        search = re.search('\((\w+),(\d+)\)', value)
        if (search):
            return {
                'name': search.group(1),
                'position': int(search.group(2))
            }
        else:
            msg = f"Error: Invalid value format of ({value})! Expected format: '(name, positionition)'!"
            raise argparse.ArgumentTypeError(msg) 

    def tick(self):
        if self.state == Node.State.WAIT_COLISION:
            if self.wait_ticks > 0:
                self.wait_ticks -= 1
            else:
                self.state = Node.State.WAIT_SIGNAL

        if self.state == Node.State.WAIT_SIGNAL and self.cell.is_free():
            self._start_transmition()

        if self.state == Node.State.TRANSMITTING:
            if self.cell.has_collision():
                self.collision()

            self.counter += 1
            if self.counter == self.channel.size():
                self._stop_transmition()
                print(f"Node {self.name} - TRANSMITTING completed")

    def _start_transmition(self):
        print(f"Node {self.name} - TRANSMITTING started")
        self.state = Node.State.TRANSMITTING
        self.counter = 0
        self.channel.add_signal_fronts(self.cell.id, True, self.name)

    def _stop_transmition(self):
        self.state = Node.State.RECIEVING
        self.channel.add_signal_fronts(self.cell.id, False, self.name)

    def send_frame(self):
        if self.state == Node.State.RECIEVING:
            self.fails_count = 0
            self.state = Node.State.WAIT_SIGNAL

    def collision(self):
        assert(self.state == Node.State.TRANSMITTING)

        print(f"Node {self.name} - detected collision #{self.fails_count}")
        self._stop_transmition()
        self.fails_count += 1
        max_wait_slots = 2 ** min(10, self.fails_count) - 1
        wait_slots = random.randint(max_wait_slots)
        print(f"Node {self.name} - wait {wait_slots} / {max_wait_slots} slots")
        self.wait_ticks = wait_slots * self.channel.size()

        self.state = Node.State.WAIT_COLISION 

    def get_status(self):
        text = f"Node {self.name}\n"
        text += f"State: {self.state}\n"

        if self.state == Node.State.TRANSMITTING:
            text += f'{self.counter} / {self.channel.size()} bits'

        if self.state == Node.State.WAIT_COLISION:
            text += f'Remaining ticks: {self.wait_ticks}'

        return text
