import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from sklearn.neighbors import NearestNeighbors

# Sample dataset
data = {
    'song_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'title': ['Song A', 'Song B', 'Song C', 'Song D', 'Song E', 'Song F', 'Song G', 'Song H', 'Song I', 'Song J'],
    'genre': ['Rock', 'Rock', 'Pop', 'Pop', 'Jazz', 'Jazz', 'Classical', 'Classical', 'Hip-Hop', 'Hip-Hop']
}

# Create a DataFrame
df = pd.DataFrame(data)

# Convert genre to numerical values
genre_mapping = {genre: idx for idx, genre in enumerate(df['genre'].unique())}
df['genre_id'] = df['genre'].map(genre_mapping)

# Prepare the feature matrix
X = df[['genre_id']]

# Instantiate the model
knn = NearestNeighbors(n_neighbors=3, algorithm='auto', metric='euclidean', n_jobs=None)
knn.fit(X)

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# YouTube API key (replace with your actual API key)
YOUTUBE_API_KEY = "AIzaSyCHXk4VYfSlsZr64_wdrXppi8JaFgYb_V8"

# YouTube Data API service object
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def recommend_songs(genre, df, genre_mapping, knn):
    if genre not in genre_mapping:
        return []

    genre_id = genre_mapping[genre]
    distances, indices = knn.kneighbors([[genre_id]])

    recommended_songs = df.iloc[indices[0]]['title'].tolist()

    # Fetch YouTube video titles based on recommended songs
    video_titles = []
    for song_title in recommended_songs:
        try:
            # Search for videos related to the song title
            search_response = youtube.search().list(
                q=song_title,
                part='snippet',
                type='video',
                maxResults=1
            ).execute()

            # Extract title of the first video
            if 'items' in search_response and len(search_response['items']) > 0:
                video_titles.append(search_response['items'][0]['snippet']['title'])
            else:
                video_titles.append(f"No video found for {song_title}")

        except HttpError as e:
            print(f"Error fetching YouTube data: {e}")

    return video_titles


def on_recommend():
    genre = genre_var.get()
    recommended_songs = recommend_songs(genre, df, genre_mapping, knn)

    if recommended_songs:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Recommended songs for genre '{genre}':\n")
        for video_title in recommended_songs:
            result_text.insert(tk.END, f"{video_title}\n")
    else:
        messagebox.showwarning("No Recommendations", f"No songs found for genre '{genre}'.")



def on_reset():
    genre_var.set(df['genre'].iloc[0])
    result_text.delete(1.0, tk.END)

# Create the main window
root = tk.Tk()
root.title("Music Recommendation System")

# Create a frame for inputs
input_frame = tk.Frame(root, padx=20, pady=20)
input_frame.pack()

# Label and dropdown for genre selection
tk.Label(input_frame, text="Select Genre:").grid(row=0, column=0, padx=10, pady=10)
genre_var = tk.StringVar()
genre_dropdown = ttk.Combobox(input_frame, textvariable=genre_var, values=df['genre'].unique())
genre_dropdown.grid(row=0, column=1, padx=10, pady=10)
genre_dropdown.current(0)  # Set default selection

# Button to recommend songs
recommend_button = tk.Button(input_frame, text="Recommend Songs", command=on_recommend)
recommend_button.grid(row=1, column=0, columnspan=2, pady=10)

# Button to reset
reset_button = tk.Button(input_frame, text="Reset", command=on_reset)
reset_button.grid(row=2, column=0, columnspan=2, pady=10)

# Create a frame for output
output_frame = tk.Frame(root, padx=20, pady=20)
output_frame.pack()

# Text widget for displaying recommendations
result_text = tk.Text(output_frame, height=10, width=50, wrap=tk.WORD)
result_text.pack()

# Functionality to handle clearing and resetting the GUI
def clear_output():
    result_text.delete(1.0, tk.END)

# Menu Bar
menubar = tk.Menu(root)
root.config(menu=menubar)

# File Menu
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Clear Output", command=clear_output)

# Debug print statements
print("Before mainloop")  
root.mainloop()
print("After mainloop")

