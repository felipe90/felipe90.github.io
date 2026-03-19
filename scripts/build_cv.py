import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CV_DIR = os.path.join(BASE_DIR, 'cv')
TEMPLATE_FILE = os.path.join(CV_DIR, 'template.html')

def strip_tags(text):
    if not text:
        return ""
    # Replace <br> and <br/> with a space
    text = re.sub(r'<br\s*/?>', ' ', text)
    # Remove other HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    # Replace multiple spaces with one
    text = re.sub(' +', ' ', text)
    return text.strip()

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def render_list(items, tag='li', class_name=None):
    html = []
    class_attr = f' class="{class_name}"' if class_name else ''
    for item in items:
        if isinstance(item, dict):
            # For languages where we have a specific class
            cls = item.get('class', '')
            val = item.get('name', '')
            html.append(f'<{tag} class="skill-tag {cls}">{val}</{tag}>'.replace('  ', ' '))
        else:
            html.append(f'<{tag}{class_attr}>{item}</{tag}>')
    return '\n                        '.join(html)

def render_jobs(jobs):
    html = []
    for job in jobs:
        bullets = render_list(job['bullets'], 'li')
        tags = render_list(job['tags'], 'li', 'exp-tag')
        
        job_html = f"""
                    <div class="exp-item">
                        <div class="exp-header">
                            <div>
                                <div class="exp-role">{job['role']}</div>
                                <div class="exp-company">{job['company']}</div>
                            </div>
                            <div class="exp-period">{job['period']}</div>
                        </div>
                        <ul class="exp-bullets">
                            {bullets}
                        </ul>
                        <ul class="exp-tags">
                            {tags}
                        </ul>
                    </div>
"""
        html.append(job_html)
    return ''.join(html)

def build_cv(lang, json_file, template_path, output_file):
    print(f"Building {output_file}...")
    data = load_json(json_file)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Always strip HTML from data fields for ATS compatibility
    data['main']['profile_text'] = strip_tags(data['main']['profile_text'])
    for job in data['main']['jobs']:
        job['role'] = strip_tags(job['role'])
        job['period'] = strip_tags(job['period'])
        job['bullets'] = [strip_tags(b) for b in job['bullets']]
    data['main']['projects'] = [strip_tags(p) for p in data['main']['projects']]
    data['sidebar']['education_school'] = strip_tags(data['sidebar']['education_school'])

    # Meta & Basic
    html = html.replace('lang="es"', f'lang="{data["lang"]}"')
    html = html.replace('{{first_name}}', data['first_name'])
    html = html.replace('{{last_name}}', data['last_name'])
    html = html.replace('{{role_title}}', data['role_title'])
    
    # Header
    html = html.replace('{{header_title}}', data['header_title'])
    html = html.replace('{{header_availability}}', data['header_availability'])
    html = html.replace('{{header_location}}', data['header_location'])
    html = html.replace('{{contact_email}}', data['contact_email'])
    html = html.replace('{{contact_linkedin}}', data['contact_linkedin'])
    html = html.replace('{{contact_github}}', data['contact_github'])
    html = html.replace('{{contact_portfolio}}', data['contact_portfolio'])
    
    # Sidebar
    sidebar = data['sidebar']
    html = html.replace('{{sidebar_title}}', sidebar['sidebar_title'])
    html = html.replace('{{languages_group_title}}', sidebar['languages_group_title'])
    html = html.replace('{{programming_languages_list}}', render_list(sidebar['programming_languages'], 'li', 'skill-tag'))
    html = html.replace('{{frameworks_title}}', sidebar['frameworks_title'])
    html = html.replace('{{frameworks_list}}', render_list(sidebar['frameworks'], 'li', 'skill-tag'))
    html = html.replace('{{ai_title}}', sidebar['ai_title'])
    html = html.replace('{{ai_list}}', render_list(sidebar['ai'], 'li', 'skill-tag accent'))
    html = html.replace('{{design_title}}', sidebar['design_title'])
    html = html.replace('{{design_list}}', render_list(sidebar['design'], 'li', 'skill-tag neutral'))
    html = html.replace('{{methodologies_title}}', sidebar['methodologies_title'])
    html = html.replace('{{methodologies_list}}', render_list(sidebar['methodologies'], 'li', 'skill-tag'))
    
    html = html.replace('{{competencies_title}}', sidebar['competencies_title'])
    html = html.replace('{{competencies_list}}', render_list(sidebar['competencies'], 'li', 'ats-tag'))
    
    html = html.replace('{{education_title}}', sidebar['education_title'])
    html = html.replace('{{education_degree}}', sidebar['education_degree'])
    html = html.replace('{{education_school}}', sidebar['education_school'])
    html = html.replace('{{education_period}}', sidebar['education_period'])
    
    html = html.replace('{{languages_title}}', sidebar['languages_title'])
    html = html.replace('{{languages_list}}', render_list(sidebar['languages'], 'li'))

    # Main
    main = data['main']
    html = html.replace('{{profile_title}}', main['profile_title'])
    html = html.replace('{{profile_text}}', main['profile_text'])

    # Metrics
    metrics_html = []
    for m in main['metrics']:
        metrics_html.append(f"""
                    <div class="metric-card">
                        <div class="metric-value">{m['value']}</div>
                        <div class="metric-label">{m['label']}</div>
                    </div>""")
    html = html.replace('{{metrics_blocks}}', ''.join(metrics_html))

    # Experience
    html = html.replace('{{experience_title}}', main['experience_title'])
    html = html.replace('{{jobs_blocks}}', render_jobs(main['jobs']))

    # Projects
    html = html.replace('{{projects_title}}', main['projects_title'])
    html = html.replace('{{projects_list}}', render_list(main['projects'], 'li'))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Successfully generated {output_file}")

if __name__ == '__main__':
    if not os.path.exists(os.path.join(BASE_DIR, 'scripts')):
        os.makedirs(os.path.join(BASE_DIR, 'scripts'))
        
    build_cv('es', os.path.join(CV_DIR, 'data_es.json'), TEMPLATE_FILE, os.path.join(CV_DIR, 'index.html'))
    build_cv('en', os.path.join(CV_DIR, 'data_en.json'), TEMPLATE_FILE, os.path.join(CV_DIR, 'index-en.html'))
    
    print("CV Build Complete!")
