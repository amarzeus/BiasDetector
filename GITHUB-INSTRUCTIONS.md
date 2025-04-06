# GitHub Deployment Instructions for BiasDetector

## Option 1: Push Code Using Git (Recommended)

1. Clone the repository locally:
   ```
   git clone https://github.com/amarzeus/BiasDetector.git
   ```

2. Copy all files from this Replit project to your local repository folder.
   
3. Add and commit the changes:
   ```
   cd BiasDetector
   git add .
   git commit -m "Update with improved fallbacks for API quota and NLTK issues"
   ```

4. Push the changes to GitHub:
   ```
   git push origin main
   ```

## Option 2: Upload Files Through GitHub Web Interface

1. Go to https://github.com/amarzeus/BiasDetector
   
2. Download the BiasDetector.zip file from this Replit project.
   
3. Extract the files from the zip archive.
   
4. For each file or folder, upload through the GitHub web interface:
   - Click "Add file" > "Upload files"
   - Drag and drop the files (note: you can only upload entire folders at once if using Chrome)
   - Add a commit message like "Update with improved fallbacks for API quota and NLTK issues"
   - Click "Commit changes"

## Key Files Updated in This Version

The following key files have been enhanced:

1. `backend/ai_processor.py`:
   - Added robust fallback mechanisms when OpenAI API quota is exceeded
   - Implemented realistic article analysis simulation using article text content
   - Created intelligent rewriting with balanced language even in demo mode

2. `backend/bias_detector.py`:
   - Fixed NLTK data loading issues with automatic downloads
   - Added robust fallback for text tokenization when NLTK resources are missing
   - Enhanced error handling for all language processing functions

3. `backend/app.py`:
   - Added "Generate New Article" feature to the demo page
   - Improved demo experience with simulated analysis results

## Testing Your Deployment

After pushing the code to GitHub, you can:

1. Clone it to a new environment
2. Install the requirements: `pip install -r requirements.txt`
3. Run the application: `python main.py`
4. Test the demo mode without an API key
5. Test with a valid OpenAI API key if available

The application now operates in two modes:
- Full Mode: Uses the OpenAI API when a valid key is provided
- Demo Mode: Shows realistic simulated results using the article text