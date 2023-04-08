import json
import logging
from argparse import ArgumentParser, Namespace, FileType
from server_bot.bot import ServerBot


LOG_NAMES = ['default', 'debug', 'info', 'warning', 'error', 'critical']
LOG_LEVELS = {l: i * 10 for i, l in enumerate(LOG_NAMES)}


def create_logger(log_level: int) -> None:
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logging.getLogger('discord.http').setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', type=str, required=True)
    parser.add_argument('-p', '--pid', type=int, required=True)
    parser.add_argument('-t', '--type', type=str, choices={'Steam', 'Spy'}, default='Steam')
    parser.add_argument('-l', '--log-level', type=str, choices=LOG_NAMES, default='info')
    return parser


def main(args: Namespace):
    config = json.load(open(args.config, 'r'))

    bot = ServerBot(args.pid, config)
    bot.run(config['TOKEN'])


if __name__ == '__main__':
    try:
        args = create_argument_parser().parse_args()
        create_logger(LOG_LEVELS[args.log_level])
    except Exception as e:
        print(e)
        exit(1)

    main(args)
