from datetime import datetime, timezone

def parse_argcl(arg:list) -> tuple:
    debug_mode = False
    if len(arg) == 1:
        raise ValueError(
            'Please, add the start date argument on the command line in format dd.mm.yy')
    else:
        for ar in arg[1:]:
            if ar == 'debag':
                debug_mode = True
            else:
                try:
                    start_date = datetime.strptime(
                        ar, '%d.%m.%y').replace(tzinfo=timezone.utc)
                except ValueError as e:
                    raise ValueError( 
            'Please, add the start date argument on the command line in format dd.mm.yy') from e
    return (start_date,debug_mode)

if __name__ == '__main__':
    from sys import argv
    print(parse_argcl(argv))