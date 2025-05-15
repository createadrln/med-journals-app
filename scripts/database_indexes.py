import sqlite3

conn = sqlite3.connect('/app/databases/CovidData.db')
cursor = conn.cursor()

add_research_table_id_index = "CREATE INDEX idx_id ON covid_research (id);"
add_research_table_source_index = "CREATE INDEX idx_source ON covid_research (source);"
add_research_table_date_index = "CREATE INDEX idx_date ON covid_research (pub_date);"

cursor.execute(add_research_table_id_index)
cursor.execute(add_research_table_source_index)
cursor.execute(add_research_table_date_index)

conn.commit()
conn.close()
