"""
AI Quiz Generation Service using GitHub Models API.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional


class QuizGeneratorService:
    """Service for generating quizzes using GitHub Models API."""

    API_URL = "https://models.inference.ai.azure.com/chat/completions"
    MODEL = "gpt-4o-mini"
    
    # Programming and tech-related keywords for topic validation
    ALLOWED_KEYWORDS = [
        # Programming Languages
        'python', 'javascript', 'java', 'c++', 'c#', 'csharp', 'ruby', 'php',
        'swift', 'kotlin', 'go', 'golang', 'rust', 'typescript', 'scala',
        'perl', 'r ', 'matlab', 'lua', 'dart', 'elixir', 'haskell', 'clojure',
        
        # Web Development
        'html', 'css', 'sass', 'scss', 'less', 'bootstrap', 'tailwind',
        'react', 'angular', 'vue', 'svelte', 'next.js', 'nextjs', 'nuxt',
        'node', 'express', 'django', 'flask', 'fastapi', 'rails', 'laravel',
        'asp.net', 'spring', 'frontend', 'backend', 'fullstack', 'full-stack',
        'web development', 'web design', 'responsive', 'ajax', 'fetch', 'api',
        'rest', 'graphql', 'websocket', 'http', 'dom', 'browser',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'sqlite',
        'oracle', 'database', 'nosql', 'query', 'queries', 'orm', 'schema',
        'normalization', 'index', 'join', 'crud',
        
        # DevOps & Tools
        'git', 'github', 'gitlab', 'bitbucket', 'docker', 'kubernetes', 'k8s',
        'aws', 'azure', 'gcp', 'cloud', 'linux', 'unix', 'bash', 'shell',
        'ci/cd', 'jenkins', 'devops', 'deployment', 'server', 'nginx', 'apache',
        'terminal', 'command line', 'cli', 'ssh', 'heroku', 'vercel', 'netlify',
        
        # Programming Concepts
        'algorithm', 'data structure', 'array', 'list', 'dictionary', 'hash',
        'tree', 'graph', 'stack', 'queue', 'heap', 'linked list', 'binary',
        'sorting', 'searching', 'recursion', 'iteration', 'loop', 'function',
        'class', 'object', 'oop', 'object-oriented', 'inheritance', 'polymorphism',
        'encapsulation', 'abstraction', 'interface', 'design pattern', 'solid',
        'dry', 'kiss', 'clean code', 'refactoring', 'debugging', 'testing',
        'unit test', 'tdd', 'bdd', 'agile', 'scrum',
        
        # Data & AI
        'machine learning', 'ml', 'artificial intelligence', 'ai', 'deep learning',
        'neural network', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scipy',
        'data science', 'data analysis', 'big data', 'data engineering',
        'statistics', 'visualization', 'matplotlib', 'jupyter', 'notebook',
        
        # Security & Networking
        'security', 'cybersecurity', 'encryption', 'authentication', 'oauth',
        'jwt', 'csrf', 'xss', 'sql injection', 'hashing', 'ssl', 'tls',
        'networking', 'tcp', 'ip', 'dns', 'firewall', 'vpn', 'protocol',
        
        # Mobile Development
        'android', 'ios', 'mobile', 'react native', 'flutter', 'xamarin',
        'app development', 'mobile app',
        
        # General Tech
        'programming', 'coding', 'software', 'developer', 'development',
        'computer science', 'cs', 'tech', 'technology', 'it', 'information technology',
        'framework', 'library', 'package', 'module', 'dependency', 'npm', 'pip',
        'version control', 'ide', 'editor', 'vscode', 'visual studio',
        'variable', 'constant', 'string', 'integer', 'float', 'boolean',
        'conditional', 'if statement', 'switch', 'exception', 'error handling',
        'async', 'await', 'promise', 'callback', 'closure', 'scope',
        'memory', 'pointer', 'reference', 'garbage collection', 'compiler',
        'interpreter', 'runtime', 'syntax', 'semantics', 'paradigm',
    ]

    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable not set")

    def is_valid_topic(self, topic: str) -> bool:
        """
        Check if the topic is related to programming/technology.
        
        Args:
            topic: The topic to validate
            
        Returns:
            True if topic is programming-related, False otherwise
        """
        topic_lower = topic.lower()
        
        # Check if any allowed keyword is in the topic
        for keyword in self.ALLOWED_KEYWORDS:
            if keyword in topic_lower:
                return True
        
        return False

    def generate_quiz(
        self, topic: str, num_questions: int = 5, difficulty: str = "medium"
    ) -> Optional[dict]:
        """
        Generate a quiz on the given topic.

        Args:
            topic: The programming topic for the quiz
            num_questions: Number of questions (default 5)
            difficulty: easy, medium, or hard

        Returns:
            Dictionary with quiz data or None if generation fails
            
        Raises:
            ValueError: If topic is not programming-related
        """
        # Validate topic is programming-related
        if not self.is_valid_topic(topic):
            raise ValueError(
                "Please enter a programming or technology-related topic. "
                "Examples: Python loops, JavaScript arrays, SQL queries, Git commands..."
            )
        
        prompt = self._build_prompt(topic, num_questions, difficulty)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a programming and technology quiz generator. "
                        "You ONLY generate quizzes about programming, software development, "
                        "computer science, and technology topics. "
                        "If asked about non-tech topics (cooking, sports, entertainment, etc.), "
                        "refuse and return an error. "
                        "Generate quiz questions in valid JSON format only. "
                        "No markdown, no code blocks, just pure JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
        }

        try:
            req = urllib.request.Request(
                self.API_URL,
                data=json.dumps(data).encode(),
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                content = result["choices"][0]["message"]["content"]
                return self._parse_response(content)
        except urllib.error.HTTPError as e:
            print(f"API Error: {e.code} - {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"Connection Error: {e.reason}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return None

    def _build_prompt(
        self, topic: str, num_questions: int, difficulty: str
    ) -> str:
        """Build the prompt for quiz generation."""
        return f"""Generate a {difficulty} difficulty programming quiz about: {topic}

Create exactly {num_questions} multiple choice questions. Each question must have exactly 4 options (A, B, C, D) with only one correct answer.

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{{
    "title": "Quiz title here",
    "description": "Brief description of the quiz",
    "questions": [
        {{
            "text": "Question text here?",
            "option_a": "First option",
            "option_b": "Second option",
            "option_c": "Third option",
            "option_d": "Fourth option",
            "correct_answer": "A",
            "explanation": "Brief explanation of why this is correct"
        }}
    ]
}}

Requirements:
- Questions should test practical programming knowledge
- Options should be plausible (avoid obviously wrong answers)
- Include code snippets in questions when appropriate
- Explanations should be educational and concise
- Difficulty: {difficulty} (easy=beginner concepts, medium=intermediate, hard=advanced)"""

    def _parse_response(self, content: str) -> Optional[dict]:
        """Parse the AI response and extract quiz data."""
        # Clean up the response - remove markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            quiz_data = json.loads(content)

            # Validate structure
            if "title" not in quiz_data or "questions" not in quiz_data:
                print("Invalid quiz structure: missing title or questions")
                return None

            if not isinstance(quiz_data["questions"], list):
                print("Invalid quiz structure: questions is not a list")
                return None

            # Validate each question
            for i, q in enumerate(quiz_data["questions"]):
                required_fields = [
                    "text",
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_answer",
                ]
                for field in required_fields:
                    if field not in q:
                        print(f"Question {i + 1} missing field: {field}")
                        return None

                # Normalize correct_answer to uppercase
                q["correct_answer"] = q["correct_answer"].upper()
                if q["correct_answer"] not in ["A", "B", "C", "D"]:
                    print(f"Question {i + 1} has invalid correct_answer")
                    return None

            return quiz_data

        except json.JSONDecodeError as e:
            print(f"Failed to parse quiz JSON: {e}")
            return None
