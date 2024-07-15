from avoda import create_app
if __name__ == "__main__":
    app = create_app()
    app_context = app.app_context()
    app_context.push() 
    from avoda.sendnews import send_news
    app.logger.info("mail send start")
    send_news(False) 