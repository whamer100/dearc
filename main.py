import cli
from dearc import Dearc


def main():
    opt = cli.parse()
    # print("yo waddup this is working")
    dearc = Dearc(opt)
    dearc.run()


if __name__ == '__main__':
    main()
