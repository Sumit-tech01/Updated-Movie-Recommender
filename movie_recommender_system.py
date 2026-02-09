# Movie Recommender System
# Item-based Collaborative Filtering

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style('whitegrid')

def load_data():
    """Load and prepare the movie data"""
    try:
        # Load ratings data
        columns_names = ['user_id', 'item_id', 'rating', 'timestamp']
        df = pd.read_csv("u.data", sep='\t', names=columns_names)
        print("✓ Ratings data loaded successfully")
        
        # Load movie titles
        movie_titles = pd.read_csv('Movie_Id_Titles')
        print("✓ Movie titles loaded successfully")
        
        # Merge datasets
        df = pd.merge(df, movie_titles, on='item_id')
        print("✓ Data merged successfully")
        
        return df, movie_titles
    except FileNotFoundError as e:
        print(f"✗ Error loading data: {e}")
        return None, None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None, None

def analyze_ratings(df):
    """Analyze rating patterns"""
    print("\n=== Rating Analysis ===")
    print(f"Total ratings: {len(df)}")
    print(f"Unique users: {df['user_id'].nunique()}")
    print(f"Unique movies: {df['item_id'].nunique()}")
    
    # Average ratings per movie
    ratings = pd.DataFrame(df.groupby('title')['rating'].mean())
    ratings['num of ratings'] = df.groupby('title')['rating'].count()
    
    return ratings

def create_visualizations(df, ratings, output_dir='static/plots'):
    """Create and save visualizations"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n=== Creating Visualizations ===")
    
    # Histogram of number of ratings
    plt.figure(figsize=(10, 6))
    ratings['num of ratings'].hist(bins=70)
    plt.title('Distribution of Number of Ratings')
    plt.xlabel('Number of Ratings')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/num_ratings_hist.png', dpi=100)
    plt.close()
    print("✓ Saved: num_ratings_hist.png")
    
    # Histogram of ratings
    plt.figure(figsize=(10, 6))
    ratings['rating'].hist(bins=70)
    plt.title('Distribution of Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/ratings_hist.png', dpi=100)
    plt.close()
    print("✓ Saved: ratings_hist.png")
    
    # Joint plot saved as image
    plt.figure(figsize=(10, 8))
    sns.jointplot(x='rating', y='num of ratings', data=ratings, alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/rating_jointplot.png', dpi=100)
    plt.close()
    print("✓ Saved: rating_jointplot.png")

def create_recommendation_matrix(df):
    """Create user-item rating matrix"""
    print("\n=== Creating Recommendation Matrix ===")
    moviemat = df.pivot_table(index='user_id', columns='title', values='rating')
    print(f"Matrix shape: {moviemat.shape}")
    return moviemat

def get_similar_movies(movie_title, moviemat, ratings, min_ratings=100):
    """Find movies similar to the given movie using correlation"""
    try:
        # Get user ratings for the movie
        movie_ratings = moviemat[movie_title]
        
        # Calculate correlation with all other movies
        similar = moviemat.corrwith(movie_ratings)
        
        # Create dataframe and drop NaN values
        corr = pd.DataFrame(similar, columns=['Correlation'])
        corr.dropna(inplace=True)
        
        # Add number of ratings info
        corr = corr.join(ratings['num of ratings'])
        
        # Filter by minimum ratings and sort
        recommendations = corr[corr['num of ratings'] >= min_ratings]
        recommendations = recommendations.sort_values('Correlation', ascending=False)
        
        return recommendations
    except KeyError:
        print(f"✗ Movie '{movie_title}' not found in database")
        return None
    except Exception as e:
        print(f"✗ Error finding similar movies: {e}")
        return None

def get_top_movies(ratings, n=10):
    """Get top N movies by rating and popularity"""
    # Filter movies with at least some ratings
    popular = ratings[ratings['num of ratings'] >= 50]
    
    # Sort by rating, then by popularity
    top_by_rating = popular.sort_values('rating', ascending=False).head(n)
    top_by_popularity = ratings.sort_values('num of ratings', ascending=False).head(n)
    
    return top_by_rating, top_by_popularity

def recommend_movies_for_user(user_id, moviemat, ratings, n=5):
    """Recommend movies for a specific user based on their ratings"""
    try:
        # Get user's ratings
        user_ratings = moviemat.loc[user_id].dropna()
        
        # Find movies the user hasn't rated
        unrated_movies = moviemat.columns.difference(user_ratings.index)
        
        # Calculate predicted ratings using correlation with rated movies
        predictions = {}
        for movie in unrated_movies:
            movie_ratings = moviemat[movie].dropna()
            similar_users = user_ratings.index.intersection(movie_ratings.index)
            
            if len(similar_users) >= 3:  # Need at least 3 similar users
                user_rated = user_ratings[similar_users]
                movie_rated = movie_ratings[similar_users]
                correlation = user_rated.corr(movie_rated)
                
                if not np.isnan(correlation) and abs(correlation) > 0.3:
                    predictions[movie] = correlation * user_rated.mean()
        
        # Sort and return top N predictions
        sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:n]
        return sorted_preds
    except Exception as e:
        print(f"✗ Error recommending movies for user {user_id}: {e}")
        return []

def run_analysis():
    """Main function to run complete analysis"""
    print("=" * 50)
    print("MOVIE RECOMMENDER SYSTEM - ANALYSIS")
    print("=" * 50)
    
    # Load data
    df, movie_titles = load_data()
    if df is None:
        return None, None, None
    
    # Analyze ratings
    ratings = analyze_ratings(df)
    
    # Create visualizations
    create_visualizations(df, ratings)
    
    # Create recommendation matrix
    moviemat = create_recommendation_matrix(df)
    
    # Get top movies
    print("\n=== Top Movies ===")
    top_by_rating, top_by_popularity = get_top_movies(ratings)
    print("\nTop by Rating:")
    print(top_by_rating)
    print("\nTop by Popularity:")
    print(top_by_popularity)
    
    # Example: Find similar movies to Star Wars
    print("\n=== Movies Similar to Star Wars (1977) ===")
    similar = get_similar_movies('Star Wars (1977)', moviemat, ratings)
    if similar is not None:
        print(similar.head(10))
    
    print("\n✓ Analysis complete!")
    print("✓ Visualizations saved to static/plots/")
    
    return df, moviemat, ratings

# Entry point
if __name__ == "__main__":
    run_analysis()

