"""
Movie Recommender System - Vercel Serverless API
"""
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
import sys

app = Flask(__name__)

# Global cache - NOT loaded during import
_DATA_CACHE = None

def get_base_path():
    """Get base path that works in Vercel"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_data():
    """Lazy load data - called only when needed"""
    global _DATA_CACHE
    
    # Return error marker if previously failed
    if _DATA_CACHE == "ERROR":
        return None
    
    # Already loaded successfully
    if isinstance(_DATA_CACHE, dict) and 'ratings' in _DATA_CACHE:
        return _DATA_CACHE
    
    # Load data
    try:
        base_path = get_base_path()
        
        columns_names = ['user_id', 'item_id', 'rating', 'timestamp']
        df = pd.read_csv(os.path.join(base_path, "u.data"), sep='\t', names=columns_names)
        movie_titles = pd.read_csv(os.path.join(base_path, 'Movie_Id_Titles'))
        
        df = pd.merge(df, movie_titles, on='item_id')
        
        ratings = pd.DataFrame(df.groupby('title')['rating'].mean())
        ratings['num of ratings'] = df.groupby('title')['rating'].count()
        
        moviemat = df.pivot_table(index='user_id', columns='title', values='rating')
        
        _DATA_CACHE = {
            'df': df,
            'ratings': ratings,
            'moviemat': moviemat
        }
        
        return _DATA_CACHE
    except Exception as e:
        print(f"DATA LOAD ERROR: {e}", file=sys.stderr)
        _DATA_CACHE = "ERROR"
        return None

def get_similar_movies(movie_title, min_ratings=100):
    """Find similar movies"""
    data = get_data()
    if data is None:
        return None
    
    moviemat = data['moviemat']
    ratings = data['ratings']
    
    try:
        movie_ratings = moviemat[movie_title]
        similar = moviemat.corrwith(movie_ratings)
        
        corr = pd.DataFrame(similar, columns=['Correlation'])
        corr.dropna(inplace=True)
        corr = corr.join(ratings['num of ratings'])
        
        recommendations = corr[corr['num of ratings'] >= min_ratings]
        recommendations = recommendations.sort_values('Correlation', ascending=False)
        
        return recommendations
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def get_recommendations_for_movie(movie_title, n=10):
    """Get top N similar movies"""
    similar = get_similar_movies(movie_title)
    if similar is not None:
        return similar.head(n)
    return None

def get_popular_movies(n=20):
    """Get most popular movies"""
    data = get_data()
    if data is None:
        return None
    return data['ratings'].sort_values('num of ratings', ascending=False).head(n)

def get_all_movies():
    """Get list of all movies"""
    data = get_data()
    if data is None:
        return []
    return sorted(data['ratings'].index.tolist())

# ============== ROUTES ==============

@app.route('/')
def index():
    """Home page"""
    data = get_data()
    if data is None:
        return jsonify({'error': 'Failed to load movie data'}), 500
    
    popular = get_popular_movies(10)
    if popular is None:
        return jsonify({'error': 'Failed to get popular movies'}), 500
    
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
    """Get recommendations"""
    data = get_data()
    if data is None:
        return jsonify({'error': 'Failed to load movie data'}), 500
    
    movie = request.form.get('movie')
    n = int(request.form.get('n', 10))
    
    if not movie:
        return render_template('error.html', message="Please select a movie"), 400
    
    recommendations = get_recommendations_for_movie(movie, n)
    
    if recommendations is None or recommendations.empty:
        return render_template('error.html', message="No recommendations found"), 404
    
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

@app.route('/api/recommend')
def api_recommend():
    """API endpoint"""
    data = get_data()
    if data is None:
        return jsonify({'error': 'Failed to load movie data'}), 500
    
    movie = request.args.get('movie')
    n = int(request.args.get('n', 10))
    
    if not movie:
        return jsonify({'error': 'Please provide a movie name'}), 400
    
    recommendations = get_recommendations_for_movie(movie, n)
    
    if recommendations is None or recommendations.empty:
        return jsonify({'error': 'No recommendations found'}), 404
    
    result = []
    for movie_title, row in recommendations.iterrows():
        result.append({
            'title': movie_title,
            'correlation': round(row['Correlation'], 4),
            'num_ratings': int(row['num of ratings'])
        })
    
    return jsonify({'movie': movie, 'recommendations': result})

@app.route('/popular')
def popular_movies():
    """Popular movies page"""
    data = get_data()
    if data is None:
        return jsonify({'error': 'Failed to load movie data'}), 500
    
    popular = get_popular_movies(30)
    if popular is None:
        return jsonify({'error': 'Failed to get popular movies'}), 500
    
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
    data = get_data()
    if data is None:
        return jsonify({'error': 'Failed to load movie data'}), 500
    
    ratings = data['ratings']
    movies = []
    for movie, row in ratings.iterrows():
        movies.append({
            'title': movie,
            'rating': round(row['rating'], 2),
            'num_ratings': int(row['num of ratings'])
        })
    
    return render_template('browse.html', movies=movies)

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message="Internal server error"), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', message="Page not found"), 404

# ============== VERCEL HANDLER ==============

def handler(request, context=None):
    """Vercel serverless entrypoint"""
    return app(request.environ, lambda status, headers: None)

