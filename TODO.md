# Movie Recommender System - Integration Plan

## Issues Found:
1. Duplicate Flask apps (app.py and api/index.py)
2. Duplicate stylesheets (static/ and style/)
3. Duplicate view directories (templates/ and views/)
4. Vercel config pointing to wrong paths
5. Node.js config in Python Flask project

## Tasks Completed: ✅
- [x] Create unified api/index.py with template/static path fix
- [x] Update vercel.json for correct API path
- [x] Clean up package.json (removed Node.js scripts)
- [x] Remove duplicate views/ directory
- [x] Update start.sh script
- [x] Test the application - ALL ROUTES WORKING

## Project Structure (Cleaned):
```
Updated-Movie-Recommender/
├── api/
│   └── index.py          # Main Flask app (Vercel compatible)
├── static/
│   └── styles.css        # Styles
├── templates/
│   ├── index.html        # Home page
│   ├── recommendations.html
│   ├── popular.html
│   ├── browse.html
│   └── error.html
├── u.data                # Ratings data
├── Movie_Id_Titles      # Movie titles
├── movie_recommender_system.py
├── requirements.txt
├── vercel.json          # Vercel config (updated)
├── package.json         # Cleaned
└── start.sh             # Startup script
```

## Running the App:
```bash
# Local development
python3 api/index.py

# App runs at: http://127.0.0.1:8000

# API endpoint
curl "http://127.0.0.1:8000/api/recommend?movie=Star%20Wars%20(1977)"
```

