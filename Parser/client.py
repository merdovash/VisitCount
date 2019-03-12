import argparse


parser = argparse.ArgumentParser(description="Process parameters")
parser.add_argument('--host', metavar='H', default='http://bisitor.itut.ru', type=str,
                        help='you can specify server host address', dest='host')
parser.add_argument('--test', type=bool, default=False, help='for testing without Reader')
parser.add_argument('--css', type=bool, default=True, help='you can disable css')

client_args = parser.parse_args()