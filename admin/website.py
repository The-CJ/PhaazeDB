def website(path):
    if path == '/admin':
        r = open("admin/source/html/main.html","r",encoding='utf-8').read()
        return r

    else:
        path = path.replace("..", "")
        path = path.strip('/')

        try:
            r = open(path, "r", encoding='utf-8').read()
            return r

        except:
            return ""
