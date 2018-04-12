import sqlite3, shlex
import subprocess, requests, threading, string, random, os, signal
from threading import Thread

cwd = os.getcwd()

# Database connection
conn = sqlite3.connect('p2p_db.db')
cur = conn.cursor()

n = 0
m = 0
p = 0

def running(binary_id, goal, n, m, key_id):
	command_line = "python3 node.py '" + binary_id + "' " + str(goal) + " " + str(n) + " " + str(m) + " " + str(key_id)
	ls_output=subprocess.Popen(shlex.split(command_line), cwd=cwd, shell=False)
	pid = ls_output.pid

	sql = "UPDATE `nodes` SET `process_id`=" + str(pid) + " WHERE `binary_id`='" + binary_id + "'"
	cur.execute(sql)
	conn.commit()

def node_run(binary_id, goal, n, m, key_id):
	child = threading.Thread(target=running(binary_id, goal, n, m, key_id))
	child.start()
	child.join()

def padded_bin(num, width):
    s = bin(num)
    return s[2:].zfill(width)

def goal1():
	# Clear database
	sql = "DELETE FROM `nodes` WHERE 1=1"
	cur.execute(sql)
	conn.commit()
	sql = "DELETE FROM `node` WHERE 1=1"
	cur.execute(sql)
	conn.commit()

	# Get dimensionality
	global n
	n = int(input("Dimensionality? "))

	# Get length of Nodes
	len_nodes = 2 ** n
	print("Number of Nodes is", len_nodes)

	# Insert values to Nodes
	nodes = []
	for index in range(len_nodes):
		node = {
			"id": padded_bin(index, n),
			"relation": []
		}
		nodes.append(node)

	loop_len = len_nodes
	while loop_len:
		for pnt in range(len_nodes - loop_len, len_nodes):
			main_node_index = len_nodes - loop_len
			same_binaries = [i for i in range(n) if nodes[main_node_index]["id"][i] != nodes[pnt]["id"][i]]
			if len(same_binaries) is 1:
				if not nodes[pnt]["id"] in nodes[main_node_index]["relation"]:
					nodes[main_node_index]["relation"].append(nodes[pnt]["id"])
				if not nodes[main_node_index]["id"] in nodes[pnt]["relation"]:
					nodes[pnt]["relation"].append(nodes[main_node_index]["id"])
		loop_len = loop_len - 1

	# Nodes
	print("=== nodes ===", nodes)

	for node in nodes:
		sql = "INSERT INTO nodes(binary_id, relation, status) VALUES(?, ?, ?)"
		relations = ""
		for relation in node["relation"]:
			relations += relation + ","
		relations = relations[:-1]
		cur.execute(sql, (node["id"], relations, 1))
		conn.commit()

def goal2():
	sql = "DELETE FROM `node` WHERE 1=1"
	cur.execute(sql)
	conn.commit()

	# Run nodes
	sql = "SELECT * FROM `nodes` WHERE 1=1"
	cur.execute(sql)
	nodes = cur.fetchall()

	if len(nodes) is 0:
		print("Not produced Goal 1. Please try it first.")
	else:
		global m
		m = int(input("Files produced? "))
		while m >= n:
			print("It should be less than " + str(n))
			m = int(input("Files produced? "))

		for node in nodes:
			node_run(node[1], 2, n, m, "no key")

def id_generator(size, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def goal3():
	sql = "SELECT * FROM `nodes` WHERE 1=1"
	cur.execute(sql)
	nodes = cur.fetchall()

	p = random.randint(1, m)
	for iloop in range(p):
		key_text = id_generator(n)
		key_id = ''
		key_id_sum = 0
		for i in range(len(key_text)):
			key_id_sum += ord(key_text[i])
		key_id = padded_bin(key_id_sum % (2 ** n), n)

		for node in nodes:
			node_run(node[1], 3, n, m, key_id)

def goal4():
	key_text = id_generator(n)
	key_id = ''
	key_id_sum = 0
	for i in range(len(key_text)):
		key_id_sum += ord(key_text[i])
	key_id = padded_bin(key_id_sum % (2 ** n), n)

	sql = "SELECT * from `nodes` WHERE `binary_id`='" + str(key_id) + "'"
	cur.execute(sql)
	remove_node = cur.fetchone()
	remove_pid = int(remove_node[4])
	sql = "DELETE FROM `nodes` WHERE `binary_id`=" + str(key_id)
	cur.execute(sql)
	conn.commit()

	os.kill(remove_pid, signal.SIGINT)

# Get goal
while True:
	goal = int(input("1: Create nodes\n2: Generate files in each node\n3: Search random file\n4: Remove random file\n" +
						"What is your goal?"))
	if goal is 1:
		goal1()
	elif goal is 2:
		if n is 0:
			print("Not executed goal 1.")
		else:
			goal2()
	elif goal is 3:
		if n is 0 or m is 0:
			print("Not executed goal 1 and goal 2.")
		else:
			goal3()
	elif goal is 4:
		if n is 0 or m is 0:
			print("Not executed goal 1 and goal 2.")
		else:
			goal4()

conn.close()