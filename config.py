class ConfigDebug():
    #SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost/Bank'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://danijel:daki_123@cbank.mysql.database.azure.com/vgcbank'
    SECRET_KEY = 'hejhej'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail SMTP server settings
    MAIL_SERVER = '127.0.0.1'
    MAIL_PORT = 1025
    MAIL_USE_SSL = False
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'email@example.com'     
    MAIL_PASSWORD = 'password'
    MAIL_DEFAULT_SENDER = '"MyApp" <noreply@example.com>'

    # Flask-User settings
    USER_APP_NAME = "c_Bank"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True        # Enable email aution
    USER_ENABLE_USERNAME = False    # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_COPYRIGHT_YEAR = 2022
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"