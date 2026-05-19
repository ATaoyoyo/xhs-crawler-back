def register_sha(parser):
    parser.add_argument('username', type=str, location='json')
    parser.add_argument('password', type=str, location='json')

def reg_args_valid(parser):
    parser.add_argument('username', type=str, location='json')
    parser.add_argument('password', type=str, location='json')