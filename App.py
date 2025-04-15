from flask import Flask, render_template, abort

app = Flask(__name__)

# Topic list and mapping
topics = [
    {"name": "Python", "description": "Learn Python programming from basics to advanced."},
    {"name": "Libraries", "description": "Explore libraries like Numpy, Pandas, Matplotlib, and more."},
    {"name": "Data Wrangling", "description": "Master data cleaning and preprocessing techniques."},
    {"name": "Statistics", "description": "Understand statistical concepts for data analysis."},
    {"name": "Probability", "description": "Dive into probability theory and its applications."},
    {"name": "Linear Algebra", "description": "Learn linear algebra for machine learning and data science."},
    {"name": "Calculus", "description": "Understand calculus concepts for optimization."},
    {"name": "DSA", "description": "Practice Data Structures and Algorithms."},
    {"name": "Tableau", "description": "Learn Tableau for data visualization."},
    {"name": "Power BI", "description": "Master Power BI for business intelligence."},
    {"name": "Power Query", "description": "Master Power Query for Data Cleaning."},
]

# Add slug to each topic
for topic in topics:
    topic['slug'] = topic['name'].lower().replace(" ", "-")

# Route: Home Page
@app.route('/')
def home():
    return render_template('home.html', topics=topics)

# Route: Subpages using slug
@app.route('/topic/<slug>')
def topic_page(slug):
    # Find topic by slug
    topic = next((t for t in topics if t['slug'] == slug), None)
    if topic:
        try:
            return render_template(f"{topic['name']}.html", topic_name=topic['name'])
        except:
            return render_template('404.html'), 404
    else:
        return render_template('404.html'), 404

# Route: 404 Error Page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Run app for deployment
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
