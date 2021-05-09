from query import execute_query
from subprocess import check_output

def test_insert():
    sql_query = 'INSERT INTO users (username, password, uuid) VALUES (?, ?, ?)'
    values = ('test', 'test123', 'uid123')
    status = execute_query(sql_query, values)
    assert status == True

def test_read():
    sql_query = 'SELECT * FROM users';
    data = execute_query(sql_query, "","select","fetchall")
    assert len(data) != 0

def test_update():
    sql_query = 'UPDATE users SET uuid = ? WHERE username = ?'
    values = ('uid1234', 'test')
    status = execute_query(sql_query, values)
    assert status == True

def test_delete():
    sql_query = 'DELETE * FROM users WHERE username = ?'
    values = ('test',)
    status = execute_query(sql_query, values)
    assert status == False

def test_login():
    login_url = 'http://127.0.0.1:5000'
    value = check_output(["curl", "-s", "-o", "/dev/null" ,"-w" ,'%{http_code}', login_url])
    value = value.decode('utf8')
    assert int(value) == 200

def test_logout():
    logout_url = 'http://127.0.0.1:5000/logout'
    value = check_output(["curl", "-s", "-o", "/dev/null" ,"-w" ,'%{http_code}', logout_url])
    value = value.decode('utf8')
    assert int(value) == 302

def test_create():
    create_url = 'http://127.0.0.1:5000/create'
    value = check_output(["curl", "-s", "-o", "/dev/null" ,"-w" ,'%{http_code}', create_url])
    value = value.decode('utf8')
    assert int(value) == 302

def test_feed():
    feed_url = 'http://127.0.0.1:5000/index'
    value = check_output(["curl", "-s", "-o", "/dev/null" ,"-w" ,'%{http_code}', feed_url])
    value = value.decode('utf8')
    assert int(value) == 302