import rispy
import requests
import json
import time
from typing import List, Dict, Optional

## One shot from Claude.
class RISClassifier:
    def __init__(self, llamafile_url: str = "http://localhost:8080"):
        """
        Initialize the classifier with llamafile server URL
        
        Args:
            llamafile_url: URL where your .llamafile server is running
        """
        self.llamafile_url = llamafile_url
        self.api_endpoint = f"{llamafile_url}/v1/chat/completions"
    
    def load_ris_file(self, filepath: str) -> List[Dict]:
        """Load RIS file and return entries"""
        with open(filepath, 'r', encoding='utf-8') as f:
            entries = rispy.load(f)
        return entries
    
    def create_classification_prompt(self, entry: Dict, inclusion_criteria: str) -> str:
        """
        Create a prompt for the AI to classify the entry
        
        Args:
            entry: Single RIS entry dictionary
            inclusion_criteria: Your specific inclusion criteria
        """
        # Extract key fields from the entry
        title = entry.get('title', 'No title')
        abstract = entry.get('abstract', entry.get('notes_abstract', 'No abstract available'))
        #authors = entry.get('authors', ['Unknown'])
        year = entry.get('year', 'Unknown')
        
        # Format authors if it's a list
        #if isinstance(authors, list):
        #    authors_str = ', '.join(authors)
        #else:
        #    authors_str = str(authors)
        
        prompt = f"""
Please classify this research paper based on the inclusion criteria provided.

INCLUSION CRITERIA:
{inclusion_criteria}

PAPER DETAILS:
Title: {title}
Year: {year}
Abstract: {abstract}

TASK:
Determine if this paper meets the inclusion criteria. Respond with:
1. Decision: INCLUDE or EXCLUDE
2. Reasoning: Brief explanation of your decision
3. Confidence: High/Medium/Low

Format your response as:
DECISION: [INCLUDE/EXCLUDE]
REASONING: [Your explanation]
CONFIDENCE: [High/Medium/Low]
"""
        return prompt
    
    def query_llama(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.6) -> Optional[str]:
        """
        Send prompt to local Llama model
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (lower = more consistent)
            0.6 optimal for deepseek distilled; 0.1 for others
        """
        payload = {
            "messages":[{"role":"user",
                         "content":prompt}],
            #"prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            # remove line below if using deepseek
            ##"stop": ["</s>", "\n\n"],
            "stream": False
        }
        
        # if using v1/chat/completions, prompt is a user message:
         # for straightup /completions, this isn't neceesary
        try:
            response = requests.post(self.api_endpoint, json=payload, timeout=2400)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'] 
            
        except requests.exceptions.RequestException as e:
            print(f"Error querying Llama: {e}")
            return None
    
    def parse_classification_response(self, response: str) -> Dict:
        """Parse the AI's classification response"""
        result = {
            'decision': 'UNKNOWN',
            'reasoning': 'Could not parse response',
            'confidence': 'Low'
        }
        
        if not response:
            return result
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('DECISION:'):
                decision = line.replace('DECISION:', '').strip()
                result['decision'] = decision
            elif line.startswith('REASONING:'):
                reasoning = line.replace('REASONING:', '').strip()
                result['reasoning'] = reasoning
            elif line.startswith('CONFIDENCE:'):
                confidence = line.replace('CONFIDENCE:', '').strip()
                result['confidence'] = confidence
        
        return result
    
    def save_results(self, results: List[Dict], output_file: str):
        """Save classification results to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    def classify_entries(self, entries: List[Dict], inclusion_criteria: str, 
                        delay_between_requests: float = 1.0) -> List[Dict]:
        """
        Classify all entries based on inclusion criteria
        
        Args:
            entries: List of RIS entries
            inclusion_criteria: Your inclusion criteria text
            delay_between_requests: Delay between API calls to avoid overwhelming the server
        """
        results = []
        
        for i, entry in enumerate(entries):
            print(f"Processing entry {i+1}/{len(entries)}")
            
            # Create prompt
            prompt = self.create_classification_prompt(entry, inclusion_criteria)
            
            # Query Llama
            response = self.query_llama(prompt)
            
            # Parse response
            classification = self.parse_classification_response(response)
            
            # Add to results
            result = {
                'entry_index': i,
                'title': entry.get('title', 'No title'),
                'year': entry.get('year', 'Unknown'),
                'decision': classification['decision'],
                'reasoning': classification['reasoning'],
                'confidence': classification['confidence'],
                'raw_response': response,
                'original_entry': entry
            }
            
            results.append(result)
            self.save_results(results,'results.json') 
            # Add delay to avoid overwhelming the server
            if delay_between_requests > 0:
                time.sleep(delay_between_requests)
        
        return results
    
    def get_summary(self, results: List[Dict]) -> Dict:
        """Get summary statistics of classification results"""
        total = len(results)
        included = sum(1 for r in results if r['decision'] == 'INCLUDE')
        excluded = sum(1 for r in results if r['decision'] == 'EXCLUDE')
        unknown = sum(1 for r in results if r['decision'] == 'UNKNOWN')
        
        confidence_counts = {}
        for r in results:
            conf = r['confidence']
            confidence_counts[conf] = confidence_counts.get(conf, 0) + 1
        
        return {
            'total_entries': total,
            'included': included,
            'excluded': excluded,
            'unknown': unknown,
            'confidence_distribution': confidence_counts
        }

# Example usage
if __name__ == "__main__":
    # Initialize classifier
    classifier = RISClassifier(llamafile_url="http://localhost:8080")
    
    # Define your inclusion criteria
    inclusion_criteria = """
    Studies must meet ALL of the following criteria:
    1. Published in the last 10 years (2014 or later)
    2. Focus on machine learning or artificial intelligence
    3. Include empirical results or experiments
    4. Written in English
    5. Peer-reviewed publication
    
    EXCLUDE if:
    - Review papers or meta-analyses
    - Theoretical papers without empirical validation
    - Conference abstracts without full papers
    - Non-English publications
    """
    
    # Load RIS file
    entries = classifier.load_ris_file('your_file.ris')
    print(f"Loaded {len(entries)} entries from RIS file")
    
    # Classify entries
    results = classifier.classify_entries(entries, inclusion_criteria)
    
    # Save results
    classifier.save_results(results, 'classification_results.json')
    
    # Print summary
    summary = classifier.get_summary(results)
    print("\nClassification Summary:")
    print(f"Total entries: {summary['total_entries']}")
    print(f"Included: {summary['included']}")
    print(f"Excluded: {summary['excluded']}")
    print(f"Unknown: {summary['unknown']}")
    print(f"Confidence distribution: {summary['confidence_distribution']}")
    
    # Show some examples
    print("\nFirst few results:")
    for i, result in enumerate(results[:3]):
        print(f"\n{i+1}. {result['title']}")
        print(f"   Decision: {result['decision']}")
        print(f"   Reasoning: {result['reasoning']}")
        print(f"   Confidence: {result['confidence']}")
