To run the database use the following command 

Postgresql set up 
<pre>
rm -rf migrations
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
</pre>