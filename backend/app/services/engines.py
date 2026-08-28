# backend/app/services/engines.py

import re


# ============================================================
# Authentication Detector
# ============================================================

class AuthDetector:
    """
    Detects common authentication mechanisms from HTTP headers.
    """

    @staticmethod
    def detect(headers):
        """
        Supports headers represented as:
        - list of {"name": "...", "value": "..."}
        - dictionary {"Authorization": "Bearer ..."}
        """

        if not headers:
            return "None"

        # ----------------------------------------------------
        # Normalize headers into iterable name/value pairs
        # ----------------------------------------------------
        if isinstance(headers, dict):
            header_items = [
                {
                    "name": str(name),
                    "value": str(value)
                }
                for name, value in headers.items()
            ]
        elif isinstance(headers, list):
            header_items = headers
        else:
            return "None"

        # ----------------------------------------------------
        # Authentication detection
        # ----------------------------------------------------
        for header in header_items:

            if not isinstance(header, dict):
                continue

            name = str(header.get("name", "")).lower()
            value = str(header.get("value", "")).lower()

            # -----------------------------------------------
            # Authorization Header
            # -----------------------------------------------
            if name == "authorization":

                if "bearer" in value:
                    return "Bearer Token"

                if "basic" in value:
                    return "Basic Auth"

                if "digest" in value:
                    return "Digest Auth"

                if value:
                    return "Authorization Header"

            # -----------------------------------------------
            # Cookie Authentication
            # -----------------------------------------------
            if name == "cookie":

                if (
                    "session" in value
                    or "sessionid" in value
                    or "session_id" in value
                    or "jwt" in value
                    or "token" in value
                ):
                    return "Session/Cookie"

            # -----------------------------------------------
            # API Key
            # -----------------------------------------------
            if (
                "api-key" in name
                or "apikey" in name
                or "x-api-key" in name
            ):
                return "API Key"

        return "None"


# ============================================================
# Rule Engine
# ============================================================

class RuleEngine:
    """
    Analyzes parsed APIs and identifies common
    performance and API design risks.
    """

    @staticmethod
    def analyze(apis):

        warnings = []

        if not apis:
            return warnings

        for api in apis:

            if not isinstance(api, dict):
                continue

            endpoint = (
                api.get("endpoint")
                or api.get("url")
                or "Unknown Endpoint"
            )

            # =================================================
            # Slow Response Detection
            # =================================================

            response_time = api.get("response_time")

            try:
                response_time = float(response_time)
            except (TypeError, ValueError):
                response_time = None

            if response_time is not None:

                if response_time > 5000:

                    warnings.append({
                        "level": "Critical",
                        "message": (
                            f"Very slow response time "
                            f"({response_time}ms) for {endpoint}"
                        ),
                        "endpoint": endpoint,
                        "response_time": response_time
                    })

                elif response_time > 2000:

                    warnings.append({
                        "level": "Warning",
                        "message": (
                            f"Slow response time "
                            f"({response_time}ms) for {endpoint}"
                        ),
                        "endpoint": endpoint,
                        "response_time": response_time
                    })

            # =================================================
            # Large Request Payload
            # =================================================

            post_data = api.get("post_data", "")

            if post_data is None:
                post_data = ""

            if isinstance(post_data, (dict, list)):
                post_data = str(post_data)

            if len(str(post_data)) > 50000:

                warnings.append({
                    "level": "Critical",
                    "message": (
                        f"Large request payload detected "
                        f"on {endpoint}"
                    ),
                    "endpoint": endpoint,
                    "payload_size": len(str(post_data))
                })

            # =================================================
            # Large Response Payload
            # =================================================

            response_body = api.get("response_body", "")

            if response_body is None:
                response_body = ""

            if isinstance(response_body, (dict, list)):
                response_body = str(response_body)

            response_size = len(str(response_body))

            if response_size > 1_000_000:

                warnings.append({
                    "level": "Warning",
                    "message": (
                        f"Large response payload detected "
                        f"on {endpoint}"
                    ),
                    "endpoint": endpoint,
                    "response_size": response_size
                })

            # =================================================
            # Missing Authentication
            # =================================================

            auth_detected = api.get("auth_detected")

            if auth_detected == "None":

                method = str(
                    api.get("method", "GET")
                ).upper()

                # Focus primarily on state-changing APIs
                if method in ["POST", "PUT", "PATCH", "DELETE"]:

                    warnings.append({
                        "level": "Info",
                        "message": (
                            f"No authentication mechanism detected "
                            f"for {method} {endpoint}"
                        ),
                        "endpoint": endpoint
                    })

        return warnings


# ============================================================
# Correlation Engine
# ============================================================

class CorrelationEngine:
    """
    Scans API response bodies for dynamic values and
    attaches correlation candidates to the API dictionary.

    The generated correlation information can later be
    consumed by the JMX generator.
    """

    @staticmethod
    def detect(apis):

        if not apis:
            return apis

        for api in apis:

            if not isinstance(api, dict):
                continue

            # Always initialize correlations
            api["correlations"] = []

            response_body = str(
                api.get("response_body", "")
            )

            # Case-insensitive analysis
            response_body_lower = response_body.lower()

            # ------------------------------------------------
            # Skip empty responses
            # ------------------------------------------------

            if not response_body_lower.strip():
                continue

            # =================================================
            # TOKEN DETECTION
            # =================================================

            token_detected = (
                "token" in response_body_lower
                or "jwt" in response_body_lower
                or "access_token" in response_body_lower
                or "access-token" in response_body_lower
                or "refresh_token" in response_body_lower
                or "refresh-token" in response_body_lower
                or "authorization" in response_body_lower
                or "auth" in response_body_lower
            )

            if token_detected:

                api["correlations"].append({
                    "reference_name": "c_token",
                    "json_path": "$..token",
                    "match_number": "1",
                    "default_value": "TOKEN_NOT_FOUND"
                })

            # =================================================
            # SESSION / ID DETECTION
            # =================================================

            session_detected = (
                "session" in response_body_lower
                or "sessionid" in response_body_lower
                or "session_id" in response_body_lower
                or "uuid" in response_body_lower
                or "userid" in response_body_lower
                or "user_id" in response_body_lower
            )

            if session_detected:

                api["correlations"].append({
                    "reference_name": "c_sessionId",
                    "json_path": "$..id",
                    "match_number": "1",
                    "default_value": "SESSION_NOT_FOUND"
                })

            # =================================================
            # ORDER ID DETECTION
            # =================================================

            if (
                "orderid" in response_body_lower
                or "order_id" in response_body_lower
                or "order" in response_body_lower
            ):

                api["correlations"].append({
                    "reference_name": "c_orderId",
                    "json_path": "$..orderId",
                    "match_number": "1",
                    "default_value": "ORDER_NOT_FOUND"
                })

            # =================================================
            # PRODUCT ID DETECTION
            # =================================================

            if (
                "productid" in response_body_lower
                or "product_id" in response_body_lower
            ):

                api["correlations"].append({
                    "reference_name": "c_productId",
                    "json_path": "$..productId",
                    "match_number": "1",
                    "default_value": "PRODUCT_NOT_FOUND"
                })

            # =================================================
            # CUSTOMER ID DETECTION
            # =================================================

            if (
                "customerid" in response_body_lower
                or "customer_id" in response_body_lower
            ):

                api["correlations"].append({
                    "reference_name": "c_customerId",
                    "json_path": "$..customerId",
                    "match_number": "1",
                    "default_value": "CUSTOMER_NOT_FOUND"
                })

            # =================================================
            # REQUEST ID DETECTION
            # =================================================

            if (
                "requestid" in response_body_lower
                or "request_id" in response_body_lower
                or "correlationid" in response_body_lower
                or "correlation_id" in response_body_lower
            ):

                api["correlations"].append({
                    "reference_name": "c_requestId",
                    "json_path": "$..requestId",
                    "match_number": "1",
                    "default_value": "REQUEST_NOT_FOUND"
                })

            # =================================================
            # Generic ID Detection
            # =================================================

            # Only add generic ID if no session correlation
            # has already been detected.
            if (
                "id" in response_body_lower
                and not any(
                    c.get("reference_name") == "c_sessionId"
                    for c in api["correlations"]
                )
            ):

                api["correlations"].append({
                    "reference_name": "c_id",
                    "json_path": "$..id",
                    "match_number": "1",
                    "default_value": "ID_NOT_FOUND"
                })

        return apis