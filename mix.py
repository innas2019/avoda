import random
from datetime import datetime, timezone
from avoda import create_app,db
from avoda.models import Posts
if __name__ == "__main__":
    app = create_app()
    app_context = app.app_context()
    app_context.push() 
    count = db.session.query(Posts.id).count()
    now = datetime.now(timezone.utc)
    l = app.logger
    for post in range(5):
        id=random.randint(1, count)
        try:
            newpost = db.one_or_404(db.select(Posts).where(Posts.id==id))
            newpost.updated=now
            db.session.add(newpost)
            l.info("post updated "+str(newpost.id))
        except:
            l.info("post id not exist "+str(id))  
    db.session.commit()
