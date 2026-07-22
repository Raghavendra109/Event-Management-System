'''import sqlite3
conn=sqlite3.connect('admin.db')
data=conn.execute("SELECT * FROM admin").fetchall()
if len(data)>0:
    print("**********THE ADMINS ARE************")
    for row in data:
        print(row[0:])
else:
    print("NO SUCH RECORD FOUND")
conn.close()
'''
#TO DELETE
import sqlite3
conn=sqlite3.connect('bookings.db')
cursor=conn.cursor()
cursor.execute("delete  from  bookings")
conn.commit()
conn.close()
print("deleted")