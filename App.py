from flask import Flask, render_template

app = Flask(__name__)

# Home Page Route
@app.route('/')
def home():
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
    for topic in topics:
        topic['slug'] = topic['name'].lower().replace(" ", "-")

    return render_template('home.html', topics=topics)

# Subpage Route
@app.route('/topic/<name>')
def topic_page(name):
    try:
        return render_template(f'{name}.html', topic_name=name)
    except:
        return render_template('404.html'), 404


#changed this code    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
