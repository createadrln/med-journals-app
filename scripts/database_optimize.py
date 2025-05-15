import sqlite3

conn = sqlite3.connect('/app/databases/CovidData.db')
cursor = conn.cursor()

analyze_query = "ANALYZE;"
vacuum_query = "VACUUM;"

cursor.execute(analyze_query)
cursor.execute(vacuum_query)

conn.commit()
conn.close()
