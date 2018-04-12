import sqlite3, time, sys, string, random

# Initializer
goal = int(sys.argv[2])
n = int(sys.argv[3])
m = int(sys.argv[4])
node_id = str(sys.argv[1])
search_key_id = str(sys.argv[5])

conn = sqlite3.connect('p2p_db.db')
cur = conn.cursor()

def id_generator(size, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def padded_bin(num, width):
    s = bin(num)
    return s[2:].zfill(width)

def goal2(node_id):
	time.sleep(10)
	key_text = id_generator(n)
	key_id = ''
	key_id_sum = 0
	for i in range(len(key_text)):
		key_id_sum += ord(key_text[i])
	key_id = padded_bin(key_id_sum % (2 ** n), n)
	sql = "INSERT INTO node(node_id, key_id, key_text) VALUES(?, ?, ?)"
	cur.execute(sql, (node_id, str(key_id), str(key_text)))
	conn.commit()

if goal is 2:
	while m:
		# Run goal 2 file system
		goal2(node_id)
		m = m - 1

elif goal is 3:
	sql = "SELECT * FROM `node` WHERE `node_id`='" + node_id + "'"
	cur.execute(sql)
	node_files = cur.fetchall()
	for node_file in node_files:
		if node_file[2] in search_key_id or search_key_id in node_file[2]:
			print("=== key is in : " + str(node_file[1]))

elif goal is 4:
	pass

conn.close()