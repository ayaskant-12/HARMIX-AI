import json
import requests

from typing import List, Dict, Any, Optional


class OllamaClient:
    """
    HARMIX AI - Ollama Client

    Supports:
    - HAR Executive Analysis
    - Interactive HAR Chat
    - Generic Prompt Generation
    - Ollama Health Check
    - Model Information
    """

    def __init__(
        self,
        model: str = "tinyllama",
        base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    # ============================================================
    # Health Check
    # ============================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Check whether Ollama is running and available.
        """

        try:

            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )

            if response.status_code == 200:

                return {
                    "status": True,
                    "models": response.json().get("models", [])
                }

            return {
                "status": False,
                "error": f"HTTP {response.status_code}"
            }

        except requests.exceptions.RequestException as e:

            return {
                "status": False,
                "error": str(e)
            }

    # ============================================================
    # Generic Prompt Generator
    # ============================================================

    def generate(self, prompt: str) -> str:
        """
        Send a normal prompt to Ollama /api/generate.
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=300
            )

            response.raise_for_status()

            data = response.json()

            return data.get(
                "response",
                ""
            ).strip()

        except requests.exceptions.Timeout:

            return "Ollama request timed out."

        except requests.exceptions.ConnectionError:

            return (
                "Unable to connect to Ollama. "
                "Make sure Ollama is running on "
                f"{self.base_url}."
            )

        except requests.exceptions.RequestException as e:

            return f"Ollama request failed: {str(e)}"

        except Exception as e:

            return f"Unexpected AI error: {str(e)}"

    # ============================================================
    # HAR Executive Analysis
    # ============================================================

    def analyze_har(
        self,
        summary_data: Dict[str, Any]
    ) -> str:
        """
        Generate executive-level performance analysis
        from parsed HAR data.
        """

        try:

            har_json = json.dumps(
                summary_data,
                indent=2
            )

        except Exception:

            har_json = str(summary_data)

        # Limit prompt size
        har_json = har_json[:8000]

        prompt = f"""
You are HARMIX AI.

You are an elite:

- Performance Engineer
- Apache JMeter Architect
- API Performance Specialist
- Load Testing Expert

You are analyzing a parsed HAR file.

IMPORTANT:
Only use the information contained in the HAR JSON.

Do not invent API endpoints,
response times,
authentication mechanisms,
correlation values,
or performance metrics.

Analyze the following HAR data.

HAR DATA:
{har_json}

Provide the following sections:

1. Executive Summary

2. Application Architecture Overview

3. API Inventory Overview

4. Authentication Analysis

5. Correlation Candidates

6. Dynamic Parameters

7. Performance Risks

8. Bottlenecks

9. API Design Observations

10. Scalability Concerns

11. Recommended Assertions

12. Recommended Timers

13. Recommended Controllers

14. Recommended Parameterization

15. JMeter Test Strategy

16. JMeter Best Practices

17. Final Recommendations

For every observation, rely only on the supplied HAR data.

If information is unavailable, explicitly state:

"Insufficient data in the HAR."

Keep the response technical, precise and useful
for a Performance Engineer.
"""

        return self.generate(prompt)

    # ============================================================
    # Interactive AI Chat
    # ============================================================

    def chat(
        self,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Interactive AI assistant for the uploaded HAR.

        The AI is strictly restricted to the supplied
        HAR context.
        """

        history = history or []
        context_data = context_data or {}

        # --------------------------------------------------------
        # Prepare HAR context
        # --------------------------------------------------------

        try:

            context_json = json.dumps(
                context_data,
                indent=2
            )

        except Exception:

            context_json = str(context_data)

        # Keep prompt within reasonable size
        context_json = context_json[:6000]

        # --------------------------------------------------------
        # Strict System Prompt
        # --------------------------------------------------------

        system_prompt = f"""
You are HARMIX AI, an elite Performance Engineering assistant.

You are currently helping a user analyze a parsed HAR file.

Here is the extracted API inventory and rule engine warnings:

{context_json}

CRITICAL RULES:

1. ONLY use the data provided in the JSON above.

2. DO NOT invent APIs, endpoints, HTTP methods,
   authentication mechanisms, response times,
   correlation values, headers, parameters,
   status codes, or performance metrics.

3. DO NOT suggest external tools, bash scripts,
   curl commands, shell commands, or third-party
   platforms such as OctoPerf, Postman, JMeter plugins,
   or other external services.

4. If the user asks for response times,
   read them directly from the provided JSON.

5. If response-time information does not exist
   in the JSON, say:
   "Response-time data is not available in the supplied HAR context."

6. If the user asks about an API that does not exist
   in the supplied JSON, say:
   "That API is not present in the supplied HAR context."

7. If the user asks about authentication,
   use only authentication information available
   in the supplied JSON.

8. If the user asks about correlation,
   use only detected correlation candidates
   available in the supplied JSON.

9. If the user asks for JMeter recommendations,
   recommendations must be based on the API information
   and findings contained in the supplied JSON.

10. Do not assume a performance bottleneck unless
    the supplied HAR data supports it.

11. Do not create numerical metrics that are not present
    in the supplied JSON.

12. If the requested information is missing,
    clearly say that the information is unavailable.

13. Be technical, precise, concise and factual.

14. Prioritize the supplied HAR data over general assumptions.

15. Never hallucinate information.
"""

        # --------------------------------------------------------
        # Build conversation
        # --------------------------------------------------------

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        # --------------------------------------------------------
        # Add conversation history
        # --------------------------------------------------------

        for msg in history:

            if not isinstance(msg, dict):
                continue

            role = msg.get("role")
            content = msg.get("content")

            if role not in [
                "user",
                "assistant"
            ]:
                continue

            if not content:
                continue

            messages.append(
                {
                    "role": role,
                    "content": str(content)
                }
            )

        # --------------------------------------------------------
        # Add current user message
        # --------------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        # --------------------------------------------------------
        # Ollama Request
        # --------------------------------------------------------

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=300
            )

            response.raise_for_status()

            data = response.json()

            message = data.get(
                "message",
                {}
            )

            content = message.get(
                "content",
                ""
            )

            if content:

                return content.strip()

            return "No response generated by HARMIX AI."

        except requests.exceptions.Timeout:

            return (
                "HARMIX AI request timed out. "
                "Ollama may be taking too long to process the request."
            )

        except requests.exceptions.ConnectionError:

            return (
                "Unable to connect to Ollama. "
                "Please make sure Ollama is running on "
                f"{self.base_url}."
            )

        except requests.exceptions.RequestException as e:

            return (
                f"Ollama chat request failed: {str(e)}"
            )

        except Exception as e:

            return (
                f"Unexpected HARMIX AI error: {str(e)}"
            )

    # ============================================================
    # Get Available Ollama Models
    # ============================================================

    def get_models(self) -> Dict[str, Any]:
        """
        Return all models installed in Ollama.
        """

        try:

            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=30
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:

            return {
                "error": str(e)
            }

        except Exception as e:

            return {
                "error": str(e)
            }

    # ============================================================
    # Check Whether Configured Model Exists
    # ============================================================

    def model_available(self) -> bool:
        """
        Check whether the configured Ollama model exists.
        """

        try:

            data = self.get_models()

            models = data.get(
                "models",
                []
            )

            for model in models:

                model_name = model.get(
                    "name",
                    ""
                )

                if (
                    model_name == self.model
                    or model_name.startswith(
                        self.model + ":"
                    )
                ):
                    return True

            return False

        except Exception:

            return False