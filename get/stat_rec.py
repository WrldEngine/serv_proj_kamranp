def set_to_media(filename):
    file = open(f'get/{filename}.txt', 'r')
    old_num = file.read()

    counter = int(old_num) + 1
    new_num = old_num.replace(old_num, str(counter))

    new_file = open(f'get/{filename}.txt', 'w')
    new_file.write(new_num)

def get_to_media(filename):
    file = open(f'get/{filename}.txt', 'r')
    stat_show = file.read()
    return stat_show