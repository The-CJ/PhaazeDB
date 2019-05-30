import hashlib

def password(passwd):
	passwd = str(passwd)
	password = hashlib.sha256(passwd.encode("UTF-8")).hexdigest()
	return password
