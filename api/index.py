"""
Movie Recommender System - Vercel Serverless API
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# Global variables
_df = None
_moviemat = None
_ratings = None
_data_loaded = False

def load_data():
    """Load data on startup"""
    global _df, _moviemat, _ratings, _data_loaded
    
    if _data_loaded:
        return True
    
    try:
        # Get the root directory (where u.data and Movie_Id_Titles are)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load ratings
        columns_names = ['user_id', 'item_id', 'rating', 'timestamp']
        _df = pd.read_csv(os.path.join(base_path, "u.data"), sep='\t', names=columns_names)
        
        # Load movie titles
        movie_titles = pd.read_csv(os.path.join(base_path, 'Movie_Id_Titles'))
        
        # Merge
        _df = pd.merge(_df, movie_titles, on='item_id')
        
        # Create ratings summary
        _ratings = pd.DataFrame(_df.groupby('title')['rating'].mean())
        _ratings['num of ratings'] = _df.groupby('title')['rating'].count()
        
        # Create pivot table
        _moviemat = _df.pivot_table(index='user_id', columns='title', values='rating')
        
        _data_loaded = True
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def get_similar_movies(movie_title, min_ratings=100):
    """Find movies similar to the given movie"""
    try:
        movie_ratings = _moviemat[movie_title]
        similar = _moviemat.corrwith(movie_ratings)
        
        corr = pd.DataFrame(similar, columns=['Correlation'])
        corr.dropna(inplace=True)
        corr = corr.join(_ratings['num of ratings'])
        
        recommendations = corr[corr['num of ratings'] >= min_ratings]
        recommendations = recommendations.sort_values('Correlation', ascending=False)
        
        return recommendations
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_recommendations_for_movie(movie_title, n=10):
    """Get top N similar movies"""
    similar = get_similar_movies(movie_title)
    if similar is not None:
        return similar.head(n)
    return None

def get_popular_movies(n=20):
    """Get most popular movies"""
    popular = _ratings.sort_values('num of ratings', ascending=False).head(n)
    return popular

def get_all_movies():
    """Get list of all movies for dropdown"""
    return sorted(_ratings.index.tolist())

# Load data when module loads
load_data()

@app.route('/')
def index():
    """Home page"""
    popular = get_popular_movies(10)
    popular_list = []
    for movie, row in popular.iterrows():
        popular_list.append({
            'title': movie,
            'rating': round(row['rating'], 2),
            'num_ratings': int(row['num of ratings'])
        })
    return render_template('index.html', popular=popular_list, movies=get_all_movies())

@app.route('/recommend', methods=['POST'])
def recommend():
    """Get recommendations based on movie selection"""
    movie = request.form.get('movie')
    n = int(request.form.get('n', 10))
    
    if not movie:
        return render_template('error.html', message="Please select a movie")
    
    recommendations = get_recommendations_for_movie(movie, n)
    
    if recommendations is None or recommendations.empty:
        return render_template('error.html', message="No recommendations found")
    
    rec_list = []
    for movie_title, row in recommendations.iterrows():
        rec_list.append({
            'title': movie_title,
            'correlation': round(row['Correlation'], 4),
            'num_ratings': int(row['num of ratings'])
        })
    
    return render_template('recommendations.html', 
                         original_movie=movie, 
                         recommendations=rec_list)

@app.route('/popular')
def popular_movies():
    """Show popular movies page"""
    popular = get_popular_movies(30)
    popular_list = []
    for movie, row in popular.iterrows():
        popular_list.append({
            'title': movie,
            'rating': round(row['rating'], 2),
            'num_ratings': int(row['num of ratings'])
        })
    return render_template('popular.html', movies=popular_list)

@app.route('/browse')
def browse_movies():
    """Browse all movies"""
    movies = []
    for movie, row in _ratings.iterrows():
        movies.append({
            'title': movie,
            'rating': round(row['rating'], 2),
            'num_ratings': int(row['num of ratings'])
        })
    return render_template('browse.html', movies=movies)

@app.route('/api/recommend')
def api_recommend():
    """API endpoint for recommendations"""
    movie = request.args.get('movie')
    n = int(request.args.get('n', 10))
    
    if not movie:
        return jsonify({'error': 'Please provide a movie name'})
    
    recommendations = get_recommendations_for_movie(movie, n)
    
    if recommendations is None or recommendations.empty:
        return jsonify({'error': 'No recommendations found'})
    
    result = []
    for movie_title, row in recommendations.iterrows():
        result.append({
            'title': movie_title,
            'correlation': round(row['Correlation'], 4),
            'num_ratings': int(row['num of ratings'])
        })
    
    return jsonify({
        'movie': movie,
        'recommendations': result
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(os.path.join(base_path, 'static'), filename)

# For local development
if __name__ == '__main__':
    print("\n" + "="*50)
    print("MOVIE RECOMMENDER SYSTEM")
    print("="*50)
    print("\nServer running at: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

