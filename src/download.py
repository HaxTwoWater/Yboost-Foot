import os 
import urllib.request
import urllib.error

def download_csv_files(user, repo, files, folder="data",branch="main"):

    if not os.path.exists(folder):
        os.makedirs(folder)
        print("Created folder : %s" % folder)

    base_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}"

    for file in files :
        
            url_brute = f"{base_url}/{file}"
            path_folder = os.path.join(folder, os.path.basename(file))
             
            print(f"Downloading {file} ...")
            try:
                urllib.request.urlretrieve(url_brute, path_folder)
                print(f"Downloaded in : {path_folder}")
            except urllib.error.HTTPError as e:
                print(f"HTTP {e.code} for '{file}'. Check the file name.")
            except Exception as e:
                print(f"Error downloading for '{file}' : {e}")

if __name__ == "__main__":
    GITHUB_USER = "martj42"
    GITHUB_REPO = "international_results"
    BRANCH = "master"  
    FOLDER_DESTINATION = "data" 
    
    FILE_LIST = [
        "results.csv",
        "goalscorers.csv",
        "shootouts.csv"
    ]
    
    download_csv_files(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        files=FILE_LIST,
        folder=FOLDER_DESTINATION,
        branch=BRANCH
    )