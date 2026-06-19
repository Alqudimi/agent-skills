import json
import sys

def evaluate_skill_relevance(task_description, skill_metadata):
    """
    Evaluates the strategic relevance of a skill based on task depth and complexity.
    """
    score = 0
    # Logic for deep evaluation
    keywords = skill_metadata.get('keywords', [])
    for word in keywords:
        if word.lower() in task_description.lower():
            score += 25
            
    # Complexity bonus
    if len(task_description.split()) > 20:
        score += 10
        
    return min(score, 100)

if __name__ == "__main__":
    # Example usage for the agent
    sample_task = "Deploy a high-availability Nginx cluster with automated SSL renewal"
    sample_skills = [
        {"name": "nginx-master", "keywords": ["nginx", "ssl", "cluster", "proxy"]},
        {"name": "basic-web-server", "keywords": ["html", "css", "server"]}
    ]
    
    results = []
    for s in sample_skills:
        relevance = evaluate_skill_relevance(sample_task, s)
        results.append({"skill": s['name'], "relevance_score": relevance})
    
    print(json.dumps(results, indent=2))
