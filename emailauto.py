from avoda import create_app
if __name__ == "__main__":
    app = create_app()
    app_context = app.app_context()
    app_context.push() 
    from avoda.email import send_news
    send_news(False) 