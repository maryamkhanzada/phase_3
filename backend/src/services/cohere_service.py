"""
Cohere API service for natural language processing.
Provides intent classification and entity extraction for chatbot.
"""
import json
import logging
from typing import Dict, Any

import cohere
from cohere.core.api_error import ApiError

from src.config import settings

logger = logging.getLogger(__name__)


class CohereService:
    """Service for interacting with Cohere API for NLP tasks."""

    def __init__(self):
        """Initialize Cohere client with API key from settings."""
        self.client = cohere.Client(api_key=settings.cohere_api_key)
        logger.info("CohereService initialized successfully")

    def classify_intent(self, message: str) -> str:
        """
        Classify user message into task management intents.

        Args:
            message: User's natural language message

        Returns:
            Intent string: "add", "list", "update", "complete", "delete", or "unknown"

        Raises:
            ApiError: If Cohere API call fails
        """
        try:
            response = self.client.classify(
                model='embed-english-v3.0',
                inputs=[message],
                examples=[
                    ("Add a task to buy milk", "add"),
                    ("Create a reminder for dentist appointment", "add"),
                    ("New task: call the doctor", "add"),
                    ("Show me my tasks", "list"),
                    ("What do I need to do?", "list"),
                    ("Display all tasks", "list"),
                    ("Mark task 5 as done", "complete"),
                    ("Complete buy groceries", "complete"),
                    ("Finish task 3", "complete"),
                    ("Update task 3 title to review code", "update"),
                    ("Change description of task 7", "update"),
                    ("Edit task 2", "update"),
                    ("Delete task 12", "delete"),
                    ("Remove the completed tasks", "delete"),
                    ("Get rid of task 4", "delete"),
                ]
            )

            intent = response.classifications[0].prediction
            confidence = response.classifications[0].confidence

            logger.info(
                f"Intent classified: '{intent}' (confidence: {confidence:.2f}) "
                f"for message: '{message[:50]}...'"
            )

            return intent

        except ApiError as e:
            logger.error(f"Cohere API error during intent classification: {e}")
            return "unknown"
        except Exception as e:
            logger.error(f"Unexpected error during intent classification: {e}")
            return "unknown"

    def extract_entities(self, message: str, intent: str) -> Dict[str, Any]:
        """
        Extract task entities from message based on detected intent.

        Args:
            message: User's natural language message
            intent: Previously classified intent

        Returns:
            Dictionary with extracted entities:
            - task_id: Optional[int] - task ID if mentioned
            - title: Optional[str] - task title
            - description: Optional[str] - task description
            - completed: Optional[bool] - completion status

        Raises:
            ApiError: If Cohere API call fails
        """
        prompt = f"""
Extract task information from the following user message.

Intent: {intent}
Message: "{message}"

Return ONLY a valid JSON object with these fields (use null if not mentioned):
- task_id: integer task ID if explicitly mentioned (e.g., "task 5", "task #3")
- title: string task title (what the task is about)
- description: string task description (additional details, if any)
- completed: boolean completion status (true/false, null if not applicable)

Example outputs:
{{"task_id": 5, "title": null, "description": null, "completed": true}}
{{"task_id": null, "title": "buy groceries", "description": "milk and eggs", "completed": null}}

JSON:
"""

        try:
            response = self.client.generate(
                model='command',
                prompt=prompt,
                temperature=0.1,  # Low temperature for deterministic extraction
                max_tokens=200
            )

            # Parse JSON from response
            json_text = response.generations[0].text.strip()

            # Remove markdown code blocks if present
            if json_text.startswith("```"):
                json_text = json_text.split("```")[1]
                if json_text.startswith("json"):
                    json_text = json_text[4:].strip()

            entities = json.loads(json_text)

            logger.info(
                f"Entities extracted for intent '{intent}': {entities} "
                f"from message: '{message[:50]}...'"
            )

            return entities

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Cohere response: {e}")
            return {"task_id": None, "title": None, "description": None, "completed": None}
        except ApiError as e:
            logger.error(f"Cohere API error during entity extraction: {e}")
            return {"task_id": None, "title": None, "description": None, "completed": None}
        except Exception as e:
            logger.error(f"Unexpected error during entity extraction: {e}")
            return {"task_id": None, "title": None, "description": None, "completed": None}


# Global service instance
cohere_service = CohereService()
