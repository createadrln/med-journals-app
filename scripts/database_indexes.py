import sqlite3

conn = sqlite3.connect('/app/databases/CovidData.db')
cursor = conn.cursor()

add_research_table_indexes = """
    CREATE INDEX idx_id ON covid_research (id);
    CREATE INDEX idx_source ON covid_research (source);
    CREATE INDEX idx_date ON covid_research (pub_date);
"""

cursor.execute(add_research_table_indexes)

conn.commit()
conn.close()
