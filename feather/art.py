import gc, os

def art_logo():
    print('''
        '{tttttttttttttttttttttttt^ *tttt
        :@@@@@@@@@@@@@@@@@@@@@@@@@m d@@@@N`
        :@@@@@@@@@@@@@@@@@@@@@@@@@m d@@@@N`
        :@@@@@m:::::::::::::rQ@@@@m d@@@@N`
        :@@@@@] vBBBBBBBBBN,`]oooo* d@@@@N`
        :@@@@@] o@@@NNNQ@@@"`ueeee| d@@@@N`
        :@@@@@] o@@&   ,||?`'Q@@@@m d@@@@N`
        :@@@@@] o@@Q]tt{{{z-'Q@@@@QOQ@@@@N`
        :@@@@@] o@@@@@@@@@@"'Q@@@@@@@@@@@N`
        :@@@@@] ';;;;;;y@@@"'Q@@@@N7Q@@@@N`
        :@@@@@] \KKe^^^a@@@"'Q@@@@m d@@@@N`
        :@@@@@] o@@@@@@@@@@" _::::' d@@@@N`
        :@@@@@] raaaaaaaaay..H####} d@@@@N`
        :@@@@@#eeeeeeeeeeeeek@@@@@m d@@@@N`
        :@@@@@@@@@@@@@@@@@@@@@@@@@m d@@@@N`
        :@@@@@@@@@@@@@@@@@@@@@@@@@e K@@@@W`
        .........................` `....-

              Booting CSH LetMeIn...      
    ''')


# It's not art, but suck my dick.
def art_mem_info():
    # Show available memory
    print('Memory Info - gc.mem_free()')
    print('---------------------------')
    print(f'{gc.mem_free()} Bytes\n')

    # Show flash size
    flash = os.statvfs('/')
    flash_size = flash[0] * flash[2]
    flash_free = flash[0] * flash[3]
    print("Flash - os.statvfs('/')")
    print('---------------------------')
    print(f"Size: {flash_size} Bytes\nFree: {flash_free} Bytes\n")

def art_ready():
    print('''

        /$$$$$$$                            /$$
        | $$__  $$                          | $$
        | $$  \ $$  /$$$$$$   /$$$$$$   /$$$$$$$ /$$   /$$
        | $$$$$$$/ /$$__  $$ |____  $$ /$$__  $$| $$  | $$
        | $$__  $$| $$$$$$$$  /$$$$$$$| $$  | $$| $$  | $$
        | $$  \ $$| $$_____/ /$$__  $$| $$  | $$| $$  | $$
        | $$  | $$|  $$$$$$$|  $$$$$$$|  $$$$$$$|  $$$$$$$ /$$
        |__/  |__/ \_______/ \_______/ \_______/ \____  $$|__/
                                                /$$  | $$
                                                |  $$$$$$/
                                                \______/

    ''')