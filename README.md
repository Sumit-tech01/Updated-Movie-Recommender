# Movie Recommender System

A web-based movie recommendation system using item-based collaborative filtering.

## Features

- 🎬 **Movie Recommendations**: Select a movie and get similar movies based on user ratings
- 📊 **Popular Movies**: Browse the most popular movies by number of ratings
- 🔍 **Browse All**: Search through all movies in the database
- 📈 **Data Analysis**: Generates visualizations of rating patterns

## Local Development

### Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Run the Analysis Script (CLI)
```bash
python3 movie_recommender_system.py
```
This will:
- Load and analyze the movie rating data
- Generate visualizations (saved to `static/plots/`)
- Display top movies and recommendations

### Run the Web Application
```bash
python3 app.py
# or
npm run server
```
Then open your browser and go to: **http://localhost:5000**

## Vercel Deployment

### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

Or connect your GitHub repository to Vercel for automatic deployments.

### Vercel Configuration

The project is configured for Vercel deployment with:
- `api/index.py` - Serverless Flask API function
- `vercel.json` - Vercel configuration
- `requirements.txt` - Python dependencies

### Vercel Deployment URL

After deployment, your app will be available at:
```
https://your-project-name.vercel.app
```

## API Endpoints

- `GET /` - Home page with search
- `POST /recommend` - Get movie recommendations
- `GET /popular` - View popular movies
- `GET /browse` - Browse all movies
- `GET /api/recommend?movie=<name>&n=<count>` - JSON API endpoint

## Project Structure

```
movie_recommender_system/
├── api/
│   └── index.py              # Vercel serverless function
├── app.py                     # Local Flask development server
├── movie_recommender_system.py # CLI analysis script
├── requirements.txt          # Python dependencies
├── package.json              # Node.js scripts
├── vercel.json              # Vercel configuration
├── README.md                # This file
├── u.data                   # Movie ratings data
├── Movie_Id_Titles          # Movie titles database
├── static/
│   ├── styles.css           # CSS styles
│   └── plots/               # Generated visualizations
└── templates/
    ├── index.html           # Home page
    ├── recommendations.html # recommendations display
    ├── popular.html         # Popular movies page
    ├── browse.html          # Browse all movies
    └── error.html           # Error page
```

## How It Works

The system uses **Item-Based Collaborative Filtering**:

1. **Data Loading**: Loads user ratings and movie information
2. **Matrix Creation**: Creates a user-item rating matrix (944 users × 1664 movies)
3. **Correlation Calculation**: For each movie pair, calculates Pearson correlation
4. **Recommendations**: Sorts movies by correlation to find similar titles

## Dataset

- **100,003 ratings** from **944 users**
- **1,682 movies** in the database
- Ratings range from 1-5 stars

## Requirements

- Python 3.7+
- Flask
- NumPy
- Pandas
- Matplotlib
- Seaborn

## License

MIT License

