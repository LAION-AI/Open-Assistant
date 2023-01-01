# This file loops through compressed json tweet data, pre-processes them,
# and then extracts them into more unified parquet files that can be handed
# off for further processing. The main focus is on producing viable replies.

# Initial data exploration seems that there is no guarantee that the original
# tweets are in the archive, so we might need to extract suitable replies
# then get the original tweets separately, and then combine them into a
# suitable thread format that can be used by our instruction model.

# This assumes data downloaded from https://archive.org/details/twitterstream
# and that the internal .tar files are extracted locally.
# They are large files so using something like 7Zip or WinRar migth be easier
# than putting all of it in scripts, but it is a possibility.

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from tqdm import tqdm

#TODO: OPTIONAL - Put the Untar process in a script instead of doing that part externally. Twitterstream archives are .tar with folders and json.gz files inside.
#TODO: Set up list of important hashtags & keywords. This might have to be done after we get the original tweets in a separate file.
#TODO: Process data and filter based on hashtags & keywords
#TODO: Determine output format and location. CSV, JSON, etc.

# Sets up paths
#TODO: Source paths from env file
path_string = "PUT THE PATH HERE TO WHERE YOU DOWNLOADED AND EXTRACTED THE ARCHIVE .TAR"
folder_path = Path(path_string)
file_list_pkl = folder_path / "file_list.pkl"
processed_file_list_pkl = folder_path / "processed_file_list.pkl"

#For the processed folder to save inside, we can create the directory if it doesn't exist
processed_folder_path = folder_path / "processed"
processed_folder_path.mkdir(parents=True, exist_ok=True)

# Set max buffer to store temporary dataframes for processing
# Change this depending on the memory of your computer
processed_max_buffer = 512

# Set up list of wanted column names.
# Note: User columns are prefixed with user_
wanted_cols = ["created_at",
               "timestamp_ms",
               "id",
               "id_str",
               "text",
               "truncated",
               "in_reply_to_status_id",
               "in_reply_to_user_id",
               "is_quote_status",
               "quote_count",
               "reply_count",
               "retweet_count",
               "favorite_count",
               "filter_level",
               "lang",
               "possibly_sensitive",
               "hashtags",
               "urls",
               "symbols",
               "user_id",
               "user_id_str",
               "user_verified",
               "user_followers_count",
               "user_statuses_count"]

def main(file_list_pkl,folder_path,wanted_cols,processed_max_buffer,processed_file_list_pkl,processed_folder_path):
    """
    Runs the main processing script to get files, loop through them, and process them.
    Outputs larger json.gz files made by concat the pre-filtered dataframes from
    the original json.gz files.
    """
    
    file_list = get_file_paths(file_list_pkl,folder_path)
    
    process_file_list(file_list,wanted_cols,processed_max_buffer,processed_file_list_pkl,processed_folder_path)
    
    print("Done")

def get_file_paths(file_list_pkl,folder_path):
    """
    Gets the file paths by recursively checking the folder structure.
    # Based on code from stackoverflow https://stackoverflow.com/questions/26835477/pickle-load-variable-if-exists-or-create-and-save-it
    """
    try:
        allpaths = pickle.load(open(file_list_pkl, "rb"))
    except (OSError, IOError) as e:
        allpaths = sorted(list(folder_path.rglob('*.[gz bz2]*')))
        pickle.dump(allpaths, open(file_list_pkl, "wb"))
    print("Got file paths.")
    return allpaths

def process_file_list(file_list,wanted_cols,processed_max_buffer,processed_file_list_pkl,processed_folder_path):
    """
    Loops through the json.gz files in the file list,
    processes them, and stores them into a unified file.
    
    This reduces the io time of opening the thousands small files.
    Furthermore, we need more tweets together to help find any conversation threads.
    
    We might want to consider different storage formats, or db usage.
    """
    
    # Gets processed file list if stored, if not, creates it.
    try:
        processed_list = pickle.load(open(processed_file_list_pkl , "rb"))
    except (OSError, IOError) as e:
        processed_list=[]
        pickle.dump(processed_list, open(processed_file_list_pkl , "wb"))
        
    # Concating 1 by 1 is not very efficient. We can store a few dataframes and concat them all at once.
    # How many we can keep in the df_list depends on our computer memory
    df_list = []
    
    # Stores temporary processed file names, but before saving to pkl
    temp_processed_list = []
    
    # Loop through file list
    for i, file in enumerate(tqdm(file_list)):
        # Only process file if it hasn't been processed already
        if file not in processed_list:
            filter_df = filter_dataframe(process_json(file,wanted_cols))
            
            # Keep track of what file we just processed
            df_list.append(filter_df)
            temp_processed_list.append(file)
            
            # If we have stored the max amount of dataframes in our specified buffer, combine them, and store them.
            if len(temp_processed_list) == processed_max_buffer:
                # Call function to combine dataframes, export it, and update processed list
                combine_df_list(df_list,i,processed_folder_path,processed_list,temp_processed_list,processed_file_list_pkl)
                
                # Reset reference lists
                df_list = []
                temp_processed_list = []
                
    # If loop is done, process the remaining files
    combine_df_list(df_list,len(file_list),processed_folder_path,processed_list,temp_processed_list,processed_file_list_pkl)
    
    print("Processing completed")
    
                
                
                
def combine_df_list(df_list,file_number,processed_folder_path,processed_list,temp_processed_list,processed_file_list_pkl):
    """
    Combines the temporary list of processed dataframes into one larger dataframe,
    then exports it to its own json file. Having larger files reduces
    IO time for opening small files.
    
    Also updates the processed list pkl
    """
    # Combine the dataframes in the buffer and save it
    combined_df = pd.concat(df_list)
    combined_df_filename = f"processed_{file_number}.parquet"
    combined_df_path = processed_folder_path / combined_df_filename
    combined_df.to_parquet(combined_df_path)

    # Update our processed list
    processed_list.extend(temp_processed_list)
    pickle.dump(processed_list, open(processed_file_list_pkl , "wb"))
    
    print(f"Processed up to file #: {file_number} . Saved file: {combined_df_filename}")
            

def process_json(json_path,wanted_cols):
    """
    Loads a json.gz file into a pandas dataframe,
    normalizes user and entity rows into their own columns,
    concats them back into one dataframe, and then returns the
    dataframe with only the wanted columns.
    """
    
    # Get main df
    df = pd.read_json(json_path, lines=True)

    # Normalize User Data
    user_df = pd.json_normalize(df.user)
    user_df.columns = ["user_" + str(col) for col in user_df.columns]

    # Concat dataframes
    df = pd.concat([df,pd.json_normalize(df.entities),user_df],axis=1)
    
    #Take wanted columns
    df = df[wanted_cols]
    
    return df

def filter_dataframe(df):
    """
    Takes in a dataframe that is processed via process_json,
    and applies some filters to reduce the search space.
    
    Current filters:
    - Reply count should be greater than 0 or should be a reply to something else.
    - Should not include truncated text.
    
    Potential future filters:
    - Lang = English only
    - Filter only for specific keywords or hashtags suitable for instruction / prompts
    - Only look at tweets from high follower count, favorites, etc.
    """
    
    # FIlter dataframe for tweets that aren't truncated, and either are in response to a tweet or have some replies.
    filter_df = df[((df["reply_count"] > 0) | (df["in_reply_to_status_id"].notnull())) & (df["truncated"] == False)]
    
    return filter_df


if __name__ == "__main__":
    main(file_list_pkl,folder_path,wanted_cols,processed_max_buffer,processed_file_list_pkl,processed_folder_path)