import xml.etree.ElementTree as ET
from urllib.parse import urlparse


class JMXGenerator:
    """
    HARMIX AI JMX Generator

    Converts parsed HAR API information into
    a JMeter-compatible .jmx test plan.

    Features:
    - Test Plan generation
    - User Defined Variables
    - Thread Group
    - Loop Controller
    - Transaction Controllers
    - HTTP Request Samplers
    - Query string support
    - HTTP headers
    - JSON correlation extractors
    - Proper HashTree structure
    - XML pretty printing
    """

    @staticmethod
    def generate(apis, output_path):

        # ============================================================
        # ROOT JMETER TEST PLAN
        # ============================================================

        root = ET.Element(
            "jmeterTestPlan",
            version="1.2",
            properties="5.0",
            jmeter="5.5"
        )

        hash_tree = ET.SubElement(
            root,
            "hashTree"
        )

        # ============================================================
        # TEST PLAN
        # ============================================================

        test_plan = ET.SubElement(
            hash_tree,
            "TestPlan",
            guiclass="TestPlanGui",
            testclass="TestPlan",
            testname="HARMIX Generated Plan"
        )

        # ============================================================
        # TEST PLAN USER DEFINED VARIABLES
        # ============================================================

        args_tp = ET.SubElement(
            test_plan,
            "elementProp",
            name="TestPlan.user_defined_variables",
            elementType="Arguments",
            guiclass="ArgumentsPanel",
            testclass="Arguments",
            testname="User Defined Variables"
        )

        ET.SubElement(
            args_tp,
            "collectionProp",
            name="Arguments.arguments"
        )

        # ============================================================
        # TEST PLAN HASH TREE
        # ============================================================

        plan_hash_tree = ET.SubElement(
            hash_tree,
            "hashTree"
        )

        # ============================================================
        # THREAD GROUP
        # ============================================================

        tg = ET.SubElement(
            plan_hash_tree,
            "ThreadGroup",
            guiclass="ThreadGroupGui",
            testclass="ThreadGroup",
            testname="Virtual Users"
        )

        # ============================================================
        # LOOP CONTROLLER
        # ============================================================

        loop_ctrl = ET.SubElement(
            tg,
            "elementProp",
            name="ThreadGroup.main_controller",
            elementType="LoopController",
            guiclass="LoopControlPanel",
            testclass="LoopController",
            testname="Loop Controller"
        )

        ET.SubElement(
            loop_ctrl,
            "boolProp",
            name="LoopController.continue_forever"
        ).text = "false"

        ET.SubElement(
            loop_ctrl,
            "stringProp",
            name="LoopController.loops"
        ).text = "1"

        # ============================================================
        # THREAD GROUP CONFIGURATION
        # ============================================================

        ET.SubElement(
            tg,
            "stringProp",
            name="ThreadGroup.num_threads"
        ).text = "1"

        ET.SubElement(
            tg,
            "stringProp",
            name="ThreadGroup.ramp_time"
        ).text = "1"

        ET.SubElement(
            tg,
            "boolProp",
            name="ThreadGroup.scheduler"
        ).text = "false"

        ET.SubElement(
            tg,
            "stringProp",
            name="ThreadGroup.duration"
        ).text = ""

        ET.SubElement(
            tg,
            "stringProp",
            name="ThreadGroup.delay"
        ).text = ""

        # ============================================================
        # THREAD GROUP HASH TREE
        # ============================================================

        tg_hash_tree = ET.SubElement(
            plan_hash_tree,
            "hashTree"
        )

        # ============================================================
        # GENERATE API TRANSACTIONS
        # ============================================================

        for index, api in enumerate(apis):

            # --------------------------------------------------------
            # Validate API
            # --------------------------------------------------------

            if not isinstance(api, dict):
                continue

            url = api.get("url", "")

            if not url:
                continue

            parsed = urlparse(url)

            endpoint = (
                api.get("endpoint")
                or parsed.path
                or url
            )

            method = (
                api.get("method")
                or "GET"
            ).upper()

            # ========================================================
            # TRANSACTION CONTROLLER
            # ========================================================

            transaction_name = f"TX - {endpoint}"

            transaction_controller = ET.SubElement(
                tg_hash_tree,
                "TransactionController",
                guiclass="TransactionControllerGui",
                testclass="TransactionController",
                testname=transaction_name
            )

            # Include child sampler timing in transaction
            ET.SubElement(
                transaction_controller,
                "boolProp",
                name="TransactionController.parent"
            ).text = "true"

            ET.SubElement(
                transaction_controller,
                "boolProp",
                name="TransactionController.includeTimers"
            ).text = "false"

            # ========================================================
            # TRANSACTION CONTROLLER HASH TREE
            # ========================================================

            tc_hash_tree = ET.SubElement(
                tg_hash_tree,
                "hashTree"
            )

            # ========================================================
            # HTTP REQUEST SAMPLER
            # ========================================================

            sampler = ET.SubElement(
                tc_hash_tree,
                "HTTPSamplerProxy",
                guiclass="HttpTestSampleGui",
                testclass="HTTPSamplerProxy",
                testname=endpoint
            )

            # ========================================================
            # HTTP ARGUMENTS
            # ========================================================

            args_http = ET.SubElement(
                sampler,
                "elementProp",
                name="HTTPsampler.Arguments",
                elementType="Arguments",
                guiclass="HTTPArgumentsPanel",
                testclass="Arguments",
                testname="User Defined Variables"
            )

            ET.SubElement(
                args_http,
                "collectionProp",
                name="Arguments.arguments"
            )

            # ========================================================
            # DOMAIN
            # ========================================================

            ET.SubElement(
                sampler,
                "stringProp",
                name="HTTPSampler.domain"
            ).text = parsed.hostname or ""

            # ========================================================
            # PORT
            # ========================================================

            try:
                port = parsed.port
            except ValueError:
                port = None

            if port:
                port_value = str(port)
            elif parsed.scheme.lower() == "https":
                port_value = "443"
            else:
                port_value = "80"

            ET.SubElement(
                sampler,
                "stringProp",
                name="HTTPSampler.port"
            ).text = port_value

            # ========================================================
            # PROTOCOL
            # ========================================================

            ET.SubElement(
                sampler,
                "stringProp",
                name="HTTPSampler.protocol"
            ).text = parsed.scheme or "http"

            # ========================================================
            # PATH
            # ========================================================

            path = parsed.path or "/"

            # Keep query parameters in the request path.
            if parsed.query:
                path = f"{path}?{parsed.query}"

            ET.SubElement(
                sampler,
                "stringProp",
                name="HTTPSampler.path"
            ).text = path

            # ========================================================
            # HTTP METHOD
            # ========================================================

            ET.SubElement(
                sampler,
                "stringProp",
                name="HTTPSampler.method"
            ).text = method

            # ========================================================
            # FOLLOW REDIRECTS
            # ========================================================

            ET.SubElement(
                sampler,
                "boolProp",
                name="HTTPSampler.follow_redirects"
            ).text = "true"

            # ========================================================
            # AUTO REDIRECTS
            # ========================================================

            ET.SubElement(
                sampler,
                "boolProp",
                name="HTTPSampler.auto_redirects"
            ).text = "false"

            # ========================================================
            # KEEP ALIVE
            # ========================================================

            ET.SubElement(
                sampler,
                "boolProp",
                name="HTTPSampler.use_keepalive"
            ).text = "true"

            # ========================================================
            # MULTIPART
            # ========================================================

            ET.SubElement(
                sampler,
                "boolProp",
                name="HTTPSampler.DO_MULTIPART_POST"
            ).text = "false"

            # ========================================================
            # BROWSER COMPATIBLE MULTIPART
            # ========================================================

            ET.SubElement(
                sampler,
                "boolProp",
                name="HTTPSampler.BROWSER_COMPATIBLE_MULTIPART_MODE"
            ).text = "false"

            # ========================================================
            # SAMPLER HASH TREE
            # ========================================================

            sampler_hash_tree = ET.SubElement(
                tc_hash_tree,
                "hashTree"
            )

            # ========================================================
            # JSON CORRELATION EXTRACTORS
            # ========================================================

            correlations = api.get(
                "correlations",
                []
            )

            if not isinstance(
                correlations,
                list
            ):
                correlations = []

            for corr in correlations:

                if not isinstance(
                    corr,
                    dict
                ):
                    continue

                reference_name = (
                    corr.get("reference_name")
                    or corr.get("referenceName")
                )

                json_path = (
                    corr.get("json_path")
                    or corr.get("jsonPath")
                )

                if not reference_name or not json_path:
                    continue

                # ----------------------------------------------------
                # JSON POST PROCESSOR
                # ----------------------------------------------------

                extractor = ET.SubElement(
                    sampler_hash_tree,
                    "JSONPostProcessor",
                    guiclass="JSONPostProcessorGui",
                    testclass="JSONPostProcessor",
                    testname=(
                        f"JSON Extractor - "
                        f"{reference_name}"
                    )
                )

                # ----------------------------------------------------
                # Reference Name
                # ----------------------------------------------------

                ET.SubElement(
                    extractor,
                    "stringProp",
                    name="JSONPostProcessor.referenceNames"
                ).text = str(
                    reference_name
                )

                # ----------------------------------------------------
                # JSON Path
                # ----------------------------------------------------

                ET.SubElement(
                    extractor,
                    "stringProp",
                    name="JSONPostProcessor.jsonPathExprs"
                ).text = str(
                    json_path
                )

                # ----------------------------------------------------
                # Match Number
                # ----------------------------------------------------

                ET.SubElement(
                    extractor,
                    "stringProp",
                    name="JSONPostProcessor.match_numbers"
                ).text = str(
                    corr.get(
                        "match_number",
                        "1"
                    )
                )

                # ----------------------------------------------------
                # Default Value
                # ----------------------------------------------------

                ET.SubElement(
                    extractor,
                    "stringProp",
                    name="JSONPostProcessor.defaultValues"
                ).text = str(
                    corr.get(
                        "default_value",
                        "NOT_FOUND"
                    )
                )

                # Every JMeter element requires HashTree
                ET.SubElement(
                    sampler_hash_tree,
                    "hashTree"
                )

            # ========================================================
            # HTTP HEADERS
            # ========================================================

            headers = api.get(
                "headers",
                {}
            )

            if isinstance(
                headers,
                dict
            ) and headers:

                header_manager = ET.SubElement(
                    sampler_hash_tree,
                    "HeaderManager",
                    guiclass="HeaderPanel",
                    testclass="HeaderManager",
                    testname="HTTP Headers"
                )

                header_collection = ET.SubElement(
                    header_manager,
                    "collectionProp",
                    name="HeaderManager.headers"
                )

                for header_name, header_value in headers.items():

                    if not header_name:
                        continue

                    # Ignore HTTP/2 pseudo headers.
                    if str(header_name).startswith(":"):
                        continue

                    header_element = ET.SubElement(
                        header_collection,
                        "elementProp",
                        name="",
                        elementType="Header"
                    )

                    ET.SubElement(
                        header_element,
                        "stringProp",
                        name="Header.name"
                    ).text = str(
                        header_name
                    )

                    ET.SubElement(
                        header_element,
                        "stringProp",
                        name="Header.value"
                    ).text = str(
                        header_value
                    )

                # Header Manager HashTree
                ET.SubElement(
                    sampler_hash_tree,
                    "hashTree"
                )

        # ============================================================
        # XML FORMATTING
        # ============================================================

        tree = ET.ElementTree(root)

        try:
            ET.indent(
                tree,
                space="  ",
                level=0
            )
        except AttributeError:
            pass

        # ============================================================
        # WRITE JMX
        # ============================================================

        tree.write(
            output_path,
            encoding="utf-8",
            xml_declaration=True
        )

        return output_path