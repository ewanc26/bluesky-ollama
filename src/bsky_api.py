from atproto import IdResolver, Client
import os
import logging

# Ensure the log directory exists
log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Set up logging to a file in the log directory
logging.basicConfig(
    filename=os.path.join(log_directory, 'general.log'), 
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def login(handle_env_var, app_pass_env_var):
    """Login to Bluesky account using environment variables."""
    try:
        handle = os.getenv(handle_env_var)
        app_pass = os.getenv(app_pass_env_var)
        host_url = os.getenv("BSKY_HOST_URL", "https://bsky.social")

        client = Client(host_url)

        if not handle or not app_pass:
            logging.error("Handle or app password missing in environment variables.")
            raise ValueError("Handle or app password missing in environment variables")

        logging.debug("Attempting to log in with handle: %s", handle)
        client.login(handle, app_pass)

        logging.info("Login successful for handle: %s", handle)
        return client
    
    except Exception as e:
        logging.exception("An error occurred during login: %s", e)
        quit(1)

def DID_resolve(handle):
    """Resolve DID (Decentralized Identifier) for a given handle."""
    try:
        logging.debug("Resolving DID for handle: %s", handle)
        resolver = IdResolver()
        did = resolver.handle.resolve(handle)
        logging.debug("Resolved DID: %s", did)

        did_doc = resolver.did.resolve(did)
        logging.debug("Resolved DID Document: %s", did_doc)

        package = {"did": did, "did_doc": did_doc}
        logging.info("Successfully resolved DID and DID Document.")

        return package

    except Exception as e:
        logging.exception("An error occurred while resolving DID: %s", e)
        return None

def retrieve_posts(client, client_did, limit=100):
    """Retrieve posts from a Bluesky account with pagination."""
    post_list = []
    has_more = True
    cursor = None

    logging.info(f"Starting to retrieve posts for client ID: {client_did}")

    while has_more:
        try:
            # Use cursor for pagination
            if cursor:
                data = client.app.bsky.feed.post.list(client_did, limit=limit, cursor=cursor)
            else:
                data = client.app.bsky.feed.post.list(client_did, limit=limit)

            logging.debug(f"Fetched data with cursor: {cursor}")

            # Check for the correct attribute containing the posts
            if not hasattr(data, 'records') or not data.records:
                logging.info("No more posts found or 'records' attribute is missing.")
                break

            # Fetch posts from the 'records' attribute
            posts = data.records

            # Add the posts to the post_list
            post_list.extend(posts.values())

            logging.info(f"Retrieved {len(posts)} posts.")

            # Get the next cursor for pagination
            cursor = data.cursor
            has_more = bool(cursor)

        except Exception as e:
            logging.error(f"Error fetching posts: {e}")
            break

    logging.info(f"Completed retrieval of posts for client ID: {client_did}. Total posts retrieved: {len(post_list)}")

    return post_list
