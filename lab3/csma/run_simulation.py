import argparse
from win32api import GetSystemMetrics
import pygame
import numpy as np

from utils import Channel, Node




def parse_args():
    def required_length(nmin, nmax):
        class RequiredLength(argparse.Action):
            def __call__(self, parser, args, values, option_string=None):
                if not nmin <= len(values) <= nmax:
                    msg='Error: Argument "{f}" requires between {nmin} and {nmax} arguments!'.format(
                        f=self.dest,nmin=nmin,nmax=nmax)
                    raise argparse.ArgumentTypeError(msg)
                setattr(args, self.dest, values)
        return RequiredLength

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--channel_size", type=int, default=50)
    parser.add_argument(
        "-n", "--nodes", 
        type=Node.parse, 
        nargs='+', 
        action=required_length(1, 9),
        default = [
            {'name': 'A', 'position': 0},
            {'name': 'B', 'position': 20},
            {'name': 'C', 'position': 45}
        ]
    )
    parser.add_argument(
        "-ww", "--window_width", 
        type=int, 
        default=1200,
        choices=range(300, GetSystemMetrics(0))
    )
    parser.add_argument(
        "-wh", "--window_height", 
        type=int, 
        default=300,
        choices=range(200, GetSystemMetrics(1))
    )
    opt = parser.parse_args()
    return vars(opt)


def main(
    channel_size: int,
    nodes: list,
    window_width: int,
    window_height: int
):
    pygame.init()
    window_size = np.array((window_width, window_height))
    surface = pygame.display.set_mode(window_size)  

    channel = Channel(channel_size)

    for (i, node) in enumerate(nodes):
        nodes[i] = channel.add_node(**node)

    clock = pygame.time.Clock()
    CHANNEL_UPDATE_PERIOD_MS = 150
    CHANNEL_UPDATE_TICK = pygame.USEREVENT + 1 
    pygame.time.set_timer(CHANNEL_UPDATE_TICK, CHANNEL_UPDATE_PERIOD_MS)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            if event.type == CHANNEL_UPDATE_TICK:
                channel.tick()
            if event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
                if key.isdigit():
                    idx = int(key) - 1
                    if idx in range(len(nodes)):
                        nodes[idx].send_frame()

        surface.fill((0,0,66))
        channel.draw(surface, window_size * 0.025, window_width * 0.95)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    params = parse_args()
    main(**params)