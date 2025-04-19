import os
from flask import Flask
from models import db
from alembic import command
from alembic.config import Config

def create_app():
    """Create Flask application instance with database configuration"""
    app = Flask(__name__)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the app
    db.init_app(app)
    
    return app

def init_db():
    """Initialize the database tables"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")

def init_migrations():
    """Initialize Alembic migrations"""
    os.system("alembic init migrations")
    
    # Update alembic.ini with database URL
    with open('alembic.ini', 'r') as f:
        config = f.read()
    
    updated_config = config.replace(
        'sqlalchemy.url = driver://user:pass@localhost/dbname',
        f'sqlalchemy.url = {os.getenv("DATABASE_URL")}'
    )
    
    with open('alembic.ini', 'w') as f:
        f.write(updated_config)
    
    # Update env.py to import models and use SQLAlchemy metadata
    with open('migrations/env.py', 'r') as f:
        env_content = f.read()
    
    updated_env = env_content.replace(
        'from alembic import context',
        'from alembic import context\nimport os\nimport sys\nsys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))\nfrom models import db'
    ).replace(
        'target_metadata = None',
        'target_metadata = db.metadata'
    )
    
    with open('migrations/env.py', 'w') as f:
        f.write(updated_env)
    
    print("Migrations initialized successfully.")

def create_migration(message):
    """Create a new migration with the given message"""
    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message=message)
    print(f"Created migration with message: {message}")

def upgrade_db():
    """Upgrade database to the latest migration"""
    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Database upgraded to the latest migration.")

if __name__ == "__main__":
    # Create the app and database tables
    init_db()
    
    # Initialize migrations if they don't exist
    if not os.path.exists("migrations"):
        init_migrations()
        create_migration("initial")
    
    # Upgrade the database to the latest migration
    upgrade_db()