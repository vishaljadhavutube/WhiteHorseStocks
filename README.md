To run the database use the following command 

To run this command you should be on project level 
<pre>
cd path/to/your/flask/project
</pre>
<pre>
source venv/bin/activate
</pre>
<pre>
pip3 install flask flask_sqlalchemy flask_wtf
</pre>
<pre>
flask shell
</pre>
<pre>
from extensions import db
db.create_all()
</pre>