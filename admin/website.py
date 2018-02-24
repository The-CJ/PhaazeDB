def website(path):
    if path == '/admin':
        r = open("admin/source/html/main.html","rb",).read()
        return r

    else:
        path = path.replace("..", "")
        path = path.strip('/')

        try:
            r = open(path, "rb").read()
            return r

        except:
            return ""
