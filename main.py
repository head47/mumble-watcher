#!/usr/bin/env python3

import asyncio
from sys import argv

import matrix_login
import watcher


def print_usage():
    print(f"Usage: {argv[0]} [main|login]")


def main():
    match len(argv):
        case 1:
            asyncio.run(watcher.main())
        case 2:
            match argv[1]:
                case "main":
                    asyncio.run(watcher.main())
                case "login":
                    asyncio.run(matrix_login.main())
                case _:
                    print_usage()
        case _:
            print_usage()


if __name__ == "__main__":
    main()
