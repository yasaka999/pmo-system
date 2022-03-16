# use sqlite
create table user(id int, name text, email text, passwd text, last_modified real)

def main():
    import sqlite3
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('select * from user')
    values = cursor.fetchall()
    print(values)
    cursor.close()
    conn.close()

main()  