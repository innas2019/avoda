import sys
from avoda import create_app
if __name__ == "__main__":
    app = create_app()
    app_context = app.app_context()
    app_context.push() 
    from avoda.sendnews import send_news
    app.logger.info("mail send start")
    first=1
    if len(sys.argv)>1:
      first = int(sys.argv[1])
    send_news(False,first) 