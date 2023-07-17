from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

def create_table_and_function(db_uri: str) -> None:
    try:
        engine = create_engine(db_uri)
        metadata = MetaData()


        # Define the table
        stories = Table(
            'stories',
            metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('author_name', Text, nullable=True),
            Column('author_email', Text, nullable=True),
            Column('author_age', Integer, nullable=True),
            Column('story_name', Text, nullable=True),
        )

        # Create the table
        metadata.create_all(engine)

        # Define the function
        get_user_by_email_func = text("""
            CREATE OR REPLACE FUNCTION get_story_by_email(author_email_param text)
            RETURNS SETOF stories AS $$
            BEGIN
                RETURN QUERY SELECT * FROM stories WHERE stories.author_email = author_email_param;
            END $$ LANGUAGE plpgsql;

        """)

        # Create the function
        with engine.begin() as connection:
            connection.execute(get_user_by_email_func)

    except Exception as e:
        raise
