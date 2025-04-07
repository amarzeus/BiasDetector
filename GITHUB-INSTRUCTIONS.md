# GitHub Deployment Instructions for BiasDetector

## Latest Update (April 7, 2025)
This update includes:
- Enhanced NLTK data loading with robust fallback mechanisms for sentence tokenization
- Improved error handling for OpenAI API quota exceeded errors with detailed user feedback
- Expanded the "Generate New Article" feature with more article types including healthcare category
- Significantly improved UI with better styling, contrast, and visibility for bias categories and headers

## Available ZIP Files
Two ZIP files have been created for your convenience:
1. `BiasDetector.zip` - Contains only the extension code for Chrome Web Store distribution
2. `BiasDetector_complete.zip` - Contains the entire project including backend, extension, and website

## Option 1: Push Code Using Git (Recommended)

1. Clone the repository locally:
   ```
   git clone https://github.com/amarzeus/BiasDetector.git
   ```

2. Copy all files from the extracted ZIP file to your local repository folder.
   
3. Add and commit the changes:
   ```
   cd BiasDetector
   git add .
   git commit -m "Update with improved NLTK fallbacks, enhanced error handling, and new healthcare category"
   ```

4. Push the changes to GitHub:
   ```
   git push origin main
   ```

## Option 2: Upload Files Through GitHub Web Interface

1. Go to https://github.com/amarzeus/BiasDetector
   
2. Download either `BiasDetector.zip` (extension only) or `BiasDetector_complete.zip` (full project) from this Replit project.
   
3. Extract the files from the zip archive.
   
4. For each file or folder, upload through the GitHub web interface:
   - Click "Add file" > "Upload files"
   - Drag and drop the files (note: you can only upload entire folders at once if using Chrome)
   - Add a commit message like "Update with improved NLTK fallbacks, enhanced error handling, and new healthcare category"
   - Click "Commit changes"

## Option 3: Create a New Repository (For a clean start)
If you want to create a fresh repository with the latest code:
1. Create a new repository on GitHub
2. Extract the ZIP file on your local machine
3. Initialize a new Git repository in the extracted folder:
   ```
   git init
   git add -A
   git commit -m "Initial commit with BiasDetector"
   ```
4. Connect to your new GitHub repository:
   ```
   git remote add origin https://github.com/yourusername/new-repository-name.git
   git push -u origin main
   ```

## Key Files Updated in This Version

The following key files have been enhanced:

1. `backend/ai_processor.py`:
   - Added more robust fallback mechanisms when OpenAI API quota is exceeded
   - Enhanced simulation of article analysis with more detailed bias categories
   - Improved rewriting algorithm with more balanced language

2. `backend/bias_detector.py`:
   - Further improved NLTK data loading with additional fallback mechanisms
   - Enhanced tokenization with better handling of complex text structures
   - Added more comprehensive error handling for all language processing functions

3. `backend/app.py`:
   - Expanded "Generate New Article" feature with more article types including healthcare
   - Added more demo article templates for testing different bias types

4. `extension/content.js` and `extension/popup.js`:
   - Improved UI styling for better visibility of bias categories
   - Enhanced contrast for better readability
   - Fixed tab navigation and header styling

## Testing Your Deployment

After pushing the code to GitHub, you can:

1. Clone it to a new environment
2. Install the requirements: `pip install -r requirements.txt`
3. Run the application: `python main.py`
4. Test the demo mode without an API key
5. Test with a valid OpenAI API key if available

The application continues to operate in two modes:
- Full Mode: Uses the OpenAI API when a valid key is provided (gpt-4o model)
- Demo Mode: Shows realistic simulated results using the article text (no API key needed)