from multiprocessing.dummy import Pool

import requests, random, json

pool = Pool(100)

def create_test():
    return dict (

    action="create",
    login="example",
    password="example",

    name="test"+str(random.randint(0,100)),
)

def insert_test():
    return dict (

    action="insert",
    login="example",
    password="example",

    into="test"+str(random.randint(0,100)),
    content=dict(
        test="yeah this here is a test with stuff",
        usless_test_content="""Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.""",
        random_ammout=random.randint(0, 800000),
        random_string=random.choice(["Lorem", "ipsum", "dolor", "consetetur", "sadipscing"]),
        list_test=["HELLO", "THERE"]
    )
)

def select_test():
    return dict (

    action="select",
    login="example",
    password="example",

    #of="test"+str(random.randint(0,100)),
    of="twitch_msg"
    )




if __name__ == '__main__':
    print("-----")
    print("1 - Create")
    print("2 - Delete")
    print("3 - Drop")
    print("4 - Insert")
    print("5 - Select")
    print("6 - Update")
    print("-----")
    type_ = input("Select DB Test Protocoll: ")

    if int(type_) == 1:
        input("This will try to create 100 new Databases by 100 calls, it's random some will be created, some will trow a error")

    if int(type_) == 2:
        input("This will try to delete 100 Entry from random Databases (created by `Create`), it's random some will be deleted, some will trow a error")

    if int(type_) == 3:
        input("This will delete the Databases (created by `Create`) with 100 calls, its random some will be deleted, some will trow a error")

    if int(type_) == 4:
        input("This will try to insert 100 new entrys in the Databases created by `Create`")

    if int(type_) == 5:
        input("This will try to select 100 entry from all Databases (created by `Create`), its random if the selected DB is present, some will trow a error")

    if int(type_) == 6:
        input("This will try to update 100 entrys in all Databases (created by `Create`), its random some will be created, some will trow a error")

    futures = []
    for x in range(100):
        if int(type_) == 1:
            futures.append(pool.apply_async(requests.post, ["http://localhost:6969/"], kwds = dict(json = create_test())))

        if int(type_) == 2:
            futures.append(pool.apply_async(requests.post, ["http://localhost:6969/"], kwds = dict(json = insert_test())))

        if int(type_) == 3:
            futures.append(pool.apply_async(requests.post, ["http://localhost:6969/"], kwds = dict(json = insert_test())))

        if int(type_) == 4:
            futures.append(pool.apply_async(requests.post, ["http://localhost:6969/"], kwds = dict(json = insert_test())))

        if int(type_) == 5:
            futures.append(pool.apply_async(requests.post, ["http://localhost:6969/"], kwds = dict(json = select_test())))

        if int(type_) == 6:
            futures.append(pool.apply_async(requests.post, ["http://localhost:6969/"], kwds = dict(json = insert_test())))

    for future in futures:
        print(future.get().text)
        print(json.loads(future.get().text))

    input(">>>")