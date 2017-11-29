import requests

class dump:
	pass

def clear():
	print("\n"*100)

def get_data():
	clear()
	dump.adress = input("Enter DB Adress or hit enter for 'http://localhost':\n>>> ")
	if dump.adress == "":
		dump.adress = 'http://localhost'
	dump.port = input("Enter DB Port or hit enter for None:\n>>> ")
	if dump.port != "":
		dump.port = ":"+dump.port
	dump.username = input("Enter DB Username or hit enter for None\n>>> ")
	dump.password = input("Enter DB Password or hit enter for None\n>>> ")

def create_call():
	while True:
		clear()
		print("This will create new container.\n")
		print("Enter New Container name to create a new one, or 'q' to return")
		name = input(">>>: ")
		if name == "q":break
		if name == "":continue

		call = dict(action="create",login=dump.username,password=dump.password,name=name)
		print(str(call)+'\n')

		while True:
			y = input("Enter 'y' to send command or 'q' to cancel\n>>> ")
			if y == 'y':
				try:
					r = requests.post(dump.adress+dump.port, json=call)
					print(r.text)
					input("\n\n\n Continue ->")
					break
				except:
					print("Error")

			elif y == "q":
				return

def drop_call():
	while True:
		clear()
		print("This will remove a container.\n")
		print("Enter Container name to delete, or 'q' to return")
		name = input(">>>: ")
		if name == "q":break
		if name == "":continue

		call = dict(action="delete",login=dump.username,password=dump.password,name=name)
		print(str(call)+'\n')

		while True:
			y = input("Enter 'y' to send command or 'q' to cancel\n>>> ")
			if y == 'y':
				try:
					r = requests.post(dump.adress+dump.port, json=call)
					print(r.text)
					input("\n\n\n Continue ->")
					break
				except:
					print("Error")

			elif y == "q":
				return

def insert_call(): #
	while True:
		clear()
		print("This will remove a container.\n")
		print("Enter Container name to delete, or 'q' to return")
		name = input(">>>: ")
		if name == "q":break
		if name == "":continue

		call = dict(action="delete",login=dump.username,password=dump.password,name=name)
		print(str(call)+'\n')

		while True:
			y = input("Enter 'y' to send command or 'q' to cancel\n>>> ")
			if y == 'y':
				try:
					r = requests.post(dump.adress+dump.port, json=call)
					print(r.text)
					input("\n\n\n Continue ->")
					break
				except:
					print("Error")

			elif y == "q":
				return

def delete_call(): #
	while True:
		clear()
		print("This will delete entrys from a container.\n")
		print("Enter Container name to delete, or 'q' to return")
		name = input(">>>: ")
		if name == "q":break
		if name == "":continue

		while True:
			print("Enter WHERE statement or hit enter to select all:")
			where = input("Remember eval compare form:\nFALSE: a_test_value = 'hello'\nRIGHT: data['a_test_value'] == 'hello'\n\n>>> ")
			if where == "":
				break
			print("Use this where? enter: 'y'")
			y = input(">>> ")
			if y == "y":
				break
			else:
				continue



		call = dict(action="delete",login=dump.username,password=dump.password,of=name, where=where)
		print(str(call)+'\n')

		while True:
			y = input("Enter 'y' to send command or 'q' to cancel\n>>> ")
			if y == 'y':
				try:
					r = requests.post(dump.adress+dump.port, json=call)
					print(r.text)
					input("\n\n\n Continue ->")
					break
				except:
					print("Error")

			elif y == "q":
				return

def update_call(): #
	while True:
		clear()
		print("This will remove a container.\n")
		print("Enter Container name to delete, or 'q' to return")
		name = input(">>>: ")
		if name == "q":break
		if name == "":continue

		call = dict(action="delete",login=dump.username,password=dump.password,name=name)
		print(str(call)+'\n')

		while True:
			y = input("Enter 'y' to send command or 'q' to cancel\n>>> ")
			if y == 'y':
				try:
					r = requests.post(dump.adress+dump.port, json=call)
					print(r.text)
					input("\n\n\n Continue ->")
					break
				except:
					print("Error")

			elif y == "q":
				return

def select_call(): #
	while True:
		clear()
		print("This will select data from a container.\n")
		print("Enter Container name to select, or 'q' to return")
		name = input(">>>: ")
		if name == "q":break
		if name == "":continue

		while True:
			fields = input("Enter comma seperated fields to request, or hit Enter for all:\n>>> ")
			if fields == "":
				fields = []
				break
			fields = fields.split(",")
			print("Use this fields? enter: 'y'")
			y = input(fields)
			if y == "y":
				break
			else:
				continue

		while True:
			print("Enter WHERE statement or hit enter to select all:")
			where = input("Remember eval compare form:\nFALSE: a_test_value = 'hello'\nRIGHT: data['a_test_value'] == 'hello'\n\n>>> ")
			if where == "":
				break
			print("Use this where? enter: 'y'")
			y = input(">>> ")
			if y == "y":
				break
			else:
				continue

		call = dict(action="select",login=dump.username,password=dump.password,of=name,fields=fields,where=where)
		print(str(call)+'\n')

		while True:
			y = input("Enter 'y' to send command or 'q' to cancel\n>>> ")
			if y == 'y':
				try:
					r = requests.post(dump.adress+dump.port, json=call)
					print(r.text)
					input("\n\n\n Continue ->")
					break
				except:
					print("Error")

			elif y == "q":
				return

get_data()

while True:
	clear()
	print("Select a method:")
	print("  1 - Create")
	print("  2 - Drop")
	print("  3 - Insert")
	print("  4 - Delete")
	print("  5 - Update")
	print("  6 - Select")
	print("  - - - - - - -")
	print("  l - Re-enter login")
	method = input(">>> ")

	if method == "l":
		get_data()
		continue

	try:
		method = int(method)
	except:
		continue

	if not 1 <= method <= 6:
		continue

	if method == 1:
		create_call()

	if method == 2:
		drop_call()

	if method == 3:
		insert_call()

	if method == 4:
		delete_call()

	if method == 5:
		update_call()

	if method == 6:
		select_call()

