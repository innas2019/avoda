from avoda import create_app,db

if __name__ == "__main__":
    app = create_app()
    app_context = app.app_context()
    app_context.push() 
    from avoda.sendnews import mix_post
    app.logger.info("mix start")
    
    mix_post(False)