import instaloader
import os
import time

def download_images_from_instagram():
    """
    Downloads images from an Instagram public profile using instaloader
    """
    # Instagram username to download from
    username = "grapeot"
    
    # Create a directory to store the downloaded images
    download_dir = "downloaded_images"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print(f"Created directory: {download_dir}")
    
    try:
        # Create an instance of Instaloader
        L = instaloader.Instaloader(
            dirname_pattern=download_dir,
            filename_pattern='{date_utc:%Y-%m-%d_%H-%M-%S}_{shortcode}',
            download_pictures=True,
            download_videos=False,  # Set to True if you want videos too
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        print(f"Attempting to download posts from Instagram user: {username}")
        
        # Get the profile
        profile = instaloader.Profile.from_username(L.context, username)
        print(f"Found profile: {profile.full_name} (@{profile.username})")
        print(f"Total posts: {profile.mediacount}")
        
        # Download posts
        successful_downloads = 0
        failed_downloads = 0
        
        for post in profile.get_posts():
            try:
                print(f"Downloading post {successful_downloads + 1}: {post.shortcode}")
                
                # Download the post
                L.download_post(post, target=download_dir)
                
                successful_downloads += 1
                
                # Add a small delay to be respectful to Instagram's servers
                time.sleep(1)
                
                # Optional: Limit the number of posts to download (uncomment to use)
                # if successful_downloads >= 10:  # Download only first 10 posts
                #     break
                
            except Exception as e:
                print(f"Error downloading post {post.shortcode}: {e}")
                failed_downloads += 1
        
        print(f"\nDownload completed!")
        print(f"Successfully downloaded: {successful_downloads} posts")
        print(f"Failed downloads: {failed_downloads} posts")
        print(f"Images saved to: {os.path.abspath(download_dir)}")
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile '{username}' does not exist or is private.")
    except instaloader.exceptions.ConnectionException as e:
        print(f"Connection error: {e}")
        print("This might be due to network issues or Instagram's rate limiting.")
    except instaloader.exceptions.LoginRequiredException:
        print("Error: This profile requires login to access.")
        print("You may need to log in to access this profile.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    download_images_from_instagram()
