# BiasDetector
## Balancing News Media

by Amar Kumar

---

## The Problem

> "I hate fake news. What I want is a translator that will take a news article and get rid of all the bias and give us objective news or a balanced editorial."
> 
> - David Blumberg, Venture Capitalist

---

## Media Bias Today

- News sources often present one-sided narratives
- Editorial boards may push specific positions without context
- Important information is frequently omitted
- Readers struggle to get balanced perspectives

---

## Example: Bush Era Economy

- **New York Times claimed**: Household income was declining under Bush
- **Wall Street Journal pointed out**: Household size was also declining
- **Missing Context**: On a per capita basis, income was actually rising

---

## Example: Historical Comparisons

- An article might state: "A hot dog cost $1 in 1920"
- **Missing Context**: What does that mean in today's inflation-adjusted dollars?
- Readers need proper context to accurately understand information

---

## Introducing BiasDetector

A Chrome extension that:
- Detects bias in news articles
- Rewrites content to present balanced viewpoints
- Shows original vs. modified content with comparisons
- Provides missing context and alternative perspectives
- Tracks bias across different news sources

---

## Key Features

1. **Bias Detection**
   - Identifies political, emotional, framing, source, factual, and omission bias
   - Rates severity on a 0-100 scale
   - Highlights specific instances in the text

2. **Content Rewriting**
   - Presents multiple perspectives
   - Uses neutral language
   - Maintains core information and flow

3. **Context Addition**
   - Adds important missing information
   - Provides historical context where relevant
   - Cites sources for added context

4. **Comparison View**
   - Side-by-side original vs. rewritten content
   - Inline changes with removed/added highlighting
   - Visual bias indicator and metrics

---

## Technical Architecture

![Architecture Diagram](https://images.unsplash.com/photo-1581092787765-e3feb951d987)

- **Chrome Extension Frontend**: HTML, CSS, JavaScript
- **Python Flask Backend**: API endpoints for analysis
- **AI Processing**: OpenAI GPT-4o for bias detection and rewriting
- **NLTK/spaCy**: For natural language processing tasks

---

## Bias Categories

1. **Political Bias**
   - Left-leaning or right-leaning rhetoric

2. **Emotional Bias**
   - Using emotional language to influence opinions

3. **Framing Bias**
   - Presenting facts selectively to promote a particular interpretation

4. **Source Bias**
   - Selective use of sources or authorities

5. **Factual Bias**
   - Presenting opinions as facts or using cherry-picked facts

6. **Omission Bias**
   - Leaving out key information that would change context

---

## Demo: Original Article

![Original Article](https://images.unsplash.com/photo-1504711434969-e33886168f5c)

"The administration's disastrous economic policies have led to skyrocketing inflation, burdening hardworking Americans. Prices have surged by 7% since last year, the highest increase in decades, proving that these reckless spending programs are failing the American people."

---

## Demo: Bias Analysis

![Bias Analysis](https://images.unsplash.com/photo-1652946619064-a12aec2d8456)

- **Bias Score**: 78/100 (High Bias)
- **Emotional Bias**: "disastrous," "skyrocketing," "burdening"
- **Political Bias**: "reckless spending programs"
- **Factual Bias**: Presenting correlation as causation
- **Omission Bias**: No mention of global inflation trends or pandemic effects

---

## Demo: Rewritten Article

![Rewritten Article](https://images.unsplash.com/photo-1622186477895-f2af6a0f5a97)

"Inflation has risen to 7% since last year, the highest increase in decades, raising concerns about the impact of economic policies. This price increase has placed financial pressure on many Americans.

Some economists attribute the inflation to government spending programs, while others point to supply chain disruptions caused by the pandemic and increased consumer demand as the economy recovers."

---

## Demo: Side-by-Side Comparison

![Comparison View](https://images.unsplash.com/photo-1542744173-05336fcc7ad4)

| Original | Rewritten |
|----------|-----------|
| "The administration's **disastrous** economic policies have led to **skyrocketing** inflation..." | "Inflation has risen to 7% since last year... raising concerns about the impact of economic policies." |
| "...proving that these **reckless spending programs** are failing the American people." | "Some economists attribute the inflation to government spending programs, while others point to supply chain disruptions..." |

---

## User Experience

- Simple browser extension interface
- One-click analysis of current article
- Tabs for analysis, rewritten content, and comparison
- In-page overlay option for seamless reading
- Recent history of analyzed articles
- Configurable settings

---

## Impact & Benefits

- **For Readers**:
  - More balanced understanding of news
  - Ability to see multiple perspectives
  - Better context for complex issues

- **For Media Literacy**:
  - Helps identify bias in trusted sources
  - Trains users to recognize bias patterns
  - Promotes critical thinking

- **For Public Discourse**:
  - Reduces polarization
  - Encourages nuanced understanding
  - Supports evidence-based discussion

---

## Long-Term Vision

1. **Bias Dashboard**
   - Track bias scores across news websites
   - Identify trends in media bias over time
   
2. **News Platform**
   - Aggregated news with bias removed
   - Multi-perspective presentation by default
   
3. **Browser Integration**
   - Native browser feature for bias detection
   - Cross-platform availability

---

## Getting Started

1. **Install the Chrome Extension**:
   - Clone the GitHub repository: `https://github.com/amarzeus/BiasDetector`
   - Load unpacked extension in Chrome

2. **Set Up the Backend**:
   - Python 3.6+ required
   - Install dependencies: Flask, OpenAI, NLTK
   - Set OpenAI API key as environment variable
   - Run the Flask server

3. **Start Analyzing**:
   - Navigate to any news article
   - Click the BiasDetector icon
   - View balanced perspectives

---

## Technical Challenges

1. **Article Extraction**
   - Diverse webpage structures
   - Paywalls and anti-scraping measures
   - Distinguishing article from comments/ads

2. **Bias Detection Accuracy**
   - Subjectivity in defining bias
   - Context-dependent interpretation
   - Domain-specific knowledge requirements

3. **Balanced Rewriting**
   - Maintaining factual accuracy
   - Preserving information density
   - Avoiding introducing new bias

---

## Future Development

1. **Expanded Language Support**
   - Multiple languages for global news coverage
   
2. **Topic-Specific Models**
   - Specialized models for politics, science, finance
   
3. **User Customization**
   - Adjustable bias sensitivity
   - Personalized focus areas
   
4. **API for Developers**
   - Integration with other news platforms
   - Developer SDK for custom applications

---

## Looking for Collaborators

- **Frontend Developers**: Improve UX/UI
- **NLP Specialists**: Enhance bias detection algorithms
- **Data Scientists**: Build bias scoring models
- **Content Experts**: Domain knowledge for specialized topics
- **UX Researchers**: Study user interaction and feedback

---

## Contact & Resources

- **GitHub**: [github.com/amarzeus/BiasDetector](https://github.com/amarzeus/BiasDetector)
- **Documentation**: Available in the repo
- **License**: MIT License
- **Contact**: [Contact information]

---

# Thank You!

Questions?

--- 

## Appendix: Implementation Details

### AI Prompt Engineering

```python
prompt = f"""You are an expert at detecting media bias. Analyze the following text for different types of bias:
        
Categories of bias to look for:
1. Political bias - left-leaning or right-leaning rhetoric
2. Emotional bias - use of emotional language to influence opinions
3. Framing bias - presenting facts selectively to promote a particular interpretation
4. Source bias - selective use of sources or authorities
5. Factual bias - presenting opinions as facts or using cherry-picked facts
6. Omission bias - leaving out key information that would change context
