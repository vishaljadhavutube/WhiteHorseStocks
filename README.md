To run the database use the following command 

To run this command you should be on project level 
<pre>
/Users/hostname/Documents/GitHub/ShareMarketTrackerV2
</pre>


<pre>
flask shell
from extensions import db
db.create_all()
</pre>