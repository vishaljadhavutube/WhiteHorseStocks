If you make any changes in the database or in tables you need to run the following command 
<pre>
flask db init
flask db migrate -m "comment for changes"
flask db upgrade
</pre>



Postgresql set up 

<pre>
#to initialize or to initialize db from scratch use following commands 
rm -rf migrations
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
</pre>

<h1>Error and solutions</h1>
ERROR [flask_migrate] Error: Can't locate revision identified by 'f34b7eaaa032'

<pre>
flask db migrate -m "your migration message"
flask db upgrade

# Verify the Alembic Version Table
psql -U yourusername -d yourdbname
SELECT * FROM alembic_version;
</pre>

