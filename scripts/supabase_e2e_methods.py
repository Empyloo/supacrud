# Path: scripts/local_supabase_e2e.py
import logging

from supacrud import Supabase

logger = logging.getLogger(__name__)

NAME = "John Doe"
EMAIL = "john.doe@example.com"
STORY = "The Tale of John Doe"
AGE = 32
STORY_NAME_EDITED = "The Tale of Jane Doe And His Past."

def setup_supacrud(credentials: dict) -> Supabase:
    try:
        db = Supabase(
            credentials["supabase_url"],
            credentials["supabase_service_role_key"],
            credentials["supabase_anon_key"],
        )
        logger.info("Supabase client created")
        return db
    except Exception as e:
        logger.error("Error setting up Supabase client: %s", e)
        raise


def test_supacrud_create(db: Supabase) -> None:
    # Create operation
    user = {"author_name": NAME, "author_email": EMAIL, "author_age": AGE, "story_name": STORY}
    logger.info("Creating a story: %s", user)
    created_user = db.create("rest/v1/stories", user)
    logger.info("** Story created **: %s", created_user)


def test_supacrud_read(db: Supabase) -> str:
    # Read operation
    logger.info("Reading story with email: %s", EMAIL)
    stories = db.read("rest/v1/stories")
    logger.info("Read stories: %s", stories)
    return stories[0]["id"] 


def test_supacrud_update(db: Supabase) -> None:
    # Update operation
    story = {"author_name": NAME, "author_email": EMAIL, "author_age":  AGE, "story_name": STORY_NAME_EDITED}
    id = test_supacrud_read(db)
    logger.info("Updating story: %s", story)
    db.update(f"rest/v1/stories?id=eq.{id}", story)
    logger.info("Story updated: %s", story)


def test_supacrud_delete(db: Supabase, id: str) -> None:
    # Delete operation
    logger.info("Deleting a story with id: %s", id)
    db.delete(f"rest/v1/stories?id=eq.{id}")
    logger.info("Story deleted: %s", id)


def test_supacrud_rpc(db: Supabase) -> None:
    logger.info("Getting a story using a function by author_email")
    db.rpc("rest/v1/rpc/get_story_by_email", {"author_email_param": EMAIL})
    logger.info("Procedure get_story_by_email called")


def main_test(credentials: dict) -> bool:
    try:
        db = setup_supacrud(credentials)
        test_supacrud_create(db)
        id = test_supacrud_read(db)
        test_supacrud_update(db)
        test_supacrud_delete(db, id)
        test_supacrud_rpc(db)
        logger.info("All Supabase CRUD operations completed successfully")
        return True
    except Exception as e:
        logger.error("Error running Supabase CRUD operations: %s", e)
        return False
